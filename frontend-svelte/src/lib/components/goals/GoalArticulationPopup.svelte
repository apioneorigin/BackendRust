<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	interface DiscoveredGoal {
		id: string;
		type: string;
		identity: string;
		goalStatement?: string;
		articulation?: string;
		firstMove: string;
		confidence: number;
		sourceFiles?: string[];
		addedToInventory?: boolean;
	}

	export let open = false;
	export let goal: DiscoveredGoal | null = null;
	export let isSaved = false;

	const dispatch = createEventDispatcher<{
		close: void;
		save: DiscoveredGoal;
		chat: DiscoveredGoal;
		delete: DiscoveredGoal;
	}>();

	const goalTypeColors: Record<string, string> = {
		OPTIMIZE: 'type-action',
		BUILD: 'type-action',
		LEVERAGE: 'type-action',
		DISCOVER: 'type-insight',
		HIDDEN: 'type-insight',
		QUANTUM: 'type-insight',
		TRANSFORM: 'type-change',
		RESOLVE: 'type-change',
		RELEASE: 'type-change',
		PROTECT: 'type-shield',
		ALIGN: 'type-shield',
		INTEGRATION: 'type-systems',
		DIFFERENTIATION: 'type-systems',
		ANTI_SILOING: 'type-systems',
		SYNTHESIS: 'type-systems',
		RECONCILIATION: 'type-systems',
		ARBITRAGE: 'type-systems'
	};

	function getConfidenceColor(confidence: number): string {
		if (confidence >= 90) return 'confidence-high';
		if (confidence >= 70) return 'confidence-good';
		if (confidence >= 50) return 'confidence-medium';
		return 'confidence-low';
	}

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleClose();
		}
	}
</script>

{#if open && goal}
	<div
		class="popup-overlay"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="presentation"
		tabindex="-1"
	>
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div
			class="goal-popup"
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			aria-modal="true"
			aria-labelledby="goal-title"
		>
			<div class="popup-header">
				<div class="header-content">
					<span class="goal-type-badge {goalTypeColors[goal.type] || 'type-default'}">
						{goal.type.replace('_', ' ')}
					</span>
					<h3 id="goal-title">{goal.identity}</h3>
					<span class="goal-confidence {getConfidenceColor(goal.confidence)}">
						{goal.confidence}%
					</span>
				</div>
				<button class="close-btn" on:click={handleClose} aria-label="Close">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M18 6 6 18" /><path d="m6 6 12 12" />
					</svg>
				</button>
			</div>

			<div class="popup-body">
				{#if goal.goalStatement}
					<p class="goal-statement">{goal.goalStatement}</p>
				{/if}

				{#if goal.articulation}
					<div class="goal-articulation">{goal.articulation}</div>
				{/if}

				{#if goal.firstMove}
					<div class="goal-first-move">
						<span class="first-move-label">First Move</span>
						<p>{goal.firstMove}</p>
					</div>
				{/if}
			</div>

			<div class="popup-footer">
				<button
					class="action-btn save-btn"
					on:click={() => goal && dispatch('save', goal)}
					disabled={isSaved}
				>
					{#if isSaved}
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M20 6 9 17l-5-5" />
						</svg>
						Saved to Library
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
						</svg>
						Save to Library
					{/if}
				</button>
				<button class="action-btn chat-btn" on:click={() => goal && dispatch('chat', goal)}>
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
					</svg>
					Chat
				</button>
				<button class="action-btn remove-btn" on:click={() => goal && dispatch('delete', goal)}>
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M3 6h18" />
						<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
						<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
					</svg>
					Delete
				</button>
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
		z-index: 1050;
		padding: 1rem;
	}

	.goal-popup {
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
		align-items: flex-start;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid var(--color-veil-thin);
		background: var(--color-field-depth);
		flex-shrink: 0;
		gap: 0.75rem;
	}

	.header-content {
		display: flex;
		align-items: flex-start;
		gap: 0.625rem;
		flex: 1;
		min-width: 0;
		flex-wrap: wrap;
	}

	.goal-type-badge {
		font-size: 0.625rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		padding: 0.25rem 0.5rem;
		border-radius: 9999px;
		flex-shrink: 0;
	}

	.type-action { background: #f1f5f9; color: #475569; }
	.type-insight { background: #eef2ff; color: #3730a3; }
	.type-change { background: #fefce8; color: #854d0e; }
	.type-shield { background: #ecfdf5; color: #065f46; }
	.type-systems { background: #f0fdfa; color: #115e59; }
	.type-default { background: #f9fafb; color: #6b7280; }

	.popup-header h3 {
		font-size: 1.0625rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin: 0;
		line-height: 1.4;
		flex: 1;
		min-width: 0;
	}

	.goal-confidence {
		font-size: 0.8125rem;
		font-weight: 700;
		flex-shrink: 0;
		white-space: nowrap;
	}

	.confidence-high { color: #16a34a; }
	.confidence-good { color: #2563eb; }
	.confidence-medium { color: #ca8a04; }
	.confidence-low { color: #dc2626; }

	.close-btn {
		padding: 0.5rem;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.375rem;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.close-btn:hover {
		background: var(--color-field-surface);
		color: var(--color-text-source);
	}

	.popup-body {
		flex: 1;
		padding: 1.5rem 2rem;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.goal-statement {
		font-size: 0.9375rem;
		font-weight: 500;
		color: var(--color-text-source);
		line-height: 1.5;
		font-style: italic;
		border-left: 3px solid var(--color-primary-300);
		padding-left: 1rem;
		margin: 0;
	}

	.goal-articulation {
		font-size: 0.9375rem;
		color: var(--color-text-manifest);
		line-height: 1.8;
		white-space: pre-line;
	}

	.goal-first-move {
		padding-top: 1rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	.first-move-label {
		font-size: 0.6875rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-whisper);
		display: block;
		margin-bottom: 0.375rem;
	}

	.goal-first-move p {
		font-size: 0.9375rem;
		font-weight: 500;
		color: var(--color-text-source);
		line-height: 1.6;
		margin: 0;
	}

	.popup-footer {
		display: flex;
		gap: 0.5rem;
		padding: 1rem 1.5rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.action-btn {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.375rem;
		padding: 0.5625rem 0.75rem;
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.save-btn {
		background: var(--color-success-50);
		border: 1px solid var(--color-success-200);
		color: var(--color-success-700);
	}

	.save-btn:hover:not(:disabled) {
		background: var(--color-success-100);
	}

	.save-btn:disabled {
		opacity: 0.7;
		cursor: default;
	}

	.chat-btn {
		background: var(--color-primary-500);
		border: none;
		color: white;
	}

	.chat-btn:hover {
		background: var(--color-primary-600);
	}

	.remove-btn {
		background: transparent;
		border: 1px solid var(--color-veil-soft);
		color: var(--color-text-whisper);
	}

	.remove-btn:hover {
		border-color: var(--color-error-400);
		color: var(--color-error-500);
		background: var(--color-error-50);
	}
</style>
