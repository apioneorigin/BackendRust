<script lang="ts">
	/**
	 * ContextControlPopup - Unified context control for matrix dimensions
	 *
	 * Shows all available row and column options (up to 40 total: 20 rows + 20 columns).
	 * User sees context titles without knowing which are rows vs columns.
	 * User selects exactly 5 rows and 5 columns for display.
	 *
	 * Features:
	 * - Shows all context titles from allRowOptions and allColumnOptions
	 * - Each title has an insight explaining why it was generated
	 * - User can select/deselect (must have exactly 5 of each type)
	 * - Max 3-word phrase titles
	 */

	import { createEventDispatcher } from 'svelte';
	import { matrix, isLoadingOptions, chat } from '$lib/stores';
	import { Button, Spinner } from '$lib/components/ui';
	import { api } from '$utils/api';

	export let open = false;

	const dispatch = createEventDispatcher<{
		close: void;
		submit: void;
	}>();

	// Combined context titles from rows and columns
	interface ContextTitle {
		index: number;  // Original index in allRowOptions or allColumnOptions
		title: string;
		insight: string;
		type: 'row' | 'column'; // Internal tracking, not shown to user
		selected: boolean;
	}

	let contextTitles: ContextTitle[] = [];

	// Build combined context titles from all available options
	$: {
		const rowTitles = ($matrix.allRowOptions || []).map((opt, idx) => ({
			index: idx,
			title: opt.label,
			insight: opt.insight || '',
			type: 'row' as const,
			selected: $matrix.selectedRowIndices?.includes(idx) ?? idx < 5
		}));

		const colTitles = ($matrix.allColumnOptions || []).map((opt, idx) => ({
			index: idx,
			title: opt.label,
			insight: opt.insight || '',
			type: 'column' as const,
			selected: $matrix.selectedColumnIndices?.includes(idx) ?? idx < 5
		}));

		contextTitles = [...rowTitles, ...colTitles];
	}

	$: selectedRowCount = contextTitles.filter(t => t.type === 'row' && t.selected).length;
	$: selectedColCount = contextTitles.filter(t => t.type === 'column' && t.selected).length;
	$: totalSelected = selectedRowCount + selectedColCount;
	$: canSubmit = selectedRowCount === 5 && selectedColCount === 5;
	$: hasOptions = contextTitles.length > 0;

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleToggleTitle(index: number, type: 'row' | 'column') {
		const titleIdx = contextTitles.findIndex(t => t.index === index && t.type === type);
		if (titleIdx === -1) return;

		const title = contextTitles[titleIdx];
		const sameTypeSelected = contextTitles.filter(t => t.type === type && t.selected).length;

		// Check if we can toggle
		if (title.selected) {
			// Can only deselect if more than 5 of this type selected
			if (sameTypeSelected <= 5) return;
		} else {
			// Can only select if fewer than 5 of this type selected
			if (sameTypeSelected >= 5) return;
		}

		// Toggle selection
		contextTitles = contextTitles.map((t, i) =>
			i === titleIdx ? { ...t, selected: !t.selected } : t
		);
	}

	async function handleSubmit() {
		if (!canSubmit) return;

		// Extract selected row and column indices
		const selectedRowIndices = contextTitles
			.filter(t => t.type === 'row' && t.selected)
			.map(t => t.index);
		const selectedColumnIndices = contextTitles
			.filter(t => t.type === 'column' && t.selected)
			.map(t => t.index);

		// Update matrix display with new selection (local state)
		matrix.updateDisplayedSelection(selectedRowIndices, selectedColumnIndices);

		// Persist selection to backend
		const conversationId = $chat.currentConversation?.id;
		if (conversationId) {
			try {
				await api.patch(`/api/matrix/${conversationId}/selection`, {
					selected_rows: selectedRowIndices,
					selected_columns: selectedColumnIndices
				});
			} catch (error) {
				console.error('Failed to persist matrix selection:', error);
				// Non-critical - local state is already updated
			}
		}

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

			<div class="popup-body">
				<div class="selection-info">
					<span class="selection-count" class:complete={canSubmit}>
						{selectedRowCount}/5 rows, {selectedColCount}/5 columns
					</span>
					<span class="selection-hint">Select 5 of each type to shape your matrix view</span>
				</div>

				{#if hasOptions}
					<div class="titles-list">
						{#each contextTitles as ctx (`${ctx.type}-${ctx.index}`)}
							{@const sameTypeSelected = contextTitles.filter(t => t.type === ctx.type && t.selected).length}
							{@const canToggle = ctx.selected ? sameTypeSelected > 5 : sameTypeSelected < 5}
							<button
								class="title-item"
								class:selected={ctx.selected}
								class:disabled={!canToggle}
								on:click={() => canToggle && handleToggleTitle(ctx.index, ctx.type)}
								disabled={!canToggle}
							>
								<div class="title-checkbox" class:checked={ctx.selected}>
									{#if ctx.selected}
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
									<span class="title-text">{ctx.title}</span>
									{#if ctx.insight}
										<span class="title-insight">{ctx.insight}</span>
									{/if}
								</div>
							</button>
						{/each}
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
		max-width: 550px;
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

	.generate-more-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem;
		margin-top: 1rem;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		color: var(--color-primary-600);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.generate-more-btn:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	.generate-more-btn:disabled {
		opacity: 0.7;
		cursor: wait;
	}

	[data-theme='dark'] .generate-more-btn {
		color: var(--color-primary-400);
	}

	[data-theme='dark'] .generate-more-btn:hover:not(:disabled) {
		background: rgba(15, 76, 117, 0.2);
	}

	.options-limit-notice {
		text-align: center;
		padding: 0.75rem;
		margin-top: 1rem;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		background: var(--color-field-depth);
		border-radius: 0.5rem;
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
