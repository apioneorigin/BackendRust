<script lang="ts">
	/**
	 * MatrixPanel - Embeddable 5x5 transformation matrix
	 *
	 * Extracted from matrix page for unified layout embedding.
	 * Shows matrix grid with risk heatmap, leverage points, and cell popup.
	 * Each cell has 5 contextual dimensions with 5-step button selectors.
	 */

	import { createEventDispatcher } from 'svelte';
	import { Button } from '$lib/components/ui';
	import type { CellData, CellDimension } from '$lib/stores';

	export let matrixData: CellData[][] = [];
	export let rowHeaders: string[] = ['Dimension 1', 'Dimension 2', 'Dimension 3', 'Dimension 4', 'Dimension 5'];
	export let columnHeaders: string[] = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5'];
	export let showRiskHeatmap = false;
	export let compact = false;

	const dispatch = createEventDispatcher<{
		cellClick: { row: number; col: number };
		cellChange: { row: number; col: number; value: number };
		dimensionChange: { row: number; col: number; dimIndex: number; value: number };
	}>();

	// The 5 discrete step values for dimensions
	const STEP_VALUES = [0, 25, 50, 75, 100];

	let selectedCell: { row: number; col: number } | null = null;
	let showCellPopup = false;

	// Get the step index (0-4) from a dimension value
	function getStepIndex(value: number): number {
		const idx = STEP_VALUES.indexOf(value);
		return idx >= 0 ? idx : 2; // Default to middle step if value not found
	}

	// Handle dimension step button click
	function handleDimensionStepClick(dimIndex: number, stepValue: number) {
		if (!selectedCell) return;
		dispatch('dimensionChange', {
			row: selectedCell.row,
			col: selectedCell.col,
			dimIndex,
			value: stepValue
		});
	}

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
					<h4>Dimensions</h4>
					<div class="dimensions-grid">
						{#each matrixData[selectedCell.row][selectedCell.col].dimensions as dim, dimIdx}
							<div class="dimension-item">
								<span class="dim-name">{dim.name}</span>
								<div class="step-buttons">
									{#each STEP_VALUES as stepValue, stepIdx}
										<button
											class="step-btn"
											class:active={dim.value === stepValue}
											on:click={() => handleDimensionStepClick(dimIdx, stepValue)}
											title={dim.stepLabels?.[stepIdx] || `Step ${stepIdx + 1}`}
										>
											{dim.stepLabels?.[stepIdx] || `Step ${stepIdx + 1}`}
										</button>
									{/each}
								</div>
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
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		padding: 1rem;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.matrix-panel.compact {
		padding: 0.75rem;
	}

	.matrix-panel.compact .matrix-grid {
		grid-template-columns: minmax(50px, 60px) repeat(5, 1fr);
	}

	.matrix-grid {
		display: grid;
		grid-template-columns: minmax(60px, 80px) repeat(5, 1fr);
		grid-template-rows: 28px repeat(5, 1fr);
		gap: 2px;
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	.compact .matrix-grid {
		grid-template-columns: minmax(50px, 60px) repeat(5, 1fr);
		grid-template-rows: 24px repeat(5, 1fr);
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
		background: transparent;
	}

	.header-text {
		font-size: 0.5625rem;
		font-weight: 500;
		color: var(--color-text-whisper);
		text-align: center;
		line-height: 1.2;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.compact .header-text {
		font-size: 0.5rem;
	}

	.matrix-cell {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0.375rem;
		border-radius: 0.25rem;
		border: none;
		background: var(--color-field-depth);
		cursor: pointer;
		transition: all 0.1s ease;
		min-height: 0;
	}

	.compact .matrix-cell {
		padding: 0.25rem;
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
	}

	.compact .power-indicator {
		width: 10px;
		height: 10px;
		font-size: 0.4375rem;
	}

	.cell-value {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.compact .cell-value {
		font-size: 0.75rem;
	}

	.confidence-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		height: 2px;
		background: var(--color-text-source);
		border-radius: 0 0 0.25rem 0.25rem;
		transition: width 0.2s ease;
		opacity: 0.3;
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
		max-width: 360px;
		max-height: 90vh;
		overflow-y: auto;
		background: var(--color-field-surface);
		border-radius: 1rem;
		box-shadow: var(--shadow-elevated);
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
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
		border: none;
		border-radius: 0.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-source);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.value-btn:hover {
		background: var(--color-primary-50);
		color: var(--color-primary-600);
	}

	[data-theme='dark'] .value-btn:hover {
		background: rgba(15, 76, 117, 0.3);
		color: var(--color-primary-400);
	}

	.value-input-group input {
		flex: 1;
		text-align: center;
		padding: 0.75rem;
		border: none;
		border-radius: 0.5rem;
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text-source);
		background: var(--color-field-depth);
		transition: all 0.15s ease;
	}

	.value-input-group input:focus {
		outline: none;
		background: var(--color-field-void);
		box-shadow: var(--shadow-sm);
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
		gap: 1rem;
	}

	.dimension-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.dim-name {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.step-buttons {
		display: flex;
		gap: 0.25rem;
		flex-wrap: wrap;
	}

	.step-btn {
		flex: 1;
		min-width: 0;
		padding: 0.375rem 0.25rem;
		background: transparent;
		border: 1px solid var(--color-accent);
		border-radius: 0.75rem;
		font-size: 0.625rem;
		font-weight: 400;
		color: var(--color-accent);
		cursor: pointer;
		transition: all 0.1s ease;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.step-btn:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.step-btn.active {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: #ffffff;
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
		background: var(--color-field-depth);
		border-radius: 0 0 1rem 1rem;
	}
</style>
