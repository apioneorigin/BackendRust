<script lang="ts">
	import { onMount } from 'svelte';
	import { goals, activeGoals, completedGoals, addToast } from '$lib/stores';
	import type { Goal } from '$lib/stores/goals';

	// Accept SvelteKit props
	export let data: Record<string, unknown> = {};
	let _restProps = $$restProps;

	let isCreating = false;
	let newGoalTitle = '';
	let newGoalDescription = '';
	let filter: 'all' | 'active' | 'locked' = 'all';

	onMount(async () => {
		await goals.loadGoals();
	});

	$: filteredGoals = filter === 'active'
		? $activeGoals
		: filter === 'locked'
		? $completedGoals
		: $goals.goals;

	async function handleCreateGoal() {
		if (!newGoalTitle.trim()) return;

		const goal = await goals.createGoal({
			title: newGoalTitle.trim(),
			description: newGoalDescription.trim() || undefined,
		});

		if (goal) {
			addToast('success', 'Goal created', 'Your new goal has been added');
			newGoalTitle = '';
			newGoalDescription = '';
			isCreating = false;
		}
	}

	async function handleLockGoal(goalId: string) {
		await goals.lockGoal(goalId);
		addToast('success', 'Goal locked', 'This goal has been finalized');
	}

	async function handleDeleteGoal(goalId: string) {
		if (confirm('Are you sure you want to delete this goal?')) {
			await goals.deleteGoal(goalId);
			addToast('info', 'Goal deleted', 'The goal has been removed');
		}
	}

	function formatDate(date: Date) {
		return new Intl.DateTimeFormat('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
		}).format(date);
	}
</script>

<svelte:head>
	<title>Goals | Reality Transformer</title>
</svelte:head>

<div class="goals-page">
	<header class="page-header">
		<div>
			<h1>Goals</h1>
			<p>Track and manage your transformation goals</p>
		</div>
		<button class="btn-primary" on:click={() => isCreating = true}>
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M12 5v14"/>
				<path d="M5 12h14"/>
			</svg>
			New Goal
		</button>
	</header>

	<!-- Filter tabs -->
	<div class="filter-tabs">
		<button
			class="filter-tab"
			class:active={filter === 'all'}
			on:click={() => filter = 'all'}
		>
			All ({$goals.goals.length})
		</button>
		<button
			class="filter-tab"
			class:active={filter === 'active'}
			on:click={() => filter = 'active'}
		>
			Active ({$activeGoals.length})
		</button>
		<button
			class="filter-tab"
			class:active={filter === 'locked'}
			on:click={() => filter = 'locked'}
		>
			Locked ({$completedGoals.length})
		</button>
	</div>

	<!-- Goals list -->
	<div class="goals-list">
		{#if filteredGoals.length === 0}
			<div class="empty-state">
				<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="10"/>
					<circle cx="12" cy="12" r="6"/>
					<circle cx="12" cy="12" r="2"/>
				</svg>
				<h3>No goals yet</h3>
				<p>Create your first goal to start your transformation journey</p>
			</div>
		{:else}
			{#each filteredGoals as goal (goal.id)}
				<div class="goal-card">
					<div class="goal-header">
						<div class="goal-status" class:locked={goal.locked}>
							{goal.locked ? 'Locked' : 'Active'}
						</div>
						{#if goal.domain}
							<span class="goal-domain">{goal.domain}</span>
						{/if}
					</div>

					<h3 class="goal-title">{goal.goalText}</h3>

					{#if goal.intent}
						<p class="goal-intent">{goal.intent}</p>
					{/if}

					<div class="goal-meta">
						<span>Created {formatDate(goal.createdAt)}</span>
						{#if goal.lockedAt}
							<span>Locked {formatDate(goal.lockedAt)}</span>
						{/if}
					</div>

					<div class="goal-actions">
						{#if !goal.locked}
							<button class="btn-success" on:click={() => handleLockGoal(goal.id)}>
								Lock Goal
							</button>
						{/if}
						<button class="btn-ghost" on:click={() => handleDeleteGoal(goal.id)}>
							Delete
						</button>
					</div>
				</div>
			{/each}
		{/if}
	</div>

	<!-- Create goal modal -->
	{#if isCreating}
		<div class="modal-overlay" on:click={() => isCreating = false} on:keydown={(e) => e.key === 'Escape' && (isCreating = false)}>
			<div class="modal" on:click|stopPropagation role="dialog" aria-modal="true">
				<h2>Create New Goal</h2>

				<form on:submit|preventDefault={handleCreateGoal}>
					<div class="form-group">
						<label for="title">Goal</label>
						<input
							type="text"
							id="title"
							bind:value={newGoalTitle}
							placeholder="What do you want to achieve?"
							required
						/>
					</div>

					<div class="form-group">
						<label for="description">Details (optional)</label>
						<textarea
							id="description"
							bind:value={newGoalDescription}
							placeholder="Add more context about your goal"
							rows="3"
						></textarea>
					</div>

					<div class="modal-actions">
						<button type="button" class="btn-ghost" on:click={() => isCreating = false}>
							Cancel
						</button>
						<button type="submit" class="btn-primary" disabled={!newGoalTitle.trim()}>
							Create Goal
						</button>
					</div>
				</form>
			</div>
		</div>
	{/if}
</div>

<style>
	.goals-page {
		padding: 1.5rem;
		max-width: 1000px;
		margin: 0 auto;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1.5rem;
	}

	.page-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: 0.25rem;
	}

	.page-header p {
		color: hsl(var(--muted-foreground));
		font-size: 0.875rem;
	}

	.btn-primary {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		background: hsl(var(--primary));
		color: hsl(var(--primary-foreground));
		border: none;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
	}

	.btn-primary:hover {
		opacity: 0.9;
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-success {
		padding: 0.5rem 0.75rem;
		background: hsl(142 76% 36%);
		color: white;
		border: none;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
	}

	.btn-ghost {
		padding: 0.5rem 0.75rem;
		background: none;
		color: hsl(var(--muted-foreground));
		border: 1px solid hsl(var(--border));
		border-radius: 0.375rem;
		font-size: 0.75rem;
		cursor: pointer;
	}

	.btn-ghost:hover {
		background: hsl(var(--accent));
	}

	.filter-tabs {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
		border-bottom: 1px solid hsl(var(--border));
		padding-bottom: 0.5rem;
	}

	.filter-tab {
		padding: 0.5rem 1rem;
		background: none;
		border: none;
		border-radius: 0.375rem;
		color: hsl(var(--muted-foreground));
		font-size: 0.875rem;
		cursor: pointer;
	}

	.filter-tab.active {
		background: hsl(var(--accent));
		color: hsl(var(--foreground));
		font-weight: 500;
	}

	.goals-list {
		display: grid;
		gap: 1rem;
	}

	.goal-card {
		padding: 1.25rem;
		background: hsl(var(--card));
		border: 1px solid hsl(var(--border));
		border-radius: 0.75rem;
	}

	.goal-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
	}

	.goal-status {
		padding: 0.25rem 0.5rem;
		border-radius: 9999px;
		font-size: 0.625rem;
		font-weight: 600;
		text-transform: uppercase;
		background: hsl(142 76% 36%);
		color: white;
	}

	.goal-status.locked {
		background: hsl(221 83% 53%);
	}

	.goal-domain {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
	}

	.goal-title {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		line-height: 1.4;
	}

	.goal-intent {
		font-size: 0.875rem;
		color: hsl(var(--muted-foreground));
		margin-bottom: 0.75rem;
		line-height: 1.5;
	}

	.goal-meta {
		display: flex;
		gap: 1rem;
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
		margin-bottom: 1rem;
	}

	.goal-actions {
		display: flex;
		gap: 0.5rem;
	}

	.empty-state {
		text-align: center;
		padding: 3rem;
		color: hsl(var(--muted-foreground));
	}

	.empty-state svg {
		margin-bottom: 1rem;
		opacity: 0.5;
	}

	.empty-state h3 {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: hsl(var(--foreground));
	}

	/* Modal */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}

	.modal {
		width: 100%;
		max-width: 480px;
		padding: 1.5rem;
		background: hsl(var(--card));
		border: 1px solid hsl(var(--border));
		border-radius: 0.75rem;
		margin: 1rem;
	}

	.modal h2 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 1.5rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		margin-bottom: 0.5rem;
	}

	.form-group input,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		background: hsl(var(--background));
		border: 1px solid hsl(var(--border));
		border-radius: 0.5rem;
		color: hsl(var(--foreground));
		font-size: 0.875rem;
	}

	.form-group input:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: hsl(var(--ring));
	}

	.modal-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		margin-top: 1.5rem;
	}
</style>
