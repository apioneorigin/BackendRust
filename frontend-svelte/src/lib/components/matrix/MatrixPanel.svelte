<script lang="ts">
	/**
	 * MatrixPanel - Embeddable 5x5 transformation matrix
	 *
	 * ARCHITECTURE:
	 * - Shows document tabs at top (each with its own matrix)
	 * - Each cell is a single clickable block showing Low/Med/High
	 * - Single-click cycles value: Low → Med → High → Low
	 * - Double-click opens dimensions popup
	 * - Dimension cells also cycle on single-click
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

	// 3-step values: Low, Medium, High
	const DIM_STEPS = [33, 67, 100];

	let selectedCell: { row: number; col: number } | null = null;
	let showCellPopup = false;
	let isPopulatingDoc: string | null = null;

	// Single-click vs double-click timer for matrix cells
	let cellClickTimer: ReturnType<typeof setTimeout> | null = null;
	let cellClickTarget: { row: number; col: number } | null = null;

	// Undo/redo history
	type DimensionChange = { row: number; col: number; dimIndex: number; oldValue: number; newValue: number };
	type EditEntry = { changes: DimensionChange[] };

	let editHistory: EditEntry[] = [];
	let editIndex = -1;

	$: canUndo = editIndex >= 0;
	$: canRedo = editIndex < editHistory.length - 1;

	let prevDocId: string | null = null;
	$: if ($activeDocumentId && $activeDocumentId !== prevDocId) {
		prevDocId = $activeDocumentId;
		editHistory = [];
		editIndex = -1;
		if (autoSaveTimer) clearTimeout(autoSaveTimer);
	}

	let autoSaveTimer: ReturnType<typeof setTimeout> | null = null;

	function scheduleAutoSave() {
		if (autoSaveTimer) clearTimeout(autoSaveTimer);
		autoSaveTimer = setTimeout(autoSave, 1500);
	}

	async function autoSave() {
		autoSaveTimer = null;
		const touchedDims = new Set<string>();
		for (const entry of editHistory) {
			for (const ch of entry.changes) {
				touchedDims.add(`${ch.row}-${ch.col}-${ch.dimIndex}`);
			}
		}
		if (touchedDims.size === 0) return;

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

	function pushEdit(changes: DimensionChange[]) {
		if (changes.length === 0) return;
		editHistory = [...editHistory.slice(0, editIndex + 1), { changes }];
		editIndex = editHistory.length - 1;
		for (const ch of changes) {
			matrix.updateCellDimension(ch.row, ch.col, ch.dimIndex, ch.newValue);
		}
		scheduleAutoSave();
	}

	function undo() {
		if (!canUndo) return;
		const entry = editHistory[editIndex];
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
		if (cellClickTimer) clearTimeout(cellClickTimer);
	});

	function hasFullData(doc: Document): boolean {
		const cells = doc.matrix_data?.cells || {};
		return Object.keys(cells).length >= 100;
	}

	function isPowerSpot(cell: CellData): boolean {
		return cell.isLeveragePoint;
	}

	function isRiskCell(cell: CellData): boolean {
		return cell.riskLevel === 'medium' || cell.riskLevel === 'high';
	}

	function shouldHideCell(cell: CellData): boolean {
		if (showPowerSpotsView && !isPowerSpot(cell)) return true;
		if (showRiskView && !isRiskCell(cell)) return true;
		return false;
	}

	function calcCellValueFromDimensions(dimensions: CellDimension[]): number {
		if (!dimensions || dimensions.length === 0) return 67;
		const sum = dimensions.reduce((acc, d) => acc + d.value, 0);
		return Math.round(sum / dimensions.length);
	}

	// Snap to nearest step
	function snapToStep(value: number): number {
		if (value <= 33) return 33;
		if (value <= 67) return 67;
		return 100;
	}

	// Cycle to next step: Low → Med → High → Low
	function getNextStep(currentValue: number): number {
		const snap = snapToStep(currentValue);
		if (snap <= 33) return 67;
		if (snap <= 67) return 100;
		return 33;
	}

	// Get level label for display
	function getLevelLabel(value: number): string {
		if (value <= 0) return '';
		if (value <= 33) return 'Low';
		if (value <= 67) return 'Med';
		return 'High';
	}

	// Matrix cell: single-click cycles, double-click opens popup
	function handleMatrixCellInteraction(row: number, col: number) {
		if (stubMode) return;
		const cell = matrixData[row]?.[col];
		if (!cell) return;

		// In filtered views, single click shows explanation
		if (showPowerSpotsView || showRiskView) {
			handleCellClick(row, col);
			return;
		}

		if (cellClickTimer && cellClickTarget?.row === row && cellClickTarget?.col === col) {
			// Double-click: open dimensions popup
			clearTimeout(cellClickTimer);
			cellClickTimer = null;
			cellClickTarget = null;
			handleCellClick(row, col);
		} else {
			if (cellClickTimer) clearTimeout(cellClickTimer);
			cellClickTarget = { row, col };
			cellClickTimer = setTimeout(() => {
				cellClickTimer = null;
				cellClickTarget = null;
				handleCellCycle(row, col);
			}, 300);
		}
	}

	// Single-click: cycle all dimensions to next step
	function handleCellCycle(row: number, col: number) {
		const cell = matrixData[row]?.[col];
		if (!cell?.dimensions) return;
		if (shouldHideCell(cell)) return;

		const avg = calcCellValueFromDimensions(cell.dimensions);
		const nextValue = getNextStep(avg);

		const changes: DimensionChange[] = [];
		for (let i = 0; i < cell.dimensions.length; i++) {
			if (cell.dimensions[i].value !== nextValue) {
				changes.push({ row, col, dimIndex: i, oldValue: cell.dimensions[i].value, newValue: nextValue });
			}
		}
		pushEdit(changes);
	}

	// Dimension cell: single-click cycles that dimension
	function handleDimensionCycle(dimIndex: number) {
		if (!selectedCell) return;
		const { row, col } = selectedCell;
		const cell = matrixData[row]?.[col];
		if (!cell?.dimensions?.[dimIndex]) return;

		const currentValue = cell.dimensions[dimIndex].value;
		const nextValue = getNextStep(currentValue);
		pushEdit([{ row, col, dimIndex, oldValue: currentValue, newValue: nextValue }]);
	}

	function handleCellClick(row: number, col: number) {
		const cell = matrixData[row]?.[col];
		if (!cell) return;

		if (showPowerSpotsView && isPowerSpot(cell)) {
			dispatch('showPowerSpotExplanation', { row, col, cell });
			return;
		}
		if (showRiskView && isRiskCell(cell)) {
			dispatch('showRiskExplanation', { row, col, cell });
			return;
		}
		if (shouldHideCell(cell)) return;

		selectedCell = { row, col };
		showCellPopup = true;
		dispatch('cellClick', { row, col });
	}

	function getCellColor(cell: CellData) {
		if (showRiskView && isRiskCell(cell)) {
			const colors = {
				low: '',
				medium: 'cell-risk-medium',
				high: 'cell-risk-high'
			};
			return colors[cell.riskLevel || 'low'];
		}
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
				<!-- svelte-ignore a11y-click-events-have-key-events -->
				<div
					class="matrix-cell {stubMode ? '' : getCellColor(cell)}"
					class:leverage-point={!stubMode && cell.isLeveragePoint}
					class:selected={!stubMode && selectedCell?.row === rowIdx && selectedCell?.col === colIdx}
					class:stub-cell={stubMode}
					class:row-alt={rowIdx % 2 === 1}
					class:col-alt={colIdx % 2 === 1}
					on:click={() => handleMatrixCellInteraction(rowIdx, colIdx)}
					role="button"
					tabindex={stubMode ? -1 : 0}
				>
					{#if !stubMode && cell.isLeveragePoint}
						<span class="power-indicator" title="Power Spot">⚡</span>
					{/if}
					{#if !stubMode}
						<span class="cell-level-text">{getLevelLabel(cellAvg)}</span>
					{/if}
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
				<div class="dimensions-list">
					{#each matrixData[selectedCell.row][selectedCell.col].dimensions as dim, dimIdx}
						<button class="dimension-cell" on:click={() => handleDimensionCycle(dimIdx)}>
							<span class="dim-name">{dim.name}</span>
							<span class="dim-level-text">{getLevelLabel(dim.value)}</span>
						</button>
						{#if dim.explanation}
							<span class="dim-explanation">{dim.explanation}</span>
						{/if}
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
		align-items: center;
		justify-content: center;
		padding: 0;
		border-radius: 0.25rem;
		border: none;
		background: var(--color-field-depth);
		transition: all 0.1s ease;
		min-height: 0;
		overflow: hidden;
		cursor: pointer;
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

	.matrix-cell.cell-risk-medium {
		background: rgba(217, 119, 6, 0.08);
	}

	.matrix-cell.cell-risk-high {
		background: rgba(220, 38, 38, 0.08);
	}

	.cell-level-text {
		font-size: 0.6875rem;
		font-weight: 500;
		color: var(--color-primary-500);
		text-transform: uppercase;
		letter-spacing: 0.03em;
		user-select: none;
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
		gap: 0.5rem;
	}

	.dimension-cell {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.625rem 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.15s ease;
		width: 100%;
		text-align: left;
		font-family: inherit;
	}

	.dimension-cell:hover {
		border-color: var(--color-primary-400);
		background: var(--color-primary-50);
	}

	.dimension-cell:active {
		transform: scale(0.99);
	}

	.dim-name {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-primary-500);
		flex: 1;
		min-width: 0;
	}

	.dim-level-text {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-primary-500);
		text-transform: uppercase;
		letter-spacing: 0.03em;
		flex-shrink: 0;
	}

	.dim-explanation {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
		line-height: 1.3;
		padding-left: 0.75rem;
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
