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
	import { Button, ConfirmDialog } from '$lib/components/ui';
	import InsightPopup from './InsightPopup.svelte';

	export let open = false;
	export let model = 'claude-opus-4-5-20251101';

	// Document creation state
	let previews: DocumentPreview[] = [];
	let selectedPreviews: Set<string> = new Set();
	let isLoadingPreviews = false;
	let isAddingDocuments = false;
	let showPreviewPanel = false;
	let showConfirmGenerate = false;

	function handleClickAdd() {
		showConfirmGenerate = true;
	}

	async function handleConfirmGenerate() {
		showConfirmGenerate = false;
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

	function handleCancelGenerate() {
		showConfirmGenerate = false;
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
	let generatingInsightKey: string | null = null;

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
	$: viewedInsightIndices = $activeDocument?.matrix_data?.viewed_insight_indices ?? [];

	// Show all options — user needs to see everything to make swap decisions
	$: visibleRowIndices = rowOptions.map((_: any, i: number) => i);
	$: visibleColIndices = columnOptions.map((_: any, i: number) => i);

	$: selectedRowCount = selectedRows.length;
	$: selectedColCount = selectedColumns.length;
	$: canSubmit = selectedRowCount === 5 && selectedColCount === 5;
	$: hasOptions = rowOptions.length > 0 || columnOptions.length > 0;

	function handleClose() {
		open = false;
		showConfirmGenerate = false;
		showPreviewPanel = false;
		dispatch('close');
	}

	let deletingDocId: string | null = null;
	let showDeleteDocConfirm = false;
	let deleteDocId: string | null = null;

	function handleDocumentTabClick(docId: string) {
		matrix.setActiveDocument(docId);
	}

	function handleDeleteDocument(docId: string) {
		if ($matrixDocuments.length <= 1) return;
		deleteDocId = docId;
		showDeleteDocConfirm = true;
	}

	async function confirmDeleteDocument() {
		if (!deleteDocId) return;
		deletingDocId = deleteDocId;
		try {
			await matrix.deleteDocument(deleteDocId);
		} finally {
			deletingDocId = null;
			deleteDocId = null;
		}
	}

	function cancelDeleteDocument() {
		deleteDocId = null;
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

	async function handleOpenInsight(opt: RowOption | ColumnOption, type: 'row' | 'column', idx: number) {
		selectedOptionLabel = opt.label;
		selectedOptionType = type;

		const insightIndex = idx + (type === 'column' ? 10 : 0);

		// Already viewed and content exists — show directly (no backend call)
		if (viewedInsightIndices.includes(insightIndex) && opt.articulated_insight?.the_truth) {
			selectedInsight = opt.articulated_insight;
			showInsightPopup = true;
			return;
		}

		// Not yet viewed — call backend to generate (if needed) + mark as viewed
		if (!opt.insight_title) return;

		const key = `${type}-${idx}`;

		generatingInsightKey = key;
		try {
			const updatedDoc = await matrix.generateInsights(insightIndex, model);
			if (updatedDoc) {
				const options = type === 'row'
					? updatedDoc.matrix_data.row_options
					: updatedDoc.matrix_data.column_options;
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
			generatingInsightKey = null;
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
							<div
								class="document-tab"
								class:active={doc.id === $activeDocumentId}
								on:click={() => handleDocumentTabClick(doc.id)}
								on:keydown={(e) => e.key === 'Enter' && handleDocumentTabClick(doc.id)}
								role="tab"
								tabindex="0"
								title={doc.description}
							>
								<span class="tab-name">{doc.name}</span>
								{#if $matrixDocuments.length > 1}
									<button
										class="tab-delete-btn"
										on:click|stopPropagation={() => handleDeleteDocument(doc.id)}
										title="Delete document"
									>&times;</button>
								{/if}
							</div>
						{/each}
						<button
							class="document-tab add-tab"
							on:click={handleClickAdd}
							disabled={isLoadingPreviews || showConfirmGenerate}
							title="Add new document"
						>+</button>
					</div>
				</div>

				{#if showConfirmGenerate}
					<div class="confirm-generate-panel">
						<p class="confirm-text">Generate 3 new documents with unique perspectives? Each includes 10 drivers and 10 outcomes with insight titles. Cell data is generated separately per document.</p>
						<div class="confirm-actions">
							<Button variant="ghost" size="sm" on:click={handleCancelGenerate}>Cancel</Button>
							<Button variant="primary" size="sm" on:click={handleConfirmGenerate}>Generate</Button>
						</div>
					</div>
				{:else if showPreviewPanel}
					<div class="preview-panel">
						{#if isLoadingPreviews}
							<div class="preview-loading">
								<span>Generating previews...</span>
								<button class="inline-stop-btn llm-active" on:click={() => matrix.cancelPreview()} title="Stop">
									<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="6" width="12" height="12" rx="1" /></svg>
								</button>
							</div>
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

			<!-- Sticky selection status — never scrolls with options list -->
			<div class="selection-info">
				<span class="selection-count" class:complete={canSubmit}>
					{selectedRowCount}/5 drivers, {selectedColCount}/5 outcomes
				</span>
				<span class="selection-hint">{canSubmit ? 'Ready to apply' : 'Select exactly 5 drivers and 5 outcomes to apply'}</span>
			</div>

			<div class="popup-body">
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
									{@const isGenerated = viewedInsightIndices.includes(idx)}
									{@const isThisLoading = generatingInsightKey === `row-${idx}`}
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
														<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12" /></svg>
													{/if}
												</div>
												<div class="title-content">
													<span class="title-text">{opt.insight_title || opt.label}</span>
												</div>
											</button>
											{#if hasInsight}
												<button
													class="insight-expand-btn"
													class:loading={isThisLoading}
													class:llm-active={isThisLoading}
													class:generated={isGenerated}
													disabled={generatingInsightKey !== null && !isThisLoading}
													on:click|stopPropagation={() => isThisLoading ? matrix.cancelInsight() : handleOpenInsight(opt, 'row', idx)}
													title={isThisLoading ? 'Stop' : isGenerated ? 'View insight' : 'Generate insight'}
												>
													{#if isThisLoading}
														<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="6" width="12" height="12" rx="1" /></svg>
													{:else if isGenerated}
														<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" /><circle cx="12" cy="12" r="3" /></svg>
													{:else}
														<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>
													{/if}
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
									{@const isGenerated = viewedInsightIndices.includes(10 + idx)}
									{@const isThisLoading = generatingInsightKey === `column-${idx}`}
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
														<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12" /></svg>
													{/if}
												</div>
												<div class="title-content">
													<span class="title-text">{opt.insight_title || opt.label}</span>
												</div>
											</button>
											{#if hasInsight}
												<button
													class="insight-expand-btn"
													class:loading={isThisLoading}
													class:llm-active={isThisLoading}
													class:generated={isGenerated}
													disabled={generatingInsightKey !== null && !isThisLoading}
													on:click|stopPropagation={() => isThisLoading ? matrix.cancelInsight() : handleOpenInsight(opt, 'column', idx)}
													title={isThisLoading ? 'Stop' : isGenerated ? 'View insight' : 'Generate insight'}
												>
													{#if isThisLoading}
														<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="6" width="12" height="12" rx="1" /></svg>
													{:else if isGenerated}
														<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" /><circle cx="12" cy="12" r="3" /></svg>
													{:else}
														<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>
													{/if}
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

<ConfirmDialog
	bind:open={showDeleteDocConfirm}
	title="Delete Document"
	message="Are you sure you want to delete this document? The matrix data for this document will be permanently removed."
	confirmText="Delete"
	variant="danger"
	on:confirm={confirmDeleteDocument}
	on:cancel={cancelDeleteDocument}
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
		user-select: none;
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

	.tab-delete-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 18px;
		height: 18px;
		padding: 0;
		background: none;
		border: 1px solid transparent;
		border-radius: 50%;
		font-size: 0.875rem;
		line-height: 1;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.tab-delete-btn:hover {
		background: #fef2f2;
		border-color: #fecaca;
		color: #ef4444;
	}

	/* Confirmation panel for document generation */
	.confirm-generate-panel {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.confirm-text {
		font-size: 0.8125rem;
		color: var(--color-text-manifest);
		line-height: 1.5;
		margin: 0 0 0.625rem;
	}

	.confirm-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
	}

	/* Preview panel */
	.preview-panel {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.preview-loading {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 1rem;
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
	}

	.inline-stop-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		padding: 0;
		border: 1px solid transparent;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.15s ease;
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

	/* Sticky selection status bar — outside scrollable body */
	.selection-info {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.625rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		background: var(--color-field-surface);
		flex-shrink: 0;
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

	.popup-body {
		flex: 1;
		padding: 1rem 1.25rem;
		overflow-y: auto;
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
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.insight-expand-btn:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		color: var(--color-primary-600);
	}

	.insight-expand-btn.generated {
		color: var(--color-primary-500);
		border-color: var(--color-primary-200);
	}

	.insight-expand-btn.generated:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
	}

	.insight-expand-btn.loading {
		cursor: wait;
		color: var(--color-primary-500);
	}

	.insight-expand-btn:disabled:not(.loading) {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.insight-expand-btn .spinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
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
