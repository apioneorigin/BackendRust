<script lang="ts">
	/**
	 * ContextControlPopup - Unified context control for matrix dimensions
	 *
	 * ARCHITECTURE:
	 * - ONLY shows documents with FULL DATA (100 cells populated)
	 * - Document stubs (only names/row-column labels) are NOT shown here
	 * - User must generate full data from Matrix tab before document appears here
	 * - Per-document row/column selection (10 options each, select 5)
	 * - Each document has ~20 word description
	 * - Clickable titles open InsightPopup when articulated_insight is available
	 */

	import { createEventDispatcher } from 'svelte';
	import {
		matrix,
		documents,
		activeDocumentId,
		activeDocument,
		isGeneratingMoreDocuments,
		chat
	} from '$lib/stores';
	import type { ArticulatedInsight, RowOption, ColumnOption, Document } from '$lib/stores/matrix';
	import { Button, Spinner } from '$lib/components/ui';
	import InsightPopup from './InsightPopup.svelte';

	export let open = false;

	// Check if a document has full data (100 cells)
	function hasFullData(doc: Document): boolean {
		const cells = doc.matrix_data?.cells || {};
		return Object.keys(cells).length >= 100;
	}

	// Only show documents with full data
	$: fullDataDocuments = $documents.filter(hasFullData);

	// Insight popup state
	let showInsightPopup = false;
	let selectedInsight: ArticulatedInsight | null = null;
	let selectedOptionLabel = '';
	let selectedOptionType: 'row' | 'column' = 'row';

	const dispatch = createEventDispatcher<{
		close: void;
		submit: void;
	}>();

	// Local selection state for the active document
	let selectedRows: number[] = [];
	let selectedColumns: number[] = [];

	// Track whether extra options are revealed (no LLM call needed - data already in backend)
	let showExtraDrivers = false;
	let showExtraOutcomes = false;

	// Sync local selection with active document and reset revealed state
	$: if ($activeDocument?.matrix_data) {
		selectedRows = [...($activeDocument.matrix_data.selected_rows || [0, 1, 2, 3, 4])];
		selectedColumns = [...($activeDocument.matrix_data.selected_columns || [0, 1, 2, 3, 4])];
		// Reset revealed state when document changes
		showExtraDrivers = false;
		showExtraOutcomes = false;
	}

	$: rowOptions = $activeDocument?.matrix_data?.row_options || [];
	$: columnOptions = $activeDocument?.matrix_data?.column_options || [];

	// Initially show only selected options, or all if extras are revealed
	$: visibleRowIndices = showExtraDrivers
		? rowOptions.map((_, i) => i)
		: selectedRows.slice(0, 5);
	$: visibleColIndices = showExtraOutcomes
		? columnOptions.map((_, i) => i)
		: selectedColumns.slice(0, 5);

	// Check if there are extra options to reveal
	$: hasExtraDrivers = rowOptions.length > 5 && !showExtraDrivers;
	$: hasExtraOutcomes = columnOptions.length > 5 && !showExtraOutcomes;

	$: selectedRowCount = selectedRows.length;
	$: selectedColCount = selectedColumns.length;
	$: canSubmit = selectedRowCount === 5 && selectedColCount === 5;
	$: hasOptions = rowOptions.length > 0 || columnOptions.length > 0;

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleDocumentTabClick(docId: string) {
		matrix.setActiveDocument(docId);
	}

	async function handleGenerateMoreDocuments() {
		try {
			await matrix.generateMoreDocuments();
		} catch (error) {
			console.error('Failed to generate more documents:', error);
		}
	}

	function handleToggleRow(index: number) {
		if (selectedRows.includes(index)) {
			// Allow deselection only when extra options are visible (so user can swap)
			if (!showExtraDrivers) return;
			if (selectedRows.length <= 5) return;
			selectedRows = selectedRows.filter(i => i !== index);
		} else {
			// When selecting a new one and already at 5, don't allow (user must deselect first)
			if (selectedRows.length >= 5) return;
			selectedRows = [...selectedRows, index];
		}
	}

	function handleToggleColumn(index: number) {
		if (selectedColumns.includes(index)) {
			// Allow deselection only when extra options are visible (so user can swap)
			if (!showExtraOutcomes) return;
			if (selectedColumns.length <= 5) return;
			selectedColumns = selectedColumns.filter(i => i !== index);
		} else {
			// When selecting a new one and already at 5, don't allow (user must deselect first)
			if (selectedColumns.length >= 5) return;
			selectedColumns = [...selectedColumns, index];
		}
	}

	function handleShowExtraDrivers() {
		showExtraDrivers = true;
	}

	function handleShowExtraOutcomes() {
		showExtraOutcomes = true;
	}

	async function handleSubmit() {
		if (!canSubmit) return;

		// Update the document selection
		await matrix.updateDocumentSelection(selectedRows, selectedColumns);

		dispatch('submit');
		handleClose();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleClose();
		}
	}

	function handleOpenInsight(opt: RowOption | ColumnOption, type: 'row' | 'column') {
		if (!opt.articulated_insight) return;
		selectedInsight = opt.articulated_insight;
		selectedOptionLabel = opt.label;
		selectedOptionType = type;
		showInsightPopup = true;
	}

	function handleCloseInsight() {
		showInsightPopup = false;
		selectedInsight = null;
	}
</script>

{#if open}
	<div
		class="popup-overlay"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="presentation"
		tabindex="-1"
	>
		<div
			class="context-popup"
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			aria-modal="true"
			aria-labelledby="context-title"
		>
			<div class="popup-header">
				<h3 id="context-title">Context Control</h3>
				<button class="close-btn" on:click={handleClose} aria-label="Close">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="20"
						height="20"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="M18 6 6 18" />
						<path d="m6 6 12 12" />
					</svg>
				</button>
			</div>

			<!-- Document Tabs -->
			<!-- Only show documents with full data (100 cells) -->
			{#if fullDataDocuments.length > 0}
				<div class="document-tabs-container">
					<div class="document-tabs">
						{#each fullDataDocuments as doc (doc.id)}
							<button
								class="document-tab"
								class:active={doc.id === $activeDocumentId}
								on:click={() => handleDocumentTabClick(doc.id)}
								title={doc.description}
							>
								<span class="tab-name">{doc.name}</span>
							</button>
						{/each}

						<!-- No + button here - generate from Matrix tab instead -->
					</div>
				</div>

				<!-- Document Description -->
				{#if $activeDocument?.description}
					<div class="document-description">
						{$activeDocument.description}
					</div>
				{/if}
			{/if}

			<div class="popup-body">
				<div class="selection-info">
					<span class="selection-count" class:complete={canSubmit}>
						{selectedRowCount}/5 drivers, {selectedColCount}/5 outcomes
					</span>
					<span class="selection-hint">{canSubmit ? 'Ready to apply' : 'Deselect one to swap with another'}</span>
				</div>

				{#if hasOptions}
					<div class="options-sections">
						<!-- Drivers (internally rows) -->
						<div class="options-section">
							<h4 class="section-title">Drivers ({visibleRowIndices.length} of {rowOptions.length})</h4>
							<div class="titles-list">
								{#each visibleRowIndices as idx (`row-${idx}`)}
									{@const opt = rowOptions[idx]}
									{@const isSelected = selectedRows.includes(idx)}
									{@const canDeselect = showExtraDrivers && selectedRows.length > 5}
									{@const canSelect = selectedRows.length < 5}
									{@const canToggle = isSelected ? canDeselect : canSelect}
									{@const hasInsight = !!opt?.articulated_insight}
									{#if opt}
										<div class="title-item-wrapper">
											<button
												class="title-item"
												class:selected={isSelected}
												class:disabled={!canToggle}
												on:click={() => handleToggleRow(idx)}
											>
												<div class="title-checkbox" class:checked={isSelected}>
													{#if isSelected}
														<svg
															xmlns="http://www.w3.org/2000/svg"
															width="14"
															height="14"
															viewBox="0 0 24 24"
															fill="none"
															stroke="currentColor"
															stroke-width="3"
														>
															<polyline points="20 6 9 17 4 12" />
														</svg>
													{/if}
												</div>
												<div class="title-content">
													<span class="title-text">{opt.label}</span>
													{#if opt.articulated_insight?.title}
														<span class="title-insight">{opt.articulated_insight.title}</span>
													{/if}
												</div>
											</button>
											{#if hasInsight}
												<button
													class="insight-expand-btn"
													on:click|stopPropagation={() => handleOpenInsight(opt, 'row')}
													title="View full insight"
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														width="16"
														height="16"
														viewBox="0 0 24 24"
														fill="none"
														stroke="currentColor"
														stroke-width="2"
														stroke-linecap="round"
														stroke-linejoin="round"
													>
														<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
														<polyline points="15 3 21 3 21 9" />
														<line x1="10" y1="14" x2="21" y2="3" />
													</svg>
												</button>
											{/if}
										</div>
									{/if}
								{/each}
							</div>
							{#if hasExtraDrivers}
								<button class="show-more-btn" on:click={handleShowExtraDrivers}>
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<path d="M12 5v14M5 12h14"/>
									</svg>
									Show 5 More Drivers
								</button>
							{/if}
						</div>

						<!-- Outcomes (internally columns) -->
						<div class="options-section">
							<h4 class="section-title">Outcomes ({visibleColIndices.length} of {columnOptions.length})</h4>
							<div class="titles-list">
								{#each visibleColIndices as idx (`col-${idx}`)}
									{@const opt = columnOptions[idx]}
									{@const isSelected = selectedColumns.includes(idx)}
									{@const canDeselect = showExtraOutcomes && selectedColumns.length > 5}
									{@const canSelect = selectedColumns.length < 5}
									{@const canToggle = isSelected ? canDeselect : canSelect}
									{@const hasInsight = !!opt?.articulated_insight}
									{#if opt}
										<div class="title-item-wrapper">
											<button
												class="title-item"
												class:selected={isSelected}
												class:disabled={!canToggle}
												on:click={() => handleToggleColumn(idx)}
											>
												<div class="title-checkbox" class:checked={isSelected}>
													{#if isSelected}
														<svg
															xmlns="http://www.w3.org/2000/svg"
															width="14"
															height="14"
															viewBox="0 0 24 24"
															fill="none"
															stroke="currentColor"
															stroke-width="3"
														>
															<polyline points="20 6 9 17 4 12" />
														</svg>
													{/if}
												</div>
												<div class="title-content">
													<span class="title-text">{opt.label}</span>
													{#if opt.articulated_insight?.title}
														<span class="title-insight">{opt.articulated_insight.title}</span>
													{/if}
												</div>
											</button>
											{#if hasInsight}
												<button
													class="insight-expand-btn"
													on:click|stopPropagation={() => handleOpenInsight(opt, 'column')}
													title="View full insight"
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														width="16"
														height="16"
														viewBox="0 0 24 24"
														fill="none"
														stroke="currentColor"
														stroke-width="2"
														stroke-linecap="round"
														stroke-linejoin="round"
													>
														<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
														<polyline points="15 3 21 3 21 9" />
														<line x1="10" y1="14" x2="21" y2="3" />
													</svg>
												</button>
											{/if}
										</div>
									{/if}
								{/each}
							</div>
							{#if hasExtraOutcomes}
								<button class="show-more-btn" on:click={handleShowExtraOutcomes}>
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<path d="M12 5v14M5 12h14"/>
									</svg>
									Show 5 More Outcomes
								</button>
							{/if}
						</div>
					</div>
				{:else}
					<div class="no-options-notice">
						No context options available yet. Send a message to generate matrix data.
					</div>
				{/if}
			</div>

			<div class="popup-footer">
				<Button variant="ghost" on:click={handleClose}>Cancel</Button>
				<Button variant="primary" on:click={handleSubmit} disabled={!canSubmit}>
					Apply Context
				</Button>
			</div>
		</div>
	</div>
{/if}

<!-- Insight Popup (nested, higher z-index) -->
<InsightPopup
	bind:open={showInsightPopup}
	insight={selectedInsight}
	optionLabel={selectedOptionLabel}
	optionType={selectedOptionType}
	on:close={handleCloseInsight}
/>

<style>
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

	.context-popup {
		width: 100%;
		max-width: 600px;
		max-height: 85vh;
		display: flex;
		flex-direction: column;
		background: var(--color-field-surface);
		border-radius: 1rem;
		border: 1px solid var(--color-veil-thin);
		box-shadow: var(--shadow-elevated);
		overflow: hidden;
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.popup-header h3 {
		font-size: 1.125rem;
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

	/* Document Tabs */
	.document-tabs-container {
		padding: 0.75rem 1.25rem 0;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.document-tabs {
		display: flex;
		gap: 0.25rem;
		overflow-x: auto;
		padding-bottom: 0.75rem;
	}

	.document-tab {
		padding: 0.5rem 1rem;
		background: var(--color-field-depth);
		border: 1px solid transparent;
		border-radius: 0.5rem 0.5rem 0 0;
		font-size: 0.8125rem;
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
		background: rgba(15, 23, 42, 0.2);
		border-color: var(--color-primary-700);
	}

	.document-tab.active {
		background: var(--color-primary-100);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
	}

	[data-theme='dark'] .document-tab.active {
		background: rgba(15, 23, 42, 0.3);
		color: var(--color-primary-300);
	}

	.tab-name {
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.add-document-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-veil-thin);
		border-radius: 0.5rem;
		color: var(--color-primary-600);
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.add-document-btn:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		border-style: solid;
	}

	[data-theme='dark'] .add-document-btn {
		color: var(--color-primary-400);
	}

	[data-theme='dark'] .add-document-btn:hover:not(:disabled) {
		background: rgba(15, 23, 42, 0.2);
	}

	.add-document-btn:disabled {
		opacity: 0.7;
		cursor: wait;
	}

	.document-description {
		padding: 0.75rem 1.25rem;
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
		line-height: 1.5;
		background: var(--color-field-depth);
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.popup-body {
		flex: 1;
		padding: 1rem 1.25rem;
		overflow-y: auto;
	}

	.selection-info {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.selection-count {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-manifest);
	}

	.selection-count.complete {
		color: #059669;
	}

	[data-theme='dark'] .selection-count.complete {
		color: #34d399;
	}

	.selection-hint {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	.options-sections {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.options-section {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.section-title {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-manifest);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.titles-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.show-more-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		margin-top: 0.75rem;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-primary-400);
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-primary-600);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.show-more-btn:hover {
		background: var(--color-primary-50);
		border-style: solid;
	}

	[data-theme='dark'] .show-more-btn {
		color: var(--color-primary-400);
	}

	[data-theme='dark'] .show-more-btn:hover {
		background: rgba(15, 23, 42, 0.2);
	}

	.title-item-wrapper {
		display: flex;
		align-items: stretch;
		gap: 0.5rem;
	}

	.insight-expand-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		color: var(--color-primary-500);
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.insight-expand-btn:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		color: var(--color-primary-600);
	}

	[data-theme='dark'] .insight-expand-btn:hover {
		background: rgba(15, 23, 42, 0.2);
		color: var(--color-primary-300);
	}

	.title-item {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid transparent;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
		flex: 1;
		min-width: 0;
	}

	.title-item:hover:not(.disabled) {
		border-color: var(--color-primary-400);
	}

	.title-item.selected {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	[data-theme='dark'] .title-item.selected {
		background: rgba(15, 23, 42, 0.2);
	}

	.title-item.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.title-checkbox {
		width: 20px;
		height: 20px;
		border: 2px solid var(--color-veil-thin);
		border-radius: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		transition: all 0.15s ease;
	}

	.title-checkbox.checked {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: white;
	}

	.title-content {
		flex: 1;
		min-width: 0;
	}

	.title-text {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.title-insight {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		margin-top: 0.25rem;
		line-height: 1.4;
	}

	.no-options-notice {
		text-align: center;
		padding: 2rem 1rem;
		font-size: 0.875rem;
		color: var(--color-text-whisper);
		background: var(--color-field-depth);
		border-radius: 0.5rem;
		border: 1px dashed var(--color-veil-thin);
	}

	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1rem 1.25rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}
</style>
