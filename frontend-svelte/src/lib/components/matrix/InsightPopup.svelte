<script lang="ts">
	/**
	 * InsightPopup - Displays articulated insights for matrix row/column options
	 *
	 * Based on insight-articulation-final.pdf:
	 * 3-component structure: THE TRUTH -> YOUR TRUTH -> THE MARK
	 * Total: 160-250 words per insight
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
					<span class="option-type-badge" class:row={optionType === 'row'} class:column={optionType === 'column'}>
						{optionType}
					</span>
					<h3 id="insight-title">{optionLabel}</h3>
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
				<!-- THE TRUTH Section -->
				<section class="insight-section the-truth">
					<div class="section-marker">
						<span class="marker-number">1</span>
						<span class="marker-label">The Truth</span>
					</div>
					<div class="section-content">
						<p class="analogy">{insight.the_truth}</p>
						<p class="law">{@html parseBold(insight.the_truth_law)}</p>
					</div>
				</section>

				<div class="section-divider"></div>

				<!-- YOUR TRUTH Section -->
				<section class="insight-section your-truth">
					<div class="section-marker">
						<span class="marker-number">2</span>
						<span class="marker-label">Your Truth</span>
					</div>
					<div class="section-content">
						<p class="recognition">{insight.your_truth}</p>
						<p class="revelation">{@html parseBold(insight.your_truth_revelation)}</p>
					</div>
				</section>

				<div class="section-divider"></div>

				<!-- THE MARK Section -->
				<section class="insight-section the-mark">
					<div class="section-marker">
						<span class="marker-number">3</span>
						<span class="marker-label">The Mark</span>
					</div>
					<div class="section-content">
						<p class="mark-name">This is <em>{insight.the_mark_name}</em>.</p>
						<p class="prediction">{insight.the_mark_prediction}</p>
						<p class="identity">{@html parseBold(insight.the_mark_identity)}</p>
					</div>
				</section>
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

	.option-type-badge.row {
		background: var(--color-primary-100);
		color: var(--color-primary-700);
	}

	.option-type-badge.column {
		background: #fef3c7;
		color: #92400e;
	}

	[data-theme='dark'] .option-type-badge.row {
		background: rgba(15, 76, 117, 0.3);
		color: var(--color-primary-300);
	}

	[data-theme='dark'] .option-type-badge.column {
		background: rgba(146, 64, 14, 0.3);
		color: #fcd34d;
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
		padding: 1.5rem;
		overflow-y: auto;
	}

	.insight-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.section-marker {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.marker-number {
		width: 1.5rem;
		height: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.75rem;
		font-weight: 700;
		background: var(--color-primary-500);
		color: white;
		border-radius: 50%;
	}

	.marker-label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-whisper);
	}

	.section-content {
		padding-left: 2rem;
	}

	.section-content p {
		margin: 0;
		line-height: 1.7;
		color: var(--color-text-manifest);
	}

	.section-content p + p {
		margin-top: 0.75rem;
	}

	/* THE TRUTH styles */
	.the-truth .analogy {
		font-style: italic;
		font-size: 0.9375rem;
		color: var(--color-text-source);
	}

	.the-truth .law {
		font-size: 0.9375rem;
	}

	.the-truth .law :global(strong) {
		color: var(--color-primary-700);
		font-weight: 600;
	}

	[data-theme='dark'] .the-truth .law :global(strong) {
		color: var(--color-primary-300);
	}

	/* YOUR TRUTH styles */
	.your-truth .recognition {
		font-size: 0.9375rem;
	}

	.your-truth .revelation {
		font-size: 0.9375rem;
	}

	.your-truth .revelation :global(strong) {
		color: var(--color-primary-700);
		font-weight: 600;
	}

	[data-theme='dark'] .your-truth .revelation :global(strong) {
		color: var(--color-primary-300);
	}

	/* THE MARK styles */
	.the-mark .mark-name {
		font-size: 0.9375rem;
	}

	.the-mark .mark-name em {
		font-style: italic;
		color: var(--color-text-source);
		font-weight: 500;
	}

	.the-mark .prediction {
		font-size: 0.9375rem;
	}

	.the-mark .identity {
		font-size: 0.9375rem;
	}

	.the-mark .identity :global(strong) {
		color: var(--color-primary-700);
		font-weight: 600;
	}

	[data-theme='dark'] .the-mark .identity :global(strong) {
		color: var(--color-primary-300);
	}

	.section-divider {
		height: 1px;
		background: var(--color-veil-thin);
		margin: 1.25rem 0;
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

	[data-theme='dark'] .close-text-btn:hover {
		background: rgba(15, 76, 117, 0.2);
		color: var(--color-primary-300);
	}
</style>
