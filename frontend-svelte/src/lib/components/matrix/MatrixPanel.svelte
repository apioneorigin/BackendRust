<script lang="ts">
	/**
	 * MatrixPanel - Embeddable 5x5 transformation matrix
	 *
	 * ARCHITECTURE:
	 * - Shows document tabs at top (each with its own matrix)
	 * - Tabs show all documents: full data docs are clickable, stubs show "Generate" button
	 * - Plus button on right to generate 3 more document stubs
	 * - Displays matrix from currently active document
	 * - Each cell has 5 contextual dimensions with 3-step signal bar selectors
	 * - Power Spots View: HIDES non-leverage cells completely, shows only power spots
	 * - Risk View: HIDES low-risk cells completely, shows only medium/high risk cells
	 */

	import { createEventDispatcher } from 'svelte';
	import { Button, Spinner } from '$lib/components/ui';
	import { matrix, documents, activeDocumentId, activeDocument, isGeneratingMoreDocuments } from '$lib/stores';
	import type { CellData, CellDimension, Document } from '$lib/stores';

	export let matrixData: CellData[][] = [];
	export let rowHeaders: string[] = ['Dimension 1', 'Dimension 2', 'Dimension 3', 'Dimension 4', 'Dimension 5'];
	export let columnHeaders: string[] = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5'];
	export let showPowerSpotsView = false;
	export let showRiskView = false;
	export let compact = false;
	export let showDocumentTabs = true;

	const dispatch = createEventDispatcher<{
		cellClick: { row: number; col: number };
		cellChange: { row: number; col: number; value: number };
		dimensionChange: { row: number; col: number; dimIndex: number; value: number };
		documentChange: { documentId: string };
		showPowerSpotExplanation: { row: number; col: number; cell: CellData };
		showRiskExplanation: { row: number; col: number; cell: CellData };
	}>();

	// The 3 discrete step values for dimensions: Low, Medium, High
	const STEP_VALUES = [0, 50, 100];
	const STEP_LABELS = ['Low', 'Medium', 'High'];

	let selectedCell: { row: number; col: number } | null = null;
	let showCellPopup = false;
	let isPopulatingDoc: string | null = null;  // Track which doc is being populated

	// Check if a document has full data (100 cells)
	function hasFullData(doc: Document): boolean {
		const cells = doc.matrix_data?.cells || {};
		return Object.keys(cells).length >= 100;
	}

	// Get the step index (0-2) from a dimension value
	function getStepIndex(value: number): number {
		const idx = STEP_VALUES.indexOf(value);
		return idx >= 0 ? idx : 1; // Default to Medium if value not found
	}

	// Check if cell is a power spot (value >= 75)
	function isPowerSpot(cell: CellData): boolean {
		return cell.value >= 75 || cell.isLeveragePoint === true;
	}

	// Check if cell is high risk (only high risk shown in Risk view)
	function isRiskCell(cell: CellData): boolean {
		return cell.riskLevel === 'high';
	}

	// Check if cell should be hidden in filtered views
	// Hidden cells are completely invisible and non-clickable
	function shouldHideCell(cell: CellData): boolean {
		if (showPowerSpotsView && !isPowerSpot(cell)) {
			return true;
		}
		if (showRiskView && !isRiskCell(cell)) {
			return true;
		}
		return false;
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
		const cell = matrixData[row]?.[col];
		if (!cell) return;

		// In filtered views, clicking relevant cells shows explanation popup
		if (showPowerSpotsView && isPowerSpot(cell)) {
			dispatch('showPowerSpotExplanation', { row, col, cell });
			return;
		}
		if (showRiskView && isRiskCell(cell)) {
			dispatch('showRiskExplanation', { row, col, cell });
			return;
		}

		// In filtered views, don't allow any interaction with hidden cells
		if (shouldHideCell(cell)) {
			return;
		}

		// Normal mode: open cell detail popup
		selectedCell = { row, col };
		showCellPopup = true;
		dispatch('cellClick', { row, col });
	}

	function handleCellValueChange(row: number, col: number, value: number) {
		const newValue = Math.max(0, Math.min(100, value));
		dispatch('cellChange', { row, col, value: newValue });
	}

	function getCellColor(cell: CellData) {
		// In risk view, show risk colors for relevant cells
		if (showRiskView && isRiskCell(cell)) {
			const colors = {
				low: '',
				medium: 'cell-risk-medium',
				high: 'cell-risk-high'
			};
			return colors[cell.riskLevel || 'low'];
		}
		// In power spots view, highlight power spots
		if (showPowerSpotsView && isPowerSpot(cell)) {
			return 'cell-power-spot';
		}
		return '';
	}

	function closeCellPopup() {
		showCellPopup = false;
		selectedCell = null;
	}

	function handleDocumentTabClick(docId: string, doc: Document) {
		// Only allow clicking on documents with full data
		if (!hasFullData(doc)) return;
		matrix.setActiveDocument(docId);
		dispatch('documentChange', { documentId: docId });
	}

	async function handleGenerateMoreDocuments() {
		try {
			await matrix.generateMoreDocuments();
		} catch (error) {
			console.error('Failed to generate more documents:', error);
		}
	}

	async function handlePopulateDocument(docId: string) {
		isPopulatingDoc = docId;
		try {
			await matrix.populateDocument(docId);
			// After population, set it as active
			matrix.setActiveDocument(docId);
		} catch (error) {
			console.error('Failed to populate document:', error);
		} finally {
			isPopulatingDoc = null;
		}
	}
</script>

<div class="matrix-panel" class:compact>
	<!-- Document Tabs with Plus Button -->
	{#if showDocumentTabs && $documents.length > 0}
		<div class="document-tabs-container">
			<div class="document-tabs">
				{#each $documents as doc (doc.id)}
					{@const isFullData = hasFullData(doc)}
					{@const isActive = doc.id === $activeDocumentId}
					{@const isPopulating = isPopulatingDoc === doc.id}
					{#if isFullData}
						<!-- Full data document: clickable tab -->
						<button
							class="document-tab"
							class:active={isActive}
							on:click={() => handleDocumentTabClick(doc.id, doc)}
							title={doc.description}
						>
							<span class="tab-name">{doc.name}</span>
						</button>
					{:else}
						<!-- Stub document: show with generate button -->
						<div class="document-tab stub" title={doc.description}>
							<span class="tab-name">{doc.name}</span>
							<button
								class="generate-btn"
								on:click|stopPropagation={() => handlePopulateDocument(doc.id)}
								disabled={isPopulating}
								title="Generate full matrix data"
							>
								{#if isPopulating}
									<Spinner size="xs" />
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<path d="M12 3v3m6.366-.366-2.12 2.12M21 12h-3m.366 6.366-2.12-2.12M12 21v-3m-6.366.366 2.12-2.12M3 12h3m-.366-6.366 2.12 2.12"/>
									</svg>
								{/if}
							</button>
						</div>
					{/if}
				{/each}

				<!-- Plus button to generate more document stubs -->
				<button
					class="add-document-btn"
					on:click={handleGenerateMoreDocuments}
					disabled={$isGeneratingMoreDocuments}
					title="Generate 3 more documents"
				>
					{#if $isGeneratingMoreDocuments}
						<Spinner size="xs" />
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M12 5v14M5 12h14"/>
						</svg>
					{/if}
				</button>
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
				{#if shouldHideCell(cell)}
					<!-- Hidden cell placeholder - preserves grid structure -->
					<div class="matrix-cell-placeholder"></div>
				{:else}
					<button
						class="matrix-cell {getCellColor(cell)}"
						class:leverage-point={cell.isLeveragePoint}
						class:selected={selectedCell?.row === rowIdx && selectedCell?.col === colIdx}
						class:clickable-highlight={showPowerSpotsView && isPowerSpot(cell) || showRiskView && isRiskCell(cell)}
						on:click={() => handleCellClick(rowIdx, colIdx)}
					>
						{#if cell.isLeveragePoint && !showRiskView}
							<span class="power-indicator" title="Power Spot">⚡</span>
						{/if}
						{#if showRiskView && isRiskCell(cell)}
							<span class="risk-indicator" title="High Risk">⚠</span>
						{/if}
						<span class="cell-value">{cell.value}</span>
						<div class="confidence-bar" style="width: {cell.confidence * 100}%"></div>
					</button>
				{/if}
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
								<div class="signal-bars">
									{#each STEP_VALUES as stepValue, stepIdx}
										<button
											class="signal-bar bar-{stepIdx + 1}"
											class:filled={getStepIndex(dim.value) >= stepIdx}
											on:click={() => handleDimensionStepClick(dimIdx, stepValue)}
										>
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

	.document-name-header {
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid var(--color-veil-thin);
		background: var(--color-field-depth);
	}

	.document-name {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-primary-600);
	}

	[data-theme='dark'] .document-name {
		color: var(--color-primary-400);
	}

	.document-tabs {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		overflow-x: auto;
		padding-bottom: 0.25rem;
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

	/* Stub document tabs (not yet populated) */
	.document-tab.stub {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-veil-thin);
		cursor: default;
		opacity: 0.8;
	}

	.document-tab.stub:hover {
		background: var(--color-field-depth);
		border-color: var(--color-primary-300);
	}

	.generate-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 20px;
		height: 20px;
		padding: 0;
		background: var(--color-primary-500);
		border: none;
		border-radius: 0.25rem;
		color: white;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.generate-btn:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.generate-btn:disabled {
		opacity: 0.7;
		cursor: wait;
	}

	/* Plus button to add more documents */
	.add-document-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		padding: 0;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-primary-400);
		border-radius: 0.375rem;
		color: var(--color-primary-500);
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.add-document-btn:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-style: solid;
	}

	[data-theme='dark'] .add-document-btn:hover:not(:disabled) {
		background: rgba(15, 76, 117, 0.2);
	}

	.add-document-btn:disabled {
		opacity: 0.7;
		cursor: wait;
	}

	.matrix-grid {
		display: grid;
		grid-template-columns: 48px repeat(5, 1fr);
		grid-template-rows: 48px repeat(5, minmax(0, 1fr));
		gap: 2px;
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	.compact .matrix-grid {
		grid-template-columns: 40px repeat(5, 1fr);
		grid-template-rows: 42px repeat(5, minmax(0, 1fr));
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
		font-size: 0.625rem;
		font-weight: 900;
		color: var(--color-text-source);
		text-align: center;
		line-height: 1.2;
		text-transform: uppercase;
		letter-spacing: 0.02em;
		word-spacing: 100vw; /* Forces each word to its own line */
		overflow: visible;
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
	}

	/* Row header text: vertical, one word per line (max 3 lines) */
	.row-header .header-text {
		font-size: 0.625rem;
		font-weight: 900;
		color: var(--color-text-source);
		text-align: right;
		line-height: 1.2;
		text-transform: uppercase;
		letter-spacing: 0.02em;
		word-spacing: 100vw; /* Forces each word to its own line */
		overflow: visible;
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
	}

	.compact .col-header .header-text,
	.compact .row-header .header-text {
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

	/* Power spot highlight in power spots view */
	.matrix-cell.cell-power-spot {
		background: rgba(251, 191, 36, 0.15);
		box-shadow: inset 0 0 0 2px rgba(251, 191, 36, 0.5);
	}

	/* Placeholder for hidden cells - preserves grid structure */
	.matrix-cell-placeholder {
		/* Empty placeholder - no visible content, just occupies grid space */
		pointer-events: none;
	}

	/* Clickable highlight for relevant cells in filtered views */
	.matrix-cell.clickable-highlight {
		cursor: pointer;
		box-shadow: inset 0 0 0 2px var(--color-primary-400);
	}

	.matrix-cell.clickable-highlight:hover {
		transform: scale(1.02);
		box-shadow: inset 0 0 0 2px var(--color-primary-500);
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

	.risk-indicator {
		position: absolute;
		top: 2px;
		right: 2px;
		font-size: 0.5rem;
		background: rgba(220, 38, 38, 0.9);
		color: #ffffff;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
	}

	.compact .risk-indicator {
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

	.value-control {
		margin-bottom: 0.75rem;
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
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-field-depth);
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
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
		padding: 0.5rem;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
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
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.5rem;
	}

	.dimensions-grid {
		display: flex;
		flex-direction: column;
		gap: 0.625rem;
	}

	.dimension-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.dim-name {
		font-size: 0.8125rem;
		font-weight: 700;
		color: var(--color-text-source);
		flex: 1;
		min-width: 0;
	}

	.signal-bars {
		display: flex;
		align-items: flex-end;
		gap: 3px;
		flex-shrink: 0;
		height: 22px;
	}

	.signal-bar {
		width: 6px;
		background: var(--color-veil-thin);
		border: none;
		border-radius: 2px;
		cursor: pointer;
		padding: 0;
		transition: background 0.15s ease;
	}

	/* Bar heights - WiFi style increasing heights */
	.signal-bar.bar-1 { height: 7px; }
	.signal-bar.bar-2 { height: 14px; }
	.signal-bar.bar-3 { height: 21px; }

	/* Filled state - bars up to selected level */
	.signal-bar.filled {
		background: var(--color-primary-500);
	}

	/* Hover state */
	.signal-bar:hover {
		background: var(--color-primary-400);
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
