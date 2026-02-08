<script lang="ts">
	/**
	 * MatrixPanel - Embeddable 5x5 transformation matrix
	 *
	 * ARCHITECTURE:
	 * - Shows document tabs at top (each with its own matrix)
	 * - Both cell bars and dimension bars use 3 segments: Low (0), Medium (50), High (100)
	 * - Cell value = average of 5 dimensions, displayed as nearest segment
	 * - Clicking a cell bar segment sets ALL dimensions to that step
	 */

	import { createEventDispatcher, onDestroy } from 'svelte';
	import { matrix, matrixDocuments as documents, activeDocumentId, activeDocument } from '$lib/stores';
	import type { CellData, CellDimension, MatrixDocument as Document } from '$lib/stores';

	export let matrixData: CellData[][] = [];
	export let rowHeaders: string[] = ['Dimension 1', 'Dimension 2', 'Dimension 3', 'Dimension 4', 'Dimension 5'];
	export let columnHeaders: string[] = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5'];
	export let showPowerSpotsView = false;
	export let showRiskView = false;
	export let compact = false;
	export let showDocumentTabs = true;
	export let stubMode = false;

	const dispatch = createEventDispatcher<{
		cellClick: { row: number; col: number };
		documentChange: { documentId: string };
		showPowerSpotExplanation: { row: number; col: number; cell: CellData };
		showRiskExplanation: { row: number; col: number; cell: CellData };
	}>();

	// Both cell bars and dimension bars use the same 3 steps: Low, Medium, High
	const DIM_STEPS = [0, 50, 100];
	const CELL_SEGMENTS = 3;

	let selectedCell: { row: number; col: number } | null = null;
	let showCellPopup = false;
	let isPopulatingDoc: string | null = null;  // Track which doc is being populated

	// Undo/redo history
	type DimensionChange = { row: number; col: number; dimIndex: number; oldValue: number; newValue: number };
	type EditEntry = { changes: DimensionChange[] };

	let editHistory: EditEntry[] = [];
	let editIndex = -1; // points to last applied edit (-1 = none)

	$: canUndo = editIndex >= 0;
	$: canRedo = editIndex < editHistory.length - 1;

	// Clear edit history when active document changes
	let prevDocId: string | null = null;
	$: if ($activeDocumentId && $activeDocumentId !== prevDocId) {
		prevDocId = $activeDocumentId;
		editHistory = [];
		editIndex = -1;
		if (autoSaveTimer) clearTimeout(autoSaveTimer);
	}

	// Auto-save: debounced persistence to backend
	let autoSaveTimer: ReturnType<typeof setTimeout> | null = null;

	function scheduleAutoSave() {
		if (autoSaveTimer) clearTimeout(autoSaveTimer);
		autoSaveTimer = setTimeout(autoSave, 1500);
	}

	async function autoSave() {
		autoSaveTimer = null;
		// Collect all touched dimensions from full history
		const touchedDims = new Set<string>();
		for (const entry of editHistory) {
			for (const ch of entry.changes) {
				touchedDims.add(`${ch.row}-${ch.col}-${ch.dimIndex}`);
			}
		}
		if (touchedDims.size === 0) return;

		// Read current values from matrixData prop (reflects undo/redo state)
		const changes: Array<{ row: number; col: number; dimIdx: number; value: number }> = [];
		for (const key of touchedDims) {
			const [row, col, dimIdx] = key.split('-').map(Number);
			const cell = matrixData[row]?.[col];
			if (!cell?.dimensions?.[dimIdx]) continue;
			changes.push({ row, col, dimIdx, value: cell.dimensions[dimIdx].value });
		}
		if (changes.length === 0) return;
		await matrix.saveCellChanges(changes);
	}

	// Push a batch of changes as a single undo-able operation
	function pushEdit(changes: DimensionChange[]) {
		if (changes.length === 0) return;
		// Truncate any redo entries
		editHistory = [...editHistory.slice(0, editIndex + 1), { changes }];
		editIndex = editHistory.length - 1;
		// Apply all changes to store
		for (const ch of changes) {
			matrix.updateCellDimension(ch.row, ch.col, ch.dimIndex, ch.newValue);
		}
		scheduleAutoSave();
	}

	function undo() {
		if (!canUndo) return;
		const entry = editHistory[editIndex];
		// Revert in reverse order
		for (let i = entry.changes.length - 1; i >= 0; i--) {
			const ch = entry.changes[i];
			matrix.updateCellDimension(ch.row, ch.col, ch.dimIndex, ch.oldValue);
		}
		editIndex--;
		scheduleAutoSave();
	}

	function redo() {
		if (!canRedo) return;
		editIndex++;
		const entry = editHistory[editIndex];
		for (const ch of entry.changes) {
			matrix.updateCellDimension(ch.row, ch.col, ch.dimIndex, ch.newValue);
		}
		scheduleAutoSave();
	}

	onDestroy(() => {
		if (autoSaveTimer) clearTimeout(autoSaveTimer);
	});

	// Check if a document has full data (100 cells)
	function hasFullData(doc: Document): boolean {
		const cells = doc.matrix_data?.cells || {};
		return Object.keys(cells).length >= 100;
	}

	// Check if cell is a power spot (leverage point)
	function isPowerSpot(cell: CellData): boolean {
		return cell.isLeveragePoint;
	}

	// Check if cell has risk (medium or high)
	function isRiskCell(cell: CellData): boolean {
		return cell.riskLevel === 'medium' || cell.riskLevel === 'high';
	}

	// Check if cell should be hidden in filtered views
	function shouldHideCell(cell: CellData): boolean {
		if (showPowerSpotsView && !isPowerSpot(cell)) return true;
		if (showRiskView && !isRiskCell(cell)) return true;
		return false;
	}

	// Calculate cell value from dimensions (average)
	function calcCellValueFromDimensions(dimensions: CellDimension[]): number {
		if (!dimensions || dimensions.length === 0) return 50;
		const sum = dimensions.reduce((acc, d) => acc + d.value, 0);
		return Math.round(sum / dimensions.length);
	}

	// Get number of filled segments (0-3) from cell value (0-100)
	function getFilledSegments(value: number): number {
		if (value <= 16) return 0;
		if (value <= 50) return 1;
		if (value <= 83) return 2;
		return 3;
	}

	// Snap to nearest dimension step (0, 50, 100)
	function snapToStep(value: number): number {
		if (value < 25) return 0;
		if (value < 75) return 50;
		return 100;
	}

	// When user clicks a cell bar segment, set ALL dimensions to the corresponding step.
	// Segment 0 = Low (0), Segment 1 = Medium (50), Segment 2 = High (100).
	function handleCellBarClick(row: number, col: number, segmentIndex: number) {
		const cell = matrixData[row]?.[col];
		if (!cell?.dimensions) return;

		// Respect filtered views - don't allow editing hidden cells
		if (shouldHideCell(cell)) return;

		const targetValue = DIM_STEPS[segmentIndex];
		if (targetValue === undefined) return;

		const changes: DimensionChange[] = [];
		for (let i = 0; i < cell.dimensions.length; i++) {
			if (cell.dimensions[i].value !== targetValue) {
				changes.push({ row, col, dimIndex: i, oldValue: cell.dimensions[i].value, newValue: targetValue });
			}
		}

		pushEdit(changes);
	}

	// Handle dimension bar click - single dimension change
	function handleDimensionBarClick(dimIndex: number, stepIndex: number) {
		if (!selectedCell) return;
		const { row, col } = selectedCell;
		const stepValue = DIM_STEPS[stepIndex];
		const cell = matrixData[row]?.[col];
		if (!cell?.dimensions?.[dimIndex]) return;
		const oldValue = cell.dimensions[dimIndex].value;
		if (oldValue === stepValue) return;
		pushEdit([{ row, col, dimIndex, oldValue, newValue: stepValue }]);
	}

	// Get dimension bar fill count (0-3) matching cell bar thresholds
	function getDimFillCount(value: number): number {
		if (value <= 16) return 0;
		if (value <= 50) return 1;
		if (value <= 83) return 2;
		return 3;
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

	function handleDocumentTabClick(docId: string) {
		matrix.setActiveDocument(docId);
		dispatch('documentChange', { documentId: docId });
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
					{@const isActive = doc.id === $activeDocumentId}
					{@const isStub = !hasFullData(doc)}
					<button
						class="document-tab"
						class:active={isActive}
						class:stub={isStub}
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
		<!-- Top-left corner: undo/redo buttons live here so they never affect grid height -->
		<div class="grid-corner">
			{#if (canUndo || canRedo) && !showCellPopup}
				<button class="undo-redo-btn" on:click={undo} disabled={!canUndo} title="Undo">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M3 7v6h6" /><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
					</svg>
				</button>
				<button class="undo-redo-btn" on:click={redo} disabled={!canRedo} title="Redo">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M21 7v6h-6" /><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13" />
					</svg>
				</button>
			{/if}
		</div>

		<!-- Column headers -->
		{#each columnHeaders as header, colIdx}
			<div class="col-header" class:col-alt={colIdx % 2 === 1}>
				<span class="header-text">{header}</span>
			</div>
		{/each}

		<!-- Matrix body -->
		{#each matrixData as row, rowIdx}
			<!-- Row header -->
			<div class="row-header" class:row-alt={rowIdx % 2 === 1}>
				<span class="header-text">{rowHeaders[rowIdx]}</span>
			</div>

			<!-- Data cells -->
			{#each row as cell, colIdx}
				{@const cellAvg = stubMode ? 0 : calcCellValueFromDimensions(cell.dimensions)}
				{@const filledCount = stubMode ? 0 : getFilledSegments(cellAvg)}
				<div
					class="matrix-cell {stubMode ? '' : getCellColor(cell)}"
					class:leverage-point={!stubMode && cell.isLeveragePoint}
					class:selected={!stubMode && selectedCell?.row === rowIdx && selectedCell?.col === colIdx}
					class:stub-cell={stubMode}
					class:row-alt={rowIdx % 2 === 1}
					class:col-alt={colIdx % 2 === 1}
				>
					{#if !stubMode && cell.isLeveragePoint}
						<span class="power-indicator" title="Power Spot">⚡</span>
					{/if}
					<!-- Top 50%: click to open dimensions popup -->
					<button
						class="cell-top-area"
						on:click={() => !stubMode && handleCellClick(rowIdx, colIdx)}
						aria-label="Open dimensions"
						disabled={stubMode}
					></button>
					<!-- Bottom 50%: 5-segment bar, clickable -->
					<div class="cell-bar">
						{#each Array(CELL_SEGMENTS) as _, segIdx}
							<button
								class="cell-bar-segment"
								class:filled={segIdx < filledCount}
								on:click={() => !stubMode && handleCellBarClick(rowIdx, colIdx, segIdx)}
								aria-label="Set level {segIdx + 1}"
								disabled={stubMode}
							></button>
						{/each}
					</div>
				</div>
			{/each}
		{/each}

		<!-- Stub overlay: covers only the cell area, headers stay visible -->
		{#if stubMode}
			{@const isPopulating = isPopulatingDoc === $activeDocumentId}
			<div class="stub-overlay">
				<button
					class="stub-generate-btn"
					class:llm-active={isPopulating}
					on:click={() => {
						if (isPopulating) { matrix.cancelPopulate(); }
						else if ($activeDocumentId) { handlePopulateDocument($activeDocumentId); }
					}}
				>
					{#if isPopulating}
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<rect x="6" y="6" width="12" height="12" rx="1" />
						</svg>
						<span>Stop</span>
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<rect x="3" y="3" width="7" height="7"/>
							<rect x="14" y="3" width="7" height="7"/>
							<rect x="14" y="14" width="7" height="7"/>
							<rect x="3" y="14" width="7" height="7"/>
						</svg>
						<span>Design Your Reality</span>
					{/if}
				</button>
			</div>
		{/if}
	</div>

</div>

<!-- Cell detail popup -->
{#if showCellPopup && selectedCell && matrixData[selectedCell.row]}
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div class="popup-overlay" on:click={closeCellPopup} on:keydown={(e) => e.key === 'Escape' && closeCellPopup()} role="presentation" tabindex="-1">
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div class="cell-popup" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true">
			<div class="popup-header">
				<h3>
					{rowHeaders[selectedCell.row]} × {columnHeaders[selectedCell.col]}
				</h3>
				<div class="popup-header-actions">
					{#if canUndo || canRedo}
						<button class="undo-redo-btn" on:click={undo} disabled={!canUndo} title="Undo">
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M3 7v6h6" /><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
							</svg>
						</button>
						<button class="undo-redo-btn" on:click={redo} disabled={!canRedo} title="Redo">
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M21 7v6h-6" /><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13" />
							</svg>
						</button>
					{/if}
					<button class="close-btn" on:click={closeCellPopup}>
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M18 6 6 18" />
							<path d="m6 6 12 12" />
						</svg>
					</button>
				</div>
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
		padding: 0 0 0.125rem;
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

	.document-tabs {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		overflow-x: auto;
		padding-bottom: 0.125rem;
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

	.document-tab.active {
		background: var(--color-primary-100);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
	}

	.tab-name {
		max-width: 100px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	/* Stub document tabs (not yet populated) */
	.document-tab.stub {
		background: var(--color-field-depth);
		border: 1px dashed var(--color-veil-thin);
		cursor: default;
		opacity: 0.7;
	}

	.document-tab.stub.active {
		border-color: var(--color-primary-300);
		opacity: 1;
	}

	.matrix-grid {
		position: relative;
		display: grid;
		grid-template-columns: 105px repeat(5, 1fr);
		grid-template-rows: 48px repeat(5, minmax(0, 1fr));
		column-gap: 2px;
		row-gap: 6px;
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	.compact .matrix-grid {
		grid-template-columns: 100px repeat(5, 1fr);
		grid-template-rows: 44px repeat(5, minmax(0, 1fr));
		column-gap: 2px;
		row-gap: 4px;
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
		padding: 0.25rem 0.375rem;
		background: transparent;
		overflow: hidden;
	}

	/* Alternating color bands for clear row/column distinction */
	.row-header.row-alt {
		background: rgba(0, 0, 0, 0.04);
		border-radius: 0.25rem;
	}

	.col-header.col-alt {
		background: rgba(0, 0, 0, 0.04);
		border-radius: 0.25rem;
	}

	.matrix-cell.row-alt {
		background: rgba(0, 0, 0, 0.035);
	}

	.matrix-cell.col-alt {
		background: rgba(0, 0, 0, 0.025);
	}

	.matrix-cell.row-alt.col-alt {
		background: rgba(0, 0, 0, 0.055);
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
		overflow: visible;
		display: -webkit-box;
		line-clamp: 3;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
	}

	/* Row header text: one word per line, right-aligned (matches column header pattern) */
	.row-header .header-text {
		font-size: 0.625rem;
		font-weight: 700;
		color: var(--color-text-whisper);
		text-align: right;
		line-height: 1.25;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		word-spacing: 100vw; /* Forces each word to its own line */
		overflow: hidden;
		display: -webkit-box;
		line-clamp: 3;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
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

	/* Top area - click to open dimensions popup */
	.cell-top-area {
		flex: 2;
		background: transparent;
		border: none;
		cursor: pointer;
		min-height: 0;
	}

	.cell-top-area:hover {
		background: rgba(0, 0, 0, 0.05);
	}

	/* Bottom thin bar strip */
	.cell-bar {
		display: flex;
		gap: 2px;
		padding: 2px 3px;
		flex-shrink: 0;
	}

	.compact .cell-bar {
		padding: 0.125rem;
		gap: 1px;
	}

	.cell-bar-segment {
		width: 28px;
		height: 8px;
		background: var(--color-veil-thin);
		border: none;
		border-radius: 2px;
		cursor: pointer;
		transition: all 0.1s ease;
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
		border-radius: 0 0 1rem 1rem;
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
	}

	.dim-explanation {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
		line-height: 1.3;
		padding-left: 0;
	}

	.dim-bar {
		display: flex;
		gap: 2px;
		flex-shrink: 0;
	}

	.dim-bar-segment {
		width: 28px;
		height: 8px;
		background: var(--color-veil-thin);
		border: none;
		border-radius: 2px;
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

	/* Popup header actions (undo/redo + close) */
	.popup-header-actions {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	/* Undo/redo buttons (shared between popup header and matrix toolbar) */
	.undo-redo-btn {
		padding: 0.375rem;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.375rem;
		transition: all 0.15s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.undo-redo-btn:hover:not(:disabled) {
		background: var(--color-field-depth);
		color: var(--color-text-source);
	}

	.undo-redo-btn:disabled {
		opacity: 0.3;
		cursor: default;
	}

	/* Grid corner (R0C0): holds undo/redo buttons without affecting layout */
	.grid-corner {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: 0.125rem;
		overflow: hidden;
	}

	/* Stub mode: cells invisible so headers stand out */
	.matrix-cell.stub-cell {
		background: transparent;
		visibility: hidden;
	}

	/* Overlay covers only the visible cell area, positioned absolutely */
	.stub-overlay {
		position: absolute;
		top: calc(56px + 2px);
		left: calc(100px + 2px);
		right: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.compact .stub-overlay {
		top: calc(52px + 2px);
		left: calc(90px + 2px);
	}

	.stub-generate-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1.25rem;
		background: var(--color-primary-500);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s ease;
		white-space: nowrap;
	}

	.stub-generate-btn:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.stub-generate-btn:disabled {
		opacity: 0.7;
		cursor: wait;
	}
</style>
