<script lang="ts">
	/**
	 * InsightPopup - Displays articulated insights for matrix row/column options
	 *
	 * Enhanced structure:
	 * 1. Micro-moment (user's context) - Fly on the Wall
	 * 2. Distant anchor (far domain analogy)
	 * 3. Principle (universal law)
	 * 4. Installation (recognition + name + identity)
	 *
	 * Total: 200-300 words, displayed as continuous prose
	 */

	import { createEventDispatcher } from 'svelte';
	import type { ArticulatedInsight } from '$lib/stores/matrix';

	export let open = false;
	export let insight: ArticulatedInsight | null = null;
	export let optionLabel = '';
	export let optionType: 'row' | 'column' = 'row';

	const dispatch = createEventDispatcher<{
		close: void;
	}>();

	// Map internal types to user-friendly labels
	$: displayType = optionType === 'row' ? 'driver' : 'outcome';

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleClose();
		}
	}

	// Parse markdown bold (**text**) to HTML
	function parseBold(text: string): string {
		if (!text) return '';
		return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
	}
</script>

{#if open && insight}
	<div
		class="popup-overlay"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="presentation"
		tabindex="-1"
	>
		<div
			class="insight-popup"
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			aria-modal="true"
			aria-labelledby="insight-title"
		>
			<div class="popup-header">
				<div class="header-content">
					<span class="option-type-badge" class:driver={optionType === 'row'} class:outcome={optionType === 'column'}>
						{displayType}
					</span>
					<h3 id="insight-title">{insight.title || optionLabel}</h3>
				</div>
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
				<!-- Continuous prose insight - fully LLM-generated, no templates -->
				<article class="insight-prose">
					{#if insight.the_truth}
						<p>{@html parseBold(insight.the_truth)}</p>
					{/if}

					{#if insight.the_truth_law}
						<p>{@html parseBold(insight.the_truth_law)}</p>
					{/if}

					{#if insight.your_truth}
						<p>{@html parseBold(insight.your_truth)}</p>
					{/if}

					{#if insight.your_truth_revelation}
						<p>{@html parseBold(insight.your_truth_revelation)}</p>
					{/if}

					{#if insight.the_mark_name || insight.the_mark_prediction || insight.the_mark_identity}
						<p>
							{#if insight.the_mark_name}<span class="mark-name">{insight.the_mark_name}</span> {/if}{insight.the_mark_prediction || ''} {@html parseBold(insight.the_mark_identity || '')}
						</p>
					{/if}
				</article>
			</div>

			<div class="popup-footer">
				<button class="close-text-btn" on:click={handleClose}>Close</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.popup-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.6);
		backdrop-filter: blur(6px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 150;
		padding: 1rem;
	}

	.insight-popup {
		width: 100%;
		max-width: 640px;
		max-height: 85vh;
		display: flex;
		flex-direction: column;
		background: var(--color-field-surface);
		border-radius: 1rem;
		border: 1px solid var(--color-veil-thin);
		box-shadow: var(--shadow-elevated), 0 25px 50px -12px rgba(0, 0, 0, 0.25);
		overflow: hidden;
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid var(--color-veil-thin);
		background: var(--color-field-depth);
		flex-shrink: 0;
	}

	.header-content {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.option-type-badge {
		font-size: 0.625rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
	}

	.option-type-badge.driver {
		background: var(--color-primary-100);
		color: var(--color-primary-700);
	}

	.option-type-badge.outcome {
		background: #fef3c7;
		color: #92400e;
	}

	.popup-header h3 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin: 0;
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
		background: var(--color-field-surface);
		color: var(--color-text-source);
	}

	.popup-body {
		flex: 1;
		padding: 1.5rem 2rem;
		overflow-y: auto;
	}

	/* Continuous prose insight styling - clean, no templates */
	.insight-prose {
		font-size: 0.9375rem;
		line-height: 1.8;
		color: var(--color-text-manifest);
	}

	.insight-prose p {
		margin: 0 0 1.25rem 0;
	}

	.insight-prose p:last-child {
		margin-bottom: 0;
	}

	/* Bold text styling (from markdown **text**) */
	.insight-prose :global(strong) {
		color: var(--color-primary-700);
		font-weight: 600;
	}

	/* Mark name styling - subtle emphasis */
	.insight-prose .mark-name {
		font-style: italic;
		color: var(--color-text-source);
		font-weight: 500;
	}

	.popup-footer {
		display: flex;
		justify-content: center;
		padding: 1rem 1.5rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.close-text-btn {
		padding: 0.625rem 1.5rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.close-text-btn:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
	}

</style>
