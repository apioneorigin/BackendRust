<script lang="ts">
	import { onMount } from 'svelte';
	import { user, addToast } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { Button, Card, Spinner } from '$lib/components/ui';
	import { api } from '$lib/utils/api';

	interface DashboardStats {
		totalUsers: number;
		activeUsers: number;
		totalConversations: number;
		totalMessages: number;
		creditsUsed: number;
		revenue: number;
	}

	interface UserListItem {
		id: string;
		email: string;
		name: string;
		role: string;
		credits: number;
		createdAt: string;
		lastActive: string;
	}

	let isLoading = true;
	let stats: DashboardStats | null = null;
	let users: UserListItem[] = [];
	let selectedTab: 'overview' | 'users' | 'analytics' | 'logs' = 'overview';

	onMount(async () => {
		// Check if user is admin
		if (!$user?.isGlobalAdmin) {
			addToast('error', 'Access denied. Admin privileges required.');
			goto('/chat');
			return;
		}

		await loadDashboard();
	});

	async function loadDashboard() {
		isLoading = true;
		try {
			const [dashboardData, usersData] = await Promise.all([
				api.get<{ stats: DashboardStats }>('/api/admin/dashboard'),
				api.get<{ users: UserListItem[] }>('/api/admin/users/list')
			]);
			stats = dashboardData.stats;
			users = usersData.users || [];
		} catch (error: any) {
			addToast('error', error.message || 'Failed to load dashboard');
		} finally {
			isLoading = false;
		}
	}

	function formatNumber(num: number): string {
		if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
		if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
		return num.toString();
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Admin Dashboard | Reality Transformer</title>
</svelte:head>

<div class="admin-page">
	<div class="admin-header">
		<div class="header-content">
			<h1>Admin Dashboard</h1>
			<p>Monitor and manage your platform</p>
		</div>
		<Button variant="outline" on:click={loadDashboard}>
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
				<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
				<path d="M3 3v5h5" />
				<path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
				<path d="M16 16h5v5" />
			</svg>
			Refresh
		</Button>
	</div>

	<!-- Tabs -->
	<div class="tabs">
		<button
			class="tab"
			class:active={selectedTab === 'overview'}
			on:click={() => (selectedTab = 'overview')}
		>
			Overview
		</button>
		<button
			class="tab"
			class:active={selectedTab === 'users'}
			on:click={() => (selectedTab = 'users')}
		>
			Users
		</button>
		<button
			class="tab"
			class:active={selectedTab === 'analytics'}
			on:click={() => (selectedTab = 'analytics')}
		>
			Analytics
		</button>
		<button class="tab" class:active={selectedTab === 'logs'} on:click={() => (selectedTab = 'logs')}>
			Logs
		</button>
	</div>

	{#if isLoading}
		<div class="loading-state">
			<Spinner size="lg" />
			<p>Loading dashboard...</p>
		</div>
	{:else}
		<!-- Overview Tab -->
		{#if selectedTab === 'overview'}
			<div class="stats-grid">
				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon users">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
								<circle cx="9" cy="7" r="4" />
								<path d="M22 21v-2a4 4 0 0 0-3-3.87" />
								<path d="M16 3.13a4 4 0 0 1 0 7.75" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalUsers || 0)}</span>
							<span class="stat-label">Total Users</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon active">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="M22 12h-4l-3 9L9 3l-3 9H2" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.activeUsers || 0)}</span>
							<span class="stat-label">Active Users</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon conversations">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalConversations || 0)}</span>
							<span class="stat-label">Conversations</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon messages">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalMessages || 0)}</span>
							<span class="stat-label">Messages</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon credits">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<circle cx="12" cy="12" r="10" />
								<path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8" />
								<path d="M12 18V6" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.creditsUsed || 0)}</span>
							<span class="stat-label">Credits Used</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon revenue">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<line x1="12" x2="12" y1="2" y2="22" />
								<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">${formatNumber(stats?.revenue || 0)}</span>
							<span class="stat-label">Revenue</span>
						</div>
					</div>
				</Card>
			</div>
		{/if}

		<!-- Users Tab -->
		{#if selectedTab === 'users'}
			<div class="users-section">
				<Card variant="default" padding="none">
					<div class="table-container">
						<table class="users-table">
							<thead>
								<tr>
									<th>User</th>
									<th>Role</th>
									<th>Credits</th>
									<th>Joined</th>
									<th>Last Active</th>
									<th>Actions</th>
								</tr>
							</thead>
							<tbody>
								{#each users as userItem (userItem.id)}
									<tr>
										<td>
											<div class="user-cell">
												<div class="user-avatar">
													{userItem.name?.[0] || userItem.email[0]}
												</div>
												<div class="user-info">
													<span class="user-name">{userItem.name || 'No name'}</span>
													<span class="user-email">{userItem.email}</span>
												</div>
											</div>
										</td>
										<td>
											<span class="role-badge" class:admin={userItem.role === 'ADMIN'}>
												{userItem.role}
											</span>
										</td>
										<td>{userItem.credits}</td>
										<td>{formatDate(userItem.createdAt)}</td>
										<td>{formatDate(userItem.lastActive)}</td>
										<td>
											<Button variant="ghost" size="sm">Edit</Button>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</Card>
			</div>
		{/if}

		<!-- Analytics Tab -->
		{#if selectedTab === 'analytics'}
			<div class="analytics-placeholder">
				<Card variant="floating" padding="lg">
					<div class="placeholder-content">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="48"
							height="48"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M3 3v18h18" />
							<path d="m19 9-5 5-4-4-3 3" />
						</svg>
						<h3>Analytics Coming Soon</h3>
						<p>Detailed usage analytics and charts will be available here.</p>
					</div>
				</Card>
			</div>
		{/if}

		<!-- Logs Tab -->
		{#if selectedTab === 'logs'}
			<div class="logs-placeholder">
				<Card variant="floating" padding="lg">
					<div class="placeholder-content">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="48"
							height="48"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
							<polyline points="14 2 14 8 20 8" />
							<line x1="16" x2="8" y1="13" y2="13" />
							<line x1="16" x2="8" y1="17" y2="17" />
							<line x1="10" x2="8" y1="9" y2="9" />
						</svg>
						<h3>System Logs</h3>
						<p>View system logs and error reports here.</p>
					</div>
				</Card>
			</div>
		{/if}
	{/if}
</div>

<style>
	.admin-page {
		padding: 2rem;
		height: 100%;
		overflow-y: auto;
	}

	.admin-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 1.5rem;
	}

	.header-content h1 {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.25rem;
	}

	.header-content p {
		color: var(--color-text-whisper);
	}

	.tabs {
		display: flex;
		gap: 0.25rem;
		margin-bottom: 1.5rem;
		background: var(--color-field-depth);
		padding: 0.25rem;
		border-radius: 0.75rem;
		width: fit-content;
	}

	.tab {
		padding: 0.625rem 1rem;
		background: transparent;
		border: none;
		border-radius: 0.5rem;
		color: var(--color-text-whisper);
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.tab:hover {
		color: var(--color-text-manifest);
	}

	.tab.active {
		background: var(--color-field-surface);
		color: var(--color-text-source);
		box-shadow: var(--shadow-sm);
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem;
		gap: 1rem;
		color: var(--color-text-whisper);
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: 1rem;
	}

	.stat-card {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.stat-icon {
		width: 48px;
		height: 48px;
		border-radius: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.stat-icon.users {
		background: var(--color-primary-100);
		color: var(--color-primary-600);
	}

	.stat-icon.active {
		background: #d1fae5;
		color: #059669;
	}

	.stat-icon.conversations {
		background: rgba(6, 182, 212, 0.1);
		color: #0891b2;
	}

	.stat-icon.messages {
		background: #fce7f3;
		color: #db2777;
	}

	.stat-icon.credits {
		background: #fef3c7;
		color: #d97706;
	}

	.stat-icon.revenue {
		background: #d1fae5;
		color: #059669;
	}

	[data-theme='dark'] .stat-icon.users {
		background: var(--color-primary-900);
		color: var(--color-primary-300);
	}

	[data-theme='dark'] .stat-icon.active {
		background: rgba(5, 150, 105, 0.2);
		color: #34d399;
	}

	.stat-content {
		display: flex;
		flex-direction: column;
	}

	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.stat-label {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
	}

	.table-container {
		overflow-x: auto;
	}

	.users-table {
		width: 100%;
		border-collapse: collapse;
	}

	.users-table th,
	.users-table td {
		padding: 1rem;
		text-align: left;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.users-table th {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-whisper);
		background: var(--color-field-depth);
	}

	.user-cell {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.user-avatar {
		width: 36px;
		height: 36px;
		background: var(--color-primary-500);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #ffffff;
		font-weight: 600;
		font-size: 0.875rem;
	}

	.user-info {
		display: flex;
		flex-direction: column;
	}

	.user-name {
		font-weight: 500;
		color: var(--color-text-source);
	}

	.user-email {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	.role-badge {
		padding: 0.25rem 0.625rem;
		background: var(--color-field-depth);
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-manifest);
	}

	.role-badge.admin {
		background: var(--color-primary-100);
		color: var(--color-primary-700);
	}

	[data-theme='dark'] .role-badge.admin {
		background: var(--color-primary-900);
		color: var(--color-primary-300);
	}

	.placeholder-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: 3rem;
		color: var(--color-text-whisper);
	}

	.placeholder-content svg {
		margin-bottom: 1rem;
		opacity: 0.5;
	}

	.placeholder-content h3 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.placeholder-content p {
		max-width: 300px;
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.admin-page {
			padding: 1rem;
		}

		.admin-header {
			flex-direction: column;
			gap: 1rem;
		}

		.tabs {
			width: 100%;
			overflow-x: auto;
		}
	}
</style>
