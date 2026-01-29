<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth, isAuthenticated, user, theme, addToast } from '$lib/stores';

	let isLoading = true;

	onMount(async () => {
		const currentUser = await auth.loadUser();
		if (!currentUser) {
			goto('/login');
			return;
		}
		isLoading = false;
	});

	async function handleLogout() {
		await auth.logout();
		addToast('info', 'Signed out', 'You have been logged out');
		goto('/login');
	}

	function toggleTheme() {
		theme.toggle();
	}
</script>

{#if isLoading}
	<div class="loading-container">
		<div class="spinner"></div>
	</div>
{:else}
	<div class="app-layout">
		<!-- Sidebar -->
		<aside class="sidebar">
			<div class="sidebar-header">
				<h2 class="logo">Reality Transformer</h2>
			</div>

			<nav class="sidebar-nav">
				<a href="/chat" class="nav-item">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
					</svg>
					<span>Chat</span>
				</a>
				<a href="/goals" class="nav-item">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="12" cy="12" r="10"/>
						<circle cx="12" cy="12" r="6"/>
						<circle cx="12" cy="12" r="2"/>
					</svg>
					<span>Goals</span>
				</a>
				<a href="/documents" class="nav-item">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
						<polyline points="14 2 14 8 20 8"/>
					</svg>
					<span>Documents</span>
				</a>
				<a href="/sessions" class="nav-item">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
						<line x1="16" x2="16" y1="2" y2="6"/>
						<line x1="8" x2="8" y1="2" y2="6"/>
						<line x1="3" x2="21" y1="10" y2="10"/>
					</svg>
					<span>Sessions</span>
				</a>
			</nav>

			<div class="sidebar-footer">
				<div class="user-info">
					<div class="user-avatar">
						{$user?.name?.[0] || $user?.email?.[0] || 'U'}
					</div>
					<div class="user-details">
						<span class="user-name">{$user?.name || 'User'}</span>
						<span class="user-email">{$user?.email}</span>
					</div>
				</div>

				<div class="footer-actions">
					<button class="icon-btn" on:click={toggleTheme} title="Toggle theme">
						{#if $theme.isDark}
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<circle cx="12" cy="12" r="4"/>
								<path d="M12 2v2"/>
								<path d="M12 20v2"/>
								<path d="m4.93 4.93 1.41 1.41"/>
								<path d="m17.66 17.66 1.41 1.41"/>
								<path d="M2 12h2"/>
								<path d="M20 12h2"/>
								<path d="m6.34 17.66-1.41 1.41"/>
								<path d="m19.07 4.93-1.41 1.41"/>
							</svg>
						{:else}
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
							</svg>
						{/if}
					</button>
					<button class="icon-btn" on:click={handleLogout} title="Sign out">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
							<polyline points="16 17 21 12 16 7"/>
							<line x1="21" x2="9" y1="12" y2="12"/>
						</svg>
					</button>
				</div>
			</div>
		</aside>

		<!-- Main content -->
		<main class="main-content">
			<slot />
		</main>
	</div>
{/if}

<style>
	.loading-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid hsl(var(--muted));
		border-top-color: hsl(var(--primary));
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.app-layout {
		display: flex;
		min-height: 100vh;
	}

	.sidebar {
		width: 260px;
		background: hsl(var(--card));
		border-right: 1px solid hsl(var(--border));
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
	}

	.sidebar-header {
		padding: 1.25rem;
		border-bottom: 1px solid hsl(var(--border));
	}

	.logo {
		font-size: 1.125rem;
		font-weight: 700;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.sidebar-nav {
		flex: 1;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.nav-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		border-radius: 0.5rem;
		color: hsl(var(--foreground));
		text-decoration: none;
		transition: background-color 0.2s;
	}

	.nav-item:hover {
		background: hsl(var(--accent));
	}

	.sidebar-footer {
		padding: 1rem;
		border-top: 1px solid hsl(var(--border));
	}

	.user-info {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.user-avatar {
		width: 36px;
		height: 36px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-weight: 600;
		font-size: 0.875rem;
	}

	.user-details {
		flex: 1;
		min-width: 0;
	}

	.user-name {
		display: block;
		font-weight: 500;
		font-size: 0.875rem;
	}

	.user-email {
		display: block;
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.footer-actions {
		display: flex;
		gap: 0.5rem;
	}

	.icon-btn {
		padding: 0.5rem;
		background: none;
		border: 1px solid hsl(var(--border));
		border-radius: 0.5rem;
		color: hsl(var(--foreground));
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.icon-btn:hover {
		background: hsl(var(--accent));
	}

	.main-content {
		flex: 1;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}
</style>
