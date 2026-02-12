<script lang="ts">
	/**
	 * InsightPopup - Displays articulated insights (drivers) or outcomes (columns)
	 *
	 * Driver structure (rows):
	 * 1. Micro-moment (user's context)
	 * 2. The Truth (far domain analogy)
	 * 3. Principle (universal law)
	 * 4. Installation (recognition + name + identity)
	 *
	 * Outcome structure (columns):
	 * 1. The Arc (force → inflection → resolution)
	 * 2. The Landscape (position → fork → state)
	 * 3. The Anchor (destination name + signal + identity)
	 *
	 * Total: 200-300 words, displayed as continuous prose
	 */

	import { createEventDispatcher } from 'svelte';
	import type { ArticulatedInsight, ArticulatedOutcome } from '$lib/stores/matrix';
	import { addToast } from '$lib/stores';

	export let open = false;
	export let insight: ArticulatedInsight | null = null;
	export let outcome: ArticulatedOutcome | null = null;
	export let optionLabel = '';
	export let optionType: 'row' | 'column' = 'row';

	const dispatch = createEventDispatcher<{
		close: void;
	}>();

	// Map internal types to user-friendly labels
	$: displayType = optionType === 'row' ? 'driver' : 'outcome';
	$: displayTitle = (outcome?.title || insight?.title || optionLabel);
	$: hasContent = !!(outcome || insight);

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleClose();
		}
	}

	// Escape HTML entities to prevent XSS from LLM-generated content
	function escapeHtml(text: string): string {
		return text
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;');
	}

	// Parse markdown bold (**text**) to HTML (sanitized)
	function parseBold(text: string): string {
		if (!text) return '';
		return escapeHtml(text).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
	}

	// Build plain text from insight/outcome fields for clipboard
	function getInsightText(): string {
		const parts: string[] = [];
		if (outcome) {
			if (outcome.the_arc) parts.push(outcome.the_arc);
			if (outcome.the_arc_destination) parts.push(outcome.the_arc_destination);
			if (outcome.the_landscape) parts.push(outcome.the_landscape);
			if (outcome.the_landscape_operating_reality) parts.push(outcome.the_landscape_operating_reality);
			const anchor = [outcome.the_anchor_name, outcome.the_anchor_signal, outcome.the_anchor_identity].filter(Boolean).join(' ');
			if (anchor) parts.push(anchor);
		} else if (insight) {
			if (insight.micro_moment) parts.push(insight.micro_moment);
			if (insight.the_truth) parts.push(insight.the_truth);
			if (insight.the_truth_law) parts.push(insight.the_truth_law);
			if (insight.your_truth) parts.push(insight.your_truth);
			if (insight.your_truth_revelation) parts.push(insight.your_truth_revelation);
			const mark = [insight.the_mark_name, insight.the_mark_prediction, insight.the_mark_identity].filter(Boolean).join(' ');
			if (mark) parts.push(mark);
		}
		return parts.join('\n\n');
	}

	async function copyToClipboard() {
		try {
			await navigator.clipboard.writeText(getInsightText());
			addToast('success', 'Copied to clipboard');
		} catch {
			addToast('error', 'Failed to copy');
		}
	}
</script>

{#if open && hasContent}
	<div
		class="popup-overlay"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="presentation"
		tabindex="-1"
	>
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
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
					<h3 id="insight-title">{displayTitle}</h3>
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
				<article class="insight-prose">
					{#if outcome}
						<!-- OUTCOME: The Arc → The Landscape → The Anchor -->
						{#if outcome.the_arc}
							<p class="the-arc">{@html parseBold(outcome.the_arc)}</p>
						{/if}

						{#if outcome.the_arc_destination}
							<p class="destination">{@html parseBold(outcome.the_arc_destination)}</p>
						{/if}

						{#if outcome.the_landscape}
							<p>{@html parseBold(outcome.the_landscape)}</p>
						{/if}

						{#if outcome.the_landscape_operating_reality}
							<p>{@html parseBold(outcome.the_landscape_operating_reality)}</p>
						{/if}

						{#if outcome.the_anchor_name || outcome.the_anchor_signal || outcome.the_anchor_identity}
							<p>
								{#if outcome.the_anchor_name}<span class="anchor-name">{outcome.the_anchor_name}.</span> {/if}{outcome.the_anchor_signal || ''} {@html parseBold(outcome.the_anchor_identity || '')}
							</p>
						{/if}
					{:else if insight}
						<!-- DRIVER: Micro Moment → The Truth → Your Truth → The Mark -->
						{#if insight.micro_moment}
							<p class="micro-moment">{@html parseBold(insight.micro_moment)}</p>
						{/if}

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
					{/if}
				</article>
			</div>

			<div class="popup-footer">
				<button class="copy-btn" on:click={copyToClipboard} title="Copy to clipboard">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
						<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
					</svg>
					Copy
				</button>
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

	/* Continuous prose styling - clean, no templates */
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

	/* Driver: Micro moment — grounding scene in user's world */
	.insight-prose .micro-moment {
		font-style: italic;
		color: var(--color-text-source);
		border-left: 3px solid var(--color-primary-300);
		padding-left: 1rem;
	}

	/* Outcome: The Arc — progressive present tense, flows naturally */
	.insight-prose .the-arc {
		color: var(--color-text-source);
	}

	/* Outcome: Arc destination — bold landing point */
	.insight-prose .destination {
		font-weight: 600;
		color: var(--color-primary-700);
	}

	/* Outcome: Anchor name — positional emphasis */
	.insight-prose .anchor-name {
		font-style: italic;
		color: var(--color-text-source);
		font-weight: 500;
	}

	/* Bold text styling (from markdown **text**) */
	.insight-prose :global(strong) {
		color: var(--color-primary-700);
		font-weight: 600;
	}

	/* Driver: Mark name styling - subtle emphasis */
	.insight-prose .mark-name {
		font-style: italic;
		color: var(--color-text-source);
		font-weight: 500;
	}

	.popup-footer {
		display: flex;
		justify-content: center;
		gap: 0.5rem;
		padding: 1rem 1.5rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.copy-btn {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.625rem 1.25rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.copy-btn:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		color: var(--color-primary-700);
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
