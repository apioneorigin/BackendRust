<script lang="ts">
	/**
	 * ContextControlPopup - Unified context control for matrix dimensions
	 *
	 * Combines row (causation) and column (effect) selection into a single popup.
	 * User sees 10 context titles without knowing which are rows vs columns.
	 * Backend tracks type internally and determines what to regenerate.
	 *
	 * Features:
	 * - Shows 10 context titles (5 rows + 5 columns combined)
	 * - Each title has an insight explaining why it was generated
	 * - User can select/deselect titles
	 * - Generate more titles button (backend determines row vs column)
	 * - Max 10-word phrase titles
	 */

	import { createEventDispatcher } from 'svelte';
	import { matrix, isLoadingOptions } from '$lib/stores';
	import { Button, Spinner } from '$lib/components/ui';

	export let open = false;

	const dispatch = createEventDispatcher<{
		close: void;
		submit: void;
	}>();

	// Combined context titles from rows and columns
	interface ContextTitle {
		id: string;
		title: string;
		insight: string;
		type: 'row' | 'column'; // Internal tracking, not shown to user
		selected: boolean;
	}

	let contextTitles: ContextTitle[] = [];

	// Build combined context titles from matrix store
	$: {
		const rowTitles = $matrix.rowHeaders.map((title, idx) => ({
			id: `row-${idx}`,
			title,
			insight: $matrix.rowInsights?.[idx] || '',
			type: 'row' as const,
			selected: true
		}));

		const colTitles = $matrix.columnHeaders.map((title, idx) => ({
			id: `col-${idx}`,
			title,
			insight: $matrix.columnInsights?.[idx] || '',
			type: 'column' as const,
			selected: true
		}));

		contextTitles = [...rowTitles, ...colTitles];
	}

	$: selectedRowCount = contextTitles.filter(t => t.type === 'row' && t.selected).length;
	$: selectedColCount = contextTitles.filter(t => t.type === 'column' && t.selected).length;
	$: totalSelected = selectedRowCount + selectedColCount;
	$: canSubmit = selectedRowCount === 5 && selectedColCount === 5;
	$: canGenerateMore = contextTitles.length < 20; // Max 10 rows + 10 columns

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleToggleTitle(id: string) {
		const title = contextTitles.find(t => t.id === id);
		if (!title) return;

		// Check if we can deselect (need at least 5 of each type)
		if (title.selected) {
			const sameTypeSelected = contextTitles.filter(t => t.type === title.type && t.selected).length;
			if (sameTypeSelected <= 5) {
				// Can't deselect - would go below 5
				return;
			}
		} else {
			// Check if we can select (max 5 of each type active)
			const sameTypeSelected = contextTitles.filter(t => t.type === title.type && t.selected).length;
			if (sameTypeSelected >= 5) {
				// Can't select - already have 5
				return;
			}
		}

		contextTitles = contextTitles.map(t =>
			t.id === id ? { ...t, selected: !t.selected } : t
		);
	}

	async function handleGenerateMore() {
		if (!canGenerateMore) return;

		// Determine what type needs more options based on current selection
		const rowCount = contextTitles.filter(t => t.type === 'row').length;
		const colCount = contextTitles.filter(t => t.type === 'column').length;

		// Generate for whichever type has fewer options, or rows if equal
		const generateType = rowCount <= colCount ? 'row' : 'column';

		await matrix.generateMoreContextTitles(generateType);
	}

	function handleSubmit() {
		if (!canSubmit) return;

		// Extract selected rows and columns
		const selectedRows = contextTitles
			.filter(t => t.type === 'row' && t.selected)
			.map(t => t.title);
		const selectedCols = contextTitles
			.filter(t => t.type === 'column' && t.selected)
			.map(t => t.title);

		// Update matrix with selected context
		matrix.updateContextSelection(selectedRows, selectedCols);

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
						{totalSelected}/10 active
					</span>
					<span class="selection-hint">Select context dimensions to shape your matrix</span>
				</div>

				<div class="titles-list">
					{#each contextTitles as ctx (ctx.id)}
						{@const sameTypeSelected = contextTitles.filter(t => t.type === ctx.type && t.selected).length}
						{@const canToggle = ctx.selected ? sameTypeSelected > 5 : sameTypeSelected < 5}
						<button
							class="title-item"
							class:selected={ctx.selected}
							class:disabled={!canToggle}
							on:click={() => canToggle && handleToggleTitle(ctx.id)}
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

				{#if canGenerateMore}
					<button
						class="generate-more-btn"
						on:click={handleGenerateMore}
						disabled={$isLoadingOptions}
					>
						{#if $isLoadingOptions}
							<Spinner size="sm" />
							<span>Generating...</span>
						{:else}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="16"
								height="16"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M12 5v14" />
								<path d="M5 12h14" />
							</svg>
							<span>Generate More Context ({contextTitles.length}/20)</span>
						{/if}
					</button>
				{:else}
					<div class="options-limit-notice">
						Maximum context options reached (20/20)
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

	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1rem 1.25rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}
</style>
