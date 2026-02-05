<script lang="ts">
	/**
	 * ContextControlPopup - Unified context control for matrix dimensions
	 *
	 * ARCHITECTURE:
	 * - Shows ALL documents (LLM-generated stubs and fully populated)
	 * - Per-document row/column selection (10 options each, select 5)
	 * - Each document has ~20 word description
	 * - Clickable titles open InsightPopup when articulated_insight is available
	 */

	import { createEventDispatcher } from 'svelte';
	import {
		matrix,
		matrixDocuments,
		activeDocumentId,
		activeDocument,
		addToast
	} from '$lib/stores';
	import type { ArticulatedInsight, RowOption, ColumnOption, DocumentPreview } from '$lib/stores/matrix';
	import { Button } from '$lib/components/ui';
	import InsightPopup from './InsightPopup.svelte';

	export let open = false;
	export let model = 'claude-opus-4-5-20251101';

	// Document creation state
	let previews: DocumentPreview[] = [];
	let selectedPreviews: Set<string> = new Set();
	let isLoadingPreviews = false;
	let isAddingDocuments = false;
	let showPreviewPanel = false;

	async function handleGeneratePreviews() {
		isLoadingPreviews = true;
		showPreviewPanel = true;
		previews = [];
		selectedPreviews = new Set();
		try {
			previews = await matrix.previewDocuments(model);
		} finally {
			isLoadingPreviews = false;
		}
	}

	function handleTogglePreview(tempId: string) {
		const next = new Set(selectedPreviews);
		if (next.has(tempId)) next.delete(tempId);
		else next.add(tempId);
		selectedPreviews = next;
	}

	async function handleAddSelected() {
		if (selectedPreviews.size === 0) return;
		isAddingDocuments = true;
		try {
			await matrix.addDocuments([...selectedPreviews], model);
			showPreviewPanel = false;
			previews = [];
			selectedPreviews = new Set();
		} finally {
			isAddingDocuments = false;
		}
	}

	function handleCancelPreviews() {
		showPreviewPanel = false;
		previews = [];
		selectedPreviews = new Set();
	}

	// Insight popup state
	let showInsightPopup = false;
	let selectedInsight: ArticulatedInsight | null = null;
	let selectedOptionLabel = '';
	let selectedOptionType: 'row' | 'column' = 'row';
	let generatingInsights = false;

	const dispatch = createEventDispatcher<{
		close: void;
		submit: void;
	}>();

	// Local selection state for the active document
	let selectedRows: number[] = [];
	let selectedColumns: number[] = [];

	// Sync local selection with active document
	// Use ?? (not ||) because Pydantic may serialize as JSON null
	$: if ($activeDocument?.matrix_data) {
		selectedRows = [...($activeDocument.matrix_data.selected_rows ?? [0, 1, 2, 3, 4])];
		selectedColumns = [...($activeDocument.matrix_data.selected_columns ?? [0, 1, 2, 3, 4])];
	}

	$: rowOptions = $activeDocument?.matrix_data?.row_options ?? [];
	$: columnOptions = $activeDocument?.matrix_data?.column_options ?? [];

	// Show all options — user needs to see everything to make swap decisions
	$: visibleRowIndices = rowOptions.map((_: any, i: number) => i);
	$: visibleColIndices = columnOptions.map((_: any, i: number) => i);

	$: selectedRowCount = selectedRows.length;
	$: selectedColCount = selectedColumns.length;
	$: canSubmit = selectedRowCount === 5 && selectedColCount === 5;
	$: hasOptions = rowOptions.length > 0 || columnOptions.length > 0;

	function handleClose() {
		open = false;
		dispatch('close');
	}

	let deletingDocId: string | null = null;

	function handleDocumentTabClick(docId: string) {
		matrix.setActiveDocument(docId);
	}

	async function handleDeleteDocument(docId: string) {
		if ($matrixDocuments.length <= 1) return;
		deletingDocId = docId;
		try {
			await matrix.deleteDocument(docId);
		} finally {
			deletingDocId = null;
		}
	}

	function handleToggleRow(index: number) {
		if (selectedRows.includes(index)) {
			selectedRows = selectedRows.filter(i => i !== index);
		} else {
			if (selectedRows.length >= 5) return;
			selectedRows = [...selectedRows, index];
		}
	}

	function handleToggleColumn(index: number) {
		if (selectedColumns.includes(index)) {
			selectedColumns = selectedColumns.filter(i => i !== index);
		} else {
			if (selectedColumns.length >= 5) return;
			selectedColumns = [...selectedColumns, index];
		}
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

	async function handleOpenInsight(opt: RowOption | ColumnOption, type: 'row' | 'column') {
		selectedOptionLabel = opt.label;
		selectedOptionType = type;

		if (opt.articulated_insight) {
			selectedInsight = opt.articulated_insight;
			showInsightPopup = true;
			return;
		}

		// Trigger on-demand generation of all missing insights
		if (!opt.insight_title) return;

		const optionsList = type === 'row' ? rowOptions : columnOptions;
		const insightIndex = optionsList.indexOf(opt) + (type === 'column' ? 10 : 0);

		generatingInsights = true;
		try {
			const updatedDoc = await matrix.generateInsights(insightIndex, model);
			if (updatedDoc) {
				const options = type === 'row'
					? updatedDoc.matrix_data.row_options
					: updatedDoc.matrix_data.column_options;
				const idx = type === 'row' ? insightIndex : insightIndex - 10;
				const updatedOpt = options[idx];
				if (updatedOpt?.articulated_insight) {
					selectedInsight = updatedOpt.articulated_insight;
					showInsightPopup = true;
				}
			}
		} catch (error: any) {
			console.error('Failed to generate insights:', error);
			addToast('error', error.message || 'Failed to generate insight');
		} finally {
			generatingInsights = false;
		}
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
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
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
			{#if $matrixDocuments.length > 0}
				<div class="document-tabs-container">
					<div class="document-tabs">
						{#each $matrixDocuments as doc (doc.id)}
							<button
								class="document-tab"
								class:active={doc.id === $activeDocumentId}
								on:click={() => handleDocumentTabClick(doc.id)}
								title={doc.description}
							>
								<span class="tab-name">{doc.name}</span>
								{#if $matrixDocuments.length > 1}
									<span
										class="tab-delete-x"
										role="button"
										tabindex="-1"
										on:click|stopPropagation={() => handleDeleteDocument(doc.id)}
										title="Delete document"
									>&times;</span>
								{/if}
							</button>
						{/each}
						<button
							class="document-tab add-tab"
							on:click={handleGeneratePreviews}
							disabled={isLoadingPreviews}
							title="Add new document"
						>+</button>
					</div>
				</div>

				{#if showPreviewPanel}
					<div class="preview-panel">
						{#if isLoadingPreviews}
							<div class="preview-loading">Generating previews...</div>
						{:else if previews.length > 0}
							<div class="preview-list">
								{#each previews as preview (preview.tempId)}
									<button
										class="preview-card"
										class:selected={selectedPreviews.has(preview.tempId)}
										on:click={() => handleTogglePreview(preview.tempId)}
									>
										<div class="preview-check" class:checked={selectedPreviews.has(preview.tempId)}>
											{#if selectedPreviews.has(preview.tempId)}
												<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12" /></svg>
											{/if}
										</div>
										<div class="preview-info">
											<span class="preview-name">{preview.name}</span>
											<span class="preview-titles">{preview.insightTitles?.slice(0, 4).join(' · ')}</span>
										</div>
									</button>
								{/each}
							</div>
							<div class="preview-actions">
								<Button variant="ghost" size="sm" on:click={handleCancelPreviews}>Cancel</Button>
								<Button variant="primary" size="sm" on:click={handleAddSelected} disabled={selectedPreviews.size === 0 || isAddingDocuments}>
									{isAddingDocuments ? 'Adding...' : `Add ${selectedPreviews.size}`}
								</Button>
							</div>
						{:else}
							<div class="preview-loading">No previews generated.</div>
						{/if}
					</div>
				{/if}

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
					<span class="selection-hint">{canSubmit ? 'Ready to apply' : 'Select exactly 5 drivers and 5 outcomes to apply'}</span>
				</div>

				{#if hasOptions}
					<div class="options-sections">
						<!-- Drivers (internally rows) -->
						<div class="options-section">
							<h4 class="section-title">Drivers ({selectedRowCount}/5 selected)</h4>
							<div class="titles-list">
								{#each visibleRowIndices as idx (`row-${idx}`)}
									{@const opt = rowOptions[idx]}
									{@const isSelected = selectedRows.includes(idx)}
									{@const canSelect = selectedRows.length < 5}
									{@const canToggle = isSelected || canSelect}
									{@const hasInsight = !!(opt?.insight_title || opt?.articulated_insight)}
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
													<span class="title-text">{opt.insight_title || opt.label}</span>
												</div>
											</button>
											{#if hasInsight}
												<button
													class="insight-expand-btn"
													class:loading={generatingInsights}
													disabled={generatingInsights}
													on:click|stopPropagation={() => handleOpenInsight(opt, 'row')}
													title={opt.articulated_insight ? 'View full insight' : 'Generate insight'}
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
						</div>

						<!-- Outcomes (internally columns) -->
						<div class="options-section">
							<h4 class="section-title">Outcomes ({selectedColCount}/5 selected)</h4>
							<div class="titles-list">
								{#each visibleColIndices as idx (`col-${idx}`)}
									{@const opt = columnOptions[idx]}
									{@const isSelected = selectedColumns.includes(idx)}
									{@const canSelect = selectedColumns.length < 5}
									{@const canToggle = isSelected || canSelect}
									{@const hasInsight = !!(opt?.insight_title || opt?.articulated_insight)}
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
													<span class="title-text">{opt.insight_title || opt.label}</span>
												</div>
											</button>
											{#if hasInsight}
												<button
													class="insight-expand-btn"
													class:loading={generatingInsights}
													disabled={generatingInsights}
													on:click|stopPropagation={() => handleOpenInsight(opt, 'column')}
													title={opt.articulated_insight ? 'View full insight' : 'Generate insight'}
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
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.75rem;
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

	.document-tab.active {
		background: var(--color-primary-100);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
	}

	.document-tab.add-tab {
		padding: 0.5rem 0.75rem;
		font-size: 1rem;
		font-weight: 400;
		color: var(--color-text-whisper);
		border: 1px dashed var(--color-veil-thin);
	}

	.document-tab.add-tab:hover {
		color: var(--color-primary-600);
		border-color: var(--color-primary-400);
	}

	.tab-name {
		max-width: 130px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.tab-delete-x {
		font-size: 1rem;
		line-height: 1;
		color: var(--color-text-whisper);
		padding: 0 0.125rem;
		border-radius: 0.25rem;
		transition: color 0.1s ease;
	}

	.tab-delete-x:hover {
		color: #ef4444;
	}

	/* Preview panel */
	.preview-panel {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.preview-loading {
		text-align: center;
		padding: 1rem;
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
	}

	.preview-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.preview-card {
		display: flex;
		align-items: flex-start;
		gap: 0.625rem;
		padding: 0.625rem 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid transparent;
		border-radius: 0.5rem;
		cursor: pointer;
		text-align: left;
		transition: all 0.15s ease;
	}

	.preview-card:hover {
		border-color: var(--color-primary-200);
	}

	.preview-card.selected {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	.preview-check {
		width: 18px;
		height: 18px;
		border: 2px solid var(--color-veil-thin);
		border-radius: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		margin-top: 1px;
		transition: all 0.15s ease;
	}

	.preview-check.checked {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: white;
	}

	.preview-info {
		flex: 1;
		min-width: 0;
	}

	.preview-name {
		display: block;
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.preview-titles {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		margin-top: 0.125rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.preview-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 0.625rem;
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

	.insight-expand-btn.loading {
		opacity: 0.5;
		cursor: wait;
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
