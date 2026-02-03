<script lang="ts">
	/**
	 * MatrixPanel - Embeddable 5x5 transformation matrix
	 *
	 * ARCHITECTURE:
	 * - Shows document tabs at top (each with its own matrix)
	 * - Each cell displays a 5-segment bar (no numbers)
	 * - Cell value = average of 5 dimensions (bidirectional sync)
	 * - Dimensions use 3 steps: 0, 50, 100 (visual bars, no labels)
	 */

	import { createEventDispatcher } from 'svelte';
	import { Button } from '$lib/components/ui';
	import { matrix, documents, activeDocumentId, activeDocument } from '$lib/stores';
	import type { CellData, CellDimension } from '$lib/stores';

	export let matrixData: CellData[][] = [];
	export let rowHeaders: string[] = ['Dimension 1', 'Dimension 2', 'Dimension 3', 'Dimension 4', 'Dimension 5'];
	export let columnHeaders: string[] = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5'];
	export let showRiskHeatmap = false;
	export let compact = false;
	export let showDocumentTabs = true;

	const dispatch = createEventDispatcher<{
		cellClick: { row: number; col: number };
		cellChange: { row: number; col: number; value: number };
		dimensionChange: { row: number; col: number; dimIndex: number; value: number };
		documentChange: { documentId: string };
	}>();

	// Dimension steps: 0, 50, 100
	const DIM_STEPS = [0, 50, 100];

	// Cell bar has 5 segments, each representing 20% range
	const CELL_SEGMENTS = 5;

	let selectedCell: { row: number; col: number } | null = null;
	let showCellPopup = false;

	// Calculate cell value from dimensions (average)
	function calcCellValueFromDimensions(dimensions: CellDimension[]): number {
		if (!dimensions || dimensions.length === 0) return 50;
		const sum = dimensions.reduce((acc, d) => acc + d.value, 0);
		return Math.round(sum / dimensions.length);
	}

	// Get number of filled segments (0-5) from cell value (0-100)
	function getFilledSegments(value: number): number {
		if (value <= 10) return 0;
		if (value <= 30) return 1;
		if (value <= 50) return 2;
		if (value <= 70) return 3;
		if (value <= 90) return 4;
		return 5;
	}

	// Snap to nearest dimension step (0, 50, 100)
	function snapToStep(value: number): number {
		if (value < 25) return 0;
		if (value < 75) return 50;
		return 100;
	}

	// When user clicks a cell bar segment, scale all dimensions proportionally
	function handleCellBarClick(row: number, col: number, segmentIndex: number) {
		// Target average based on segment clicked (0-4 maps to 10, 30, 50, 70, 90)
		const targetAvg = (segmentIndex + 1) * 20 - 10; // 10, 30, 50, 70, 90

		const cell = matrixData[row]?.[col];
		if (!cell?.dimensions) return;

		const currentAvg = calcCellValueFromDimensions(cell.dimensions);

		if (currentAvg === 0) {
			// All dimensions are 0, set all to target
			const targetStep = snapToStep(targetAvg);
			cell.dimensions.forEach((_, idx) => {
				dispatch('dimensionChange', { row, col, dimIndex: idx, value: targetStep });
			});
		} else {
			// Scale proportionally
			const scaleFactor = targetAvg / currentAvg;
			cell.dimensions.forEach((dim, idx) => {
				const newValue = snapToStep(Math.min(100, Math.max(0, dim.value * scaleFactor)));
				dispatch('dimensionChange', { row, col, dimIndex: idx, value: newValue });
			});
		}
	}

	// Handle dimension bar click - cycle through steps or set directly
	function handleDimensionBarClick(dimIndex: number, stepIndex: number) {
		if (!selectedCell) return;
		const stepValue = DIM_STEPS[stepIndex];
		dispatch('dimensionChange', {
			row: selectedCell.row,
			col: selectedCell.col,
			dimIndex,
			value: stepValue
		});
	}

	// Get dimension bar fill count (0, 1, 2, 3 segments to fill)
	function getDimFillCount(value: number): number {
		if (value <= 0) return 0;
		if (value <= 25) return 1;
		if (value <= 75) return 2;
		return 3; // 100
	}

	function handleCellClick(row: number, col: number) {
		selectedCell = { row, col };
		showCellPopup = true;
		dispatch('cellClick', { row, col });
	}

	function getCellColor(cell: CellData) {
		if (showRiskHeatmap && cell.riskLevel) {
			const colors = {
				low: 'cell-risk-low',
				medium: 'cell-risk-medium',
				high: 'cell-risk-high'
			};
			return colors[cell.riskLevel];
		}
		return '';
	}

	function closeCellPopup() {
		showCellPopup = false;
		selectedCell = null;
	}

	function handleDocumentTabClick(docId: string) {
		matrix.setActiveDocument(docId);
		dispatch('documentChange', { documentId: docId });
	}
</script>

<div class="matrix-panel" class:compact>
	<!-- Document Tabs (no "+" button here) -->
	{#if showDocumentTabs && $documents.length > 1}
		<div class="document-tabs-container">
			<div class="document-tabs">
				{#each $documents as doc (doc.id)}
					<button
						class="document-tab"
						class:active={doc.id === $activeDocumentId}
						on:click={() => handleDocumentTabClick(doc.id)}
						title={doc.description}
					>
						<span class="tab-name">{doc.name}</span>
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Matrix Grid -->
	<div class="matrix-grid">
		<!-- Top-left corner (empty) -->
		<div class="grid-corner"></div>

		<!-- Column headers -->
		{#each columnHeaders as header}
			<div class="col-header">
				<span class="header-text">{header}</span>
			</div>
		{/each}

		<!-- Matrix body -->
		{#each matrixData as row, rowIdx}
			<!-- Row header -->
			<div class="row-header">
				<span class="header-text">{rowHeaders[rowIdx]}</span>
			</div>

			<!-- Data cells -->
			{#each row as cell, colIdx}
				{@const cellAvg = calcCellValueFromDimensions(cell.dimensions)}
				{@const filledCount = getFilledSegments(cellAvg)}
				<div
					class="matrix-cell {getCellColor(cell)}"
					class:leverage-point={cell.isLeveragePoint}
					class:selected={selectedCell?.row === rowIdx && selectedCell?.col === colIdx}
				>
					{#if cell.isLeveragePoint}
						<span class="power-indicator" title="Power Spot">⚡</span>
					{/if}
					<!-- Top 50%: click to open dimensions popup -->
					<button
						class="cell-top-area"
						on:click={() => handleCellClick(rowIdx, colIdx)}
						aria-label="Open dimensions"
					></button>
					<!-- Bottom 50%: 5-segment bar, clickable -->
					<div class="cell-bar">
						{#each Array(CELL_SEGMENTS) as _, segIdx}
							<button
								class="cell-bar-segment"
								class:filled={segIdx < filledCount}
								on:click={() => handleCellBarClick(rowIdx, colIdx, segIdx)}
								aria-label="Set level {segIdx + 1}"
							></button>
						{/each}
					</div>
				</div>
			{/each}
		{/each}
	</div>
</div>

<!-- Cell detail popup -->
{#if showCellPopup && selectedCell && matrixData[selectedCell.row]}
	<div class="popup-overlay" on:click={closeCellPopup} on:keydown={(e) => e.key === 'Escape' && closeCellPopup()} role="presentation" tabindex="-1">
		<div class="cell-popup" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true">
			<div class="popup-header">
				<h3>
					{rowHeaders[selectedCell.row]} × {columnHeaders[selectedCell.col]}
				</h3>
				<button class="close-btn" on:click={closeCellPopup}>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M18 6 6 18" />
						<path d="m6 6 12 12" />
					</svg>
				</button>
			</div>

			<div class="popup-body">
				<!-- Dimensions as visual bars (no labels, no cell value) -->
				<div class="dimensions-list">
					{#each matrixData[selectedCell.row][selectedCell.col].dimensions as dim, dimIdx}
						{@const fillCount = getDimFillCount(dim.value)}
						<div class="dimension-item">
							<div class="dimension-row">
								<span class="dim-name">{dim.name}</span>
								<div class="dim-bar">
									{#each DIM_STEPS as _, stepIdx}
										<button
											class="dim-bar-segment"
											class:filled={stepIdx < fillCount}
											on:click={() => handleDimensionBarClick(dimIdx, stepIdx)}
										></button>
									{/each}
								</div>
							</div>
							{#if dim.explanation}
								<span class="dim-explanation">{dim.explanation}</span>
							{/if}
						</div>
					{/each}
				</div>

				{#if matrixData[selectedCell.row][selectedCell.col].isLeveragePoint}
					<div class="power-spot-badge">
						<span>⚡</span>
						<span>Power Spot</span>
					</div>
				{/if}
			</div>

			<div class="popup-footer">
				<Button variant="ghost" on:click={closeCellPopup}>Close</Button>
			</div>
		</div>
	</div>
{/if}

<style>
	.matrix-panel {
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		padding: 0.5rem;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.matrix-panel.compact {
		padding: 0.375rem;
	}

	/* Document Tabs */
	.document-tabs-container {
		padding: 0 0 0.5rem;
		flex-shrink: 0;
	}

	.document-tabs {
		display: flex;
		gap: 0.25rem;
		overflow-x: auto;
	}

	.document-tab {
		padding: 0.375rem 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid transparent;
		border-radius: 0.375rem;
		font-size: 0.6875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.15s ease;
		white-space: nowrap;
		flex-shrink: 0;
	}

	.document-tab:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-200);
	}

	[data-theme='dark'] .document-tab:hover {
		background: rgba(15, 76, 117, 0.2);
		border-color: var(--color-primary-700);
	}

	.document-tab.active {
		background: var(--color-primary-100);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
	}

	[data-theme='dark'] .document-tab.active {
		background: rgba(15, 76, 117, 0.3);
		color: var(--color-primary-300);
	}

	.tab-name {
		max-width: 100px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.matrix-grid {
		display: grid;
		grid-template-columns: 100px repeat(5, 1fr);
		grid-template-rows: 56px repeat(5, minmax(0, 1fr));
		gap: 2px;
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	.compact .matrix-grid {
		grid-template-columns: 90px repeat(5, 1fr);
		grid-template-rows: 52px repeat(5, minmax(0, 1fr));
		gap: 2px;
	}

	.grid-corner {
		/* Empty corner cell */
	}

	.col-header {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		padding: 0.125rem;
		background: transparent;
		overflow: hidden;
	}

	.row-header {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding: 0.125rem 0.25rem;
		background: transparent;
		overflow: hidden;
	}

	/* Column header text: vertical, one word per line (max 3 lines) */
	.col-header .header-text {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-whisper);
		text-align: center;
		line-height: 1.2;
		text-transform: uppercase;
		letter-spacing: 0.02em;
		word-spacing: 100vw; /* Forces each word to its own line */
		overflow: hidden;
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
	}

	/* Row header text: horizontal, single line */
	.row-header .header-text {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-whisper);
		text-align: right;
		line-height: 1.2;
		text-transform: uppercase;
		letter-spacing: 0.02em;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 100%;
	}

	.compact .col-header .header-text,
	.compact .row-header .header-text {
		font-size: 0.6875rem;
	}

	.matrix-cell {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: stretch;
		justify-content: stretch;
		padding: 0;
		border-radius: 0.25rem;
		border: none;
		background: var(--color-field-depth);
		transition: all 0.1s ease;
		min-height: 0;
		overflow: hidden;
	}

	.matrix-cell:hover {
		background: var(--color-accent-subtle);
	}

	.matrix-cell.selected {
		background: var(--color-accent-subtle);
		box-shadow: inset 0 0 0 1px var(--color-text-source);
	}

	.matrix-cell.leverage-point {
		box-shadow: inset 0 0 0 1px var(--color-text-source);
	}

	.matrix-cell.cell-risk-low {
		background: rgba(22, 163, 74, 0.08);
	}

	.matrix-cell.cell-risk-medium {
		background: rgba(217, 119, 6, 0.08);
	}

	.matrix-cell.cell-risk-high {
		background: rgba(220, 38, 38, 0.08);
	}

	/* Top 50% - click to open dimensions popup */
	.cell-top-area {
		flex: 1;
		background: transparent;
		border: none;
		cursor: pointer;
		min-height: 50%;
	}

	.cell-top-area:hover {
		background: rgba(0, 0, 0, 0.05);
	}

	[data-theme='dark'] .cell-top-area:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	/* Bottom 50% - 5-segment bar */
	.cell-bar {
		display: flex;
		gap: 2px;
		padding: 0.25rem;
		min-height: 50%;
		align-items: stretch;
	}

	.compact .cell-bar {
		padding: 0.125rem;
		gap: 1px;
	}

	.cell-bar-segment {
		flex: 1;
		background: var(--color-veil-thin);
		border: none;
		border-radius: 2px;
		cursor: pointer;
		transition: all 0.1s ease;
		min-height: 8px;
	}

	.cell-bar-segment:hover {
		background: var(--color-primary-300);
	}

	.cell-bar-segment.filled {
		background: var(--color-primary-500);
	}

	.cell-bar-segment.filled:hover {
		background: var(--color-primary-600);
	}

	[data-theme='dark'] .cell-bar-segment {
		background: rgba(255, 255, 255, 0.1);
	}

	[data-theme='dark'] .cell-bar-segment:hover {
		background: var(--color-primary-400);
	}

	[data-theme='dark'] .cell-bar-segment.filled {
		background: var(--color-primary-400);
	}

	[data-theme='dark'] .cell-bar-segment.filled:hover {
		background: var(--color-primary-300);
	}

	.power-indicator {
		position: absolute;
		top: 2px;
		right: 2px;
		font-size: 0.5rem;
		background: var(--color-text-source);
		color: var(--color-field-void);
		width: 12px;
		height: 12px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1;
	}

	.compact .power-indicator {
		width: 10px;
		height: 10px;
		font-size: 0.4375rem;
	}

	/* Popup styles */
	.popup-overlay {
		position: fixed;
		inset: 0;
		background: rgba(255, 255, 255, 0.8);
		backdrop-filter: blur(8px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: 1rem;
	}

	[data-theme='dark'] .popup-overlay {
		background: rgba(0, 0, 0, 0.8);
	}

	.cell-popup {
		width: 100%;
		max-width: 560px;
		background: var(--color-field-surface);
		border-radius: 1rem;
		box-shadow: var(--shadow-elevated);
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		background: var(--color-field-depth);
		border-radius: 1rem 1rem 0 0;
	}

	.popup-header h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.close-btn {
		padding: 0.5rem;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.375rem;
		transition: all 0.15s ease;
	}

	.close-btn:hover {
		background: var(--color-field-depth);
		color: var(--color-text-source);
	}

	.popup-body {
		padding: 0.75rem 1rem;
	}

	/* Dimensions list in popup */
	.dimensions-list {
		display: flex;
		flex-direction: column;
		gap: 0.875rem;
	}

	.dimension-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.dimension-row {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.dim-name {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-source);
		flex: 1;
		min-width: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.dim-explanation {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
		line-height: 1.3;
		padding-left: 0;
	}

	.dim-bar {
		display: flex;
		gap: 4px;
		flex-shrink: 0;
	}

	.dim-bar-segment {
		width: 28px;
		height: 16px;
		background: var(--color-veil-thin);
		border: none;
		border-radius: 3px;
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.dim-bar-segment:hover {
		background: var(--color-primary-300);
	}

	.dim-bar-segment.filled {
		background: var(--color-primary-500);
	}

	.dim-bar-segment.filled:hover {
		background: var(--color-primary-600);
	}

	[data-theme='dark'] .dim-bar-segment {
		background: rgba(255, 255, 255, 0.15);
	}

	[data-theme='dark'] .dim-bar-segment:hover {
		background: var(--color-primary-400);
	}

	[data-theme='dark'] .dim-bar-segment.filled {
		background: var(--color-primary-400);
	}

	[data-theme='dark'] .dim-bar-segment.filled:hover {
		background: var(--color-primary-300);
	}

	.power-spot-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		margin-top: 0.5rem;
		background: var(--color-accent);
		color: white;
		border-radius: 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		background: var(--color-field-depth);
		border-radius: 0 0 1rem 1rem;
	}
</style>
