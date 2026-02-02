<script lang="ts">
	/**
	 * ContextControlPopup - Unified context control for matrix dimensions
	 *
	 * NEW ARCHITECTURE:
	 * - Shows document tabs at top (each with its own 10x10 matrix)
	 * - "+" button at right of last tab to generate more documents via gpt-5.2
	 * - Per-document row/column selection (10 options each, select 5)
	 * - Each document has ~20 word description
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
	import { Button, Spinner } from '$lib/components/ui';

	export let open = false;

	const dispatch = createEventDispatcher<{
		close: void;
		submit: void;
	}>();

	// Local selection state for the active document
	let selectedRows: number[] = [];
	let selectedColumns: number[] = [];

	// Sync local selection with active document
	$: if ($activeDocument?.matrix_data) {
		selectedRows = [...($activeDocument.matrix_data.selected_rows || [0, 1, 2, 3, 4])];
		selectedColumns = [...($activeDocument.matrix_data.selected_columns || [0, 1, 2, 3, 4])];
	}

	$: rowOptions = $activeDocument?.matrix_data?.row_options || [];
	$: columnOptions = $activeDocument?.matrix_data?.column_options || [];

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
			// Can only deselect if more than 5 selected
			if (selectedRows.length <= 5) return;
			selectedRows = selectedRows.filter(i => i !== index);
		} else {
			// Can only select if fewer than 5 selected
			if (selectedRows.length >= 5) return;
			selectedRows = [...selectedRows, index];
		}
	}

	function handleToggleColumn(index: number) {
		if (selectedColumns.includes(index)) {
			// Can only deselect if more than 5 selected
			if (selectedColumns.length <= 5) return;
			selectedColumns = selectedColumns.filter(i => i !== index);
		} else {
			// Can only select if fewer than 5 selected
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
			{#if $documents.length > 0}
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

						<!-- Generate More Documents Button -->
						<button
							class="add-document-btn"
							on:click={handleGenerateMoreDocuments}
							disabled={$isGeneratingMoreDocuments}
							title="Generate 3 more documents"
						>
							{#if $isGeneratingMoreDocuments}
								<Spinner size="sm" />
							{:else}
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
									<path d="M12 5v14" />
									<path d="M5 12h14" />
								</svg>
							{/if}
						</button>
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
						{selectedRowCount}/5 rows, {selectedColCount}/5 columns
					</span>
					<span class="selection-hint">Select 5 of each type to shape your matrix view</span>
				</div>

				{#if hasOptions}
					<div class="options-sections">
						<!-- Row Options -->
						<div class="options-section">
							<h4 class="section-title">Rows ({rowOptions.length} available)</h4>
							<div class="titles-list">
								{#each rowOptions as opt, idx (`row-${idx}`)}
									{@const isSelected = selectedRows.includes(idx)}
									{@const canToggle = isSelected ? selectedRows.length > 5 : selectedRows.length < 5}
									<button
										class="title-item"
										class:selected={isSelected}
										class:disabled={!canToggle}
										on:click={() => canToggle && handleToggleRow(idx)}
										disabled={!canToggle}
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
											{#if opt.insight}
												<span class="title-insight">{opt.insight}</span>
											{/if}
										</div>
									</button>
								{/each}
							</div>
						</div>

						<!-- Column Options -->
						<div class="options-section">
							<h4 class="section-title">Columns ({columnOptions.length} available)</h4>
							<div class="titles-list">
								{#each columnOptions as opt, idx (`col-${idx}`)}
									{@const isSelected = selectedColumns.includes(idx)}
									{@const canToggle = isSelected ? selectedColumns.length > 5 : selectedColumns.length < 5}
									<button
										class="title-item"
										class:selected={isSelected}
										class:disabled={!canToggle}
										on:click={() => canToggle && handleToggleColumn(idx)}
										disabled={!canToggle}
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
											{#if opt.insight}
												<span class="title-insight">{opt.insight}</span>
											{/if}
										</div>
									</button>
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
		background: rgba(15, 76, 117, 0.2);
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
		width: 100%;
	}

	.title-item:hover:not(.disabled) {
		border-color: var(--color-primary-400);
	}

	.title-item.selected {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	[data-theme='dark'] .title-item.selected {
		background: rgba(15, 76, 117, 0.2);
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
