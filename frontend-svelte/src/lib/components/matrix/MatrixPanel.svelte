<script lang="ts">
	/**
	 * MatrixPanel - Embeddable 5x5 transformation matrix
	 *
	 * Extracted from matrix page for unified layout embedding.
	 * Shows matrix grid with risk heatmap, leverage points, and cell popup.
	 */

	import { createEventDispatcher } from 'svelte';
	import { Button } from '$lib/components/ui';

	export let matrixData: CellData[][] = [];
	export let rowHeaders: string[] = ['Dimension 1', 'Dimension 2', 'Dimension 3', 'Dimension 4', 'Dimension 5'];
	export let columnHeaders: string[] = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5'];
	export let showRiskHeatmap = false;
	export let compact = false;

	const dispatch = createEventDispatcher<{
		cellClick: { row: number; col: number };
		cellChange: { row: number; col: number; value: number };
	}>();

	interface CellData {
		value: number;
		dimensions: number[];
		confidence: number;
		description: string;
		isLeveragePoint: boolean;
		riskLevel?: 'low' | 'medium' | 'high';
	}

	let selectedCell: { row: number; col: number } | null = null;
	let showCellPopup = false;

	function handleCellClick(row: number, col: number) {
		selectedCell = { row, col };
		showCellPopup = true;
		dispatch('cellClick', { row, col });
	}

	function handleCellValueChange(row: number, col: number, value: number) {
		const newValue = Math.max(0, Math.min(100, value));
		dispatch('cellChange', { row, col, value: newValue });
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
</script>

<div class="matrix-panel" class:compact>
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
				<button
					class="matrix-cell {getCellColor(cell)}"
					class:leverage-point={cell.isLeveragePoint}
					class:selected={selectedCell?.row === rowIdx && selectedCell?.col === colIdx}
					on:click={() => handleCellClick(rowIdx, colIdx)}
				>
					{#if cell.isLeveragePoint}
						<span class="power-indicator" title="Power Spot">⚡</span>
					{/if}
					<span class="cell-value">{cell.value}</span>
					<div class="confidence-bar" style="width: {cell.confidence * 100}%"></div>
				</button>
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
				<div class="value-control">
					<label for="cell-value">Score</label>
					<div class="value-input-group">
						<button
							class="value-btn"
							on:click={() => handleCellValueChange(selectedCell.row, selectedCell.col, matrixData[selectedCell.row][selectedCell.col].value - 5)}
						>
							-
						</button>
						<input
							id="cell-value"
							type="number"
							min="0"
							max="100"
							value={matrixData[selectedCell.row][selectedCell.col].value}
							on:input={(e) => handleCellValueChange(selectedCell.row, selectedCell.col, parseInt(e.currentTarget.value) || 0)}
						/>
						<button
							class="value-btn"
							on:click={() => handleCellValueChange(selectedCell.row, selectedCell.col, matrixData[selectedCell.row][selectedCell.col].value + 5)}
						>
							+
						</button>
					</div>
				</div>

				<div class="dimensions-section">
					<h4>Dials</h4>
					<div class="dimensions-grid">
						{#each matrixData[selectedCell.row][selectedCell.col].dimensions as dim, idx}
							<div class="dimension-item">
								<span class="dim-label">Dial {idx + 1}</span>
								<div class="dim-bar-container">
									<div class="dim-bar" style="width: {dim}%"></div>
								</div>
								<span class="dim-value">{dim}</span>
							</div>
						{/each}
					</div>
				</div>

				{#if matrixData[selectedCell.row][selectedCell.col].isLeveragePoint}
					<div class="power-spot-badge">
						<span>⚡</span>
						<span>Power Spot - High Impact Cell</span>
					</div>
				{/if}
			</div>

			<div class="popup-footer">
				<Button variant="ghost" on:click={closeCellPopup}>Close</Button>
				<Button variant="primary" on:click={closeCellPopup}>Save</Button>
			</div>
		</div>
	</div>
{/if}

<style>
	.matrix-panel {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		padding: 1rem;
		height: 100%;
		display: flex;
		flex-direction: column;
	}

	.matrix-panel.compact {
		padding: 0.75rem;
	}

	.matrix-grid {
		display: grid;
		grid-template-columns: 80px repeat(5, 1fr);
		grid-template-rows: 32px repeat(5, 1fr);
		gap: 3px;
		flex: 1;
		min-height: 0;
	}

	.compact .matrix-grid {
		grid-template-columns: 60px repeat(5, 1fr);
		grid-template-rows: 28px repeat(5, 1fr);
		gap: 2px;
	}

	.grid-corner {
		/* Empty corner cell */
	}

	.col-header,
	.row-header {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.25rem;
		background: var(--color-primary-50);
		border-radius: 0.25rem;
	}

	[data-theme='dark'] .col-header,
	[data-theme='dark'] .row-header {
		background: rgba(15, 76, 117, 0.3);
	}

	.header-text {
		font-size: 0.625rem;
		font-weight: 600;
		color: var(--color-primary-700);
		text-align: center;
		line-height: 1.2;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.compact .header-text {
		font-size: 0.5625rem;
	}

	[data-theme='dark'] .header-text {
		color: var(--color-primary-300);
	}

	.matrix-cell {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0.5rem;
		border-radius: 0.375rem;
		border: 1px solid var(--color-veil-thin);
		background: var(--color-field-depth);
		cursor: pointer;
		transition: all 0.15s ease;
		min-height: 0;
	}

	.compact .matrix-cell {
		padding: 0.25rem;
	}

	.matrix-cell:hover {
		border-color: var(--color-primary-400);
		transform: translateY(-1px);
	}

	.matrix-cell.selected {
		border-color: var(--color-primary-500);
		box-shadow: 0 0 0 2px var(--color-primary-100);
	}

	.matrix-cell.leverage-point {
		border-color: var(--color-accent);
		border-width: 2px;
	}

	.matrix-cell.cell-risk-low {
		background: rgba(5, 150, 105, 0.1);
	}

	.matrix-cell.cell-risk-medium {
		background: rgba(217, 119, 6, 0.1);
	}

	.matrix-cell.cell-risk-high {
		background: rgba(220, 38, 38, 0.1);
	}

	[data-theme='dark'] .matrix-cell.cell-risk-low {
		background: rgba(52, 211, 153, 0.15);
	}

	[data-theme='dark'] .matrix-cell.cell-risk-medium {
		background: rgba(251, 191, 36, 0.15);
	}

	[data-theme='dark'] .matrix-cell.cell-risk-high {
		background: rgba(248, 113, 113, 0.15);
	}

	.power-indicator {
		position: absolute;
		top: 2px;
		right: 2px;
		font-size: 0.5rem;
		background: var(--color-accent);
		color: white;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.compact .power-indicator {
		width: 12px;
		height: 12px;
		font-size: 0.4375rem;
	}

	.cell-value {
		font-size: 1rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.compact .cell-value {
		font-size: 0.875rem;
	}

	.confidence-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		height: 2px;
		background: var(--color-primary-400);
		border-radius: 0 0 0.25rem 0.25rem;
		transition: width 0.3s ease;
	}

	/* Popup styles */
	.popup-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: 1rem;
	}

	.cell-popup {
		width: 100%;
		max-width: 380px;
		max-height: 90vh;
		overflow-y: auto;
		background: var(--color-field-surface);
		border-radius: 1rem;
		border: 1px solid var(--color-veil-thin);
		box-shadow: var(--shadow-elevated);
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		border-bottom: 1px solid var(--color-veil-thin);
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
		padding: 1rem;
	}

	.value-control {
		margin-bottom: 1.25rem;
	}

	.value-control label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.5rem;
	}

	.value-input-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.value-btn {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-source);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.value-btn:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	[data-theme='dark'] .value-btn:hover {
		background: rgba(15, 76, 117, 0.3);
	}

	.value-input-group input {
		flex: 1;
		text-align: center;
		padding: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text-source);
		background: var(--color-field-void);
	}

	.value-input-group input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.dimensions-section h4 {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.75rem;
	}

	.dimensions-grid {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.dimension-item {
		display: grid;
		grid-template-columns: 50px 1fr 35px;
		align-items: center;
		gap: 0.5rem;
	}

	.dim-label {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	.dim-bar-container {
		height: 6px;
		background: var(--color-field-depth);
		border-radius: 3px;
		overflow: hidden;
	}

	.dim-bar {
		height: 100%;
		background: var(--color-primary-400);
		border-radius: 3px;
		transition: width 0.3s ease;
	}

	.dim-value {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-source);
		text-align: right;
	}

	.power-spot-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem;
		margin-top: 1rem;
		background: var(--color-accent);
		color: white;
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 500;
	}

	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1rem;
		border-top: 1px solid var(--color-veil-thin);
	}
</style>
