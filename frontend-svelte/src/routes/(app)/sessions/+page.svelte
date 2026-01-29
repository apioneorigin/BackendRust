<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { session, sessions, addToast } from '$lib/stores';
	import type { Session } from '$lib/stores/session';

	// Accept SvelteKit props
	export let data: Record<string, unknown> = {};
	let _restProps = $$restProps;

	onMount(async () => {
		await session.loadSessions();
	});

	async function handleCreateSession() {
		const newSession = await session.createSession();
		if (newSession) {
			addToast('success', 'Session created', 'A new transformation session has been started');
			goto('/chat');
		}
	}

	async function handleSelectSession(sessionId: string) {
		await session.selectSession(sessionId);
		goto('/chat');
	}

	function formatDate(date: Date | string) {
		const d = typeof date === 'string' ? new Date(date) : date;
		return new Intl.DateTimeFormat('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		}).format(d);
	}

	function getStageLabel(stage: number) {
		const stages = ['Goal', 'Discover', 'Decode', 'Design', 'Dashboard'];
		return stages[stage] || 'Unknown';
	}

	function getStageProgress(stage: number) {
		return ((stage + 1) / 5) * 100;
	}
</script>

<svelte:head>
	<title>Sessions | Reality Transformer</title>
</svelte:head>

<div class="sessions-page">
	<header class="page-header">
		<div>
			<h1>Transformation Sessions</h1>
			<p>Your transformation journey history</p>
		</div>
		<button class="btn-primary" on:click={handleCreateSession}>
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M12 5v14"/>
				<path d="M5 12h14"/>
			</svg>
			New Session
		</button>
	</header>

	<!-- Sessions list -->
	<div class="sessions-list">
		{#if $sessions.length === 0}
			<div class="empty-state">
				<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
					<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
					<line x1="16" x2="16" y1="2" y2="6"/>
					<line x1="8" x2="8" y1="2" y2="6"/>
					<line x1="3" x2="21" y1="10" y2="10"/>
				</svg>
				<h3>No sessions yet</h3>
				<p>Start a new transformation session to begin your journey</p>
				<button class="btn-primary" on:click={handleCreateSession}>
					Start Your First Session
				</button>
			</div>
		{:else}
			{#each $sessions as sess (sess.id)}
				<button
					class="session-card"
					on:click={() => handleSelectSession(sess.id)}
				>
					<div class="session-header">
						<div class="session-status" class:completed={sess.completed}>
							{sess.completed ? 'Completed' : 'In Progress'}
						</div>
						<span class="session-date">{formatDate(sess.lastAccessedAt)}</span>
					</div>

					<h3 class="session-title">
						{sess.goalText || 'Untitled Session'}
					</h3>

					<div class="session-progress">
						<div class="progress-bar">
							<div
								class="progress-fill"
								style="width: {getStageProgress(sess.stage)}%"
							></div>
						</div>
						<span class="progress-label">
							Stage: {getStageLabel(sess.stage)}
						</span>
					</div>

					<div class="session-meta">
						<span>Created {formatDate(sess.createdAt)}</span>
					</div>
				</button>
			{/each}
		{/if}
	</div>
</div>

<style>
	.sessions-page {
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

	.sessions-list {
		display: grid;
		gap: 1rem;
	}

	.session-card {
		width: 100%;
		padding: 1.25rem;
		background: hsl(var(--card));
		border: 1px solid hsl(var(--border));
		border-radius: 0.75rem;
		text-align: left;
		cursor: pointer;
		transition: border-color 0.2s, box-shadow 0.2s;
	}

	.session-card:hover {
		border-color: hsl(var(--primary) / 0.5);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.session-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
	}

	.session-status {
		padding: 0.25rem 0.625rem;
		background: hsl(38 92% 50% / 0.1);
		color: hsl(38 92% 50%);
		border-radius: 9999px;
		font-size: 0.6875rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.session-status.completed {
		background: hsl(142 76% 36% / 0.1);
		color: hsl(142 76% 36%);
	}

	.session-date {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
	}

	.session-title {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: 1rem;
		line-height: 1.4;
	}

	.session-progress {
		margin-bottom: 1rem;
	}

	.progress-bar {
		height: 6px;
		background: hsl(var(--muted));
		border-radius: 9999px;
		overflow: hidden;
		margin-bottom: 0.5rem;
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
		border-radius: 9999px;
		transition: width 0.3s ease;
	}

	.progress-label {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
	}

	.session-meta {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
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

	.empty-state p {
		margin-bottom: 1.5rem;
	}
</style>
