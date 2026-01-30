<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth, isAuthenticated, user, theme, addToast } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';

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
		<div class="flex flex-col items-center gap-4">
			<Spinner size="lg" />
			<p class="text-text-whisper text-sm">Loading...</p>
		</div>
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
						<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
					</svg>
					<span>Chat</span>
				</a>
				<a href="/documents" class="nav-item">
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
						<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
						<polyline points="14 2 14 8 20 8" />
					</svg>
					<span>Documents</span>
				</a>
				<a href="/settings" class="nav-item">
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
						<path
							d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
						/>
						<circle cx="12" cy="12" r="3" />
					</svg>
					<span>Settings</span>
				</a>

				{#if $user?.isGlobalAdmin}
					<a href="/admin" class="nav-item">
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
							<path
								d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
							/>
						</svg>
						<span>Admin</span>
					</a>
				{/if}
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
					<button class="sidebar-icon-btn" on:click={toggleTheme} title="Toggle theme">
						{#if $theme.isDark}
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
								<circle cx="12" cy="12" r="4" />
								<path d="M12 2v2" />
								<path d="M12 20v2" />
								<path d="m4.93 4.93 1.41 1.41" />
								<path d="m17.66 17.66 1.41 1.41" />
								<path d="M2 12h2" />
								<path d="M20 12h2" />
								<path d="m6.34 17.66-1.41 1.41" />
								<path d="m19.07 4.93-1.41 1.41" />
							</svg>
						{:else}
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
								<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
							</svg>
						{/if}
					</button>
					<button class="sidebar-icon-btn" on:click={handleLogout} title="Sign out">
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
							<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
							<polyline points="16 17 21 12 16 7" />
							<line x1="21" x2="9" y1="12" y2="12" />
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
		min-height: 100dvh;
		background-color: var(--color-field-void);
	}

	.app-layout {
		display: flex;
		min-height: 100dvh;
	}

	.sidebar {
		width: 260px;
		background: var(--color-field-surface);
		border-right: 1px solid var(--color-veil-thin);
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
	}

	.sidebar-header {
		padding: 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.logo {
		font-size: 1.125rem;
		font-weight: 700;
		background: var(--gradient-primary);
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
		border-radius: 0.625rem;
		color: var(--color-text-manifest);
		text-decoration: none;
		transition: all 0.15s ease;
		font-weight: 500;
		font-size: 0.875rem;
	}

	.nav-item:hover {
		background: var(--color-field-depth);
		color: var(--color-text-source);
	}

	.sidebar-footer {
		padding: 1rem;
		border-top: 1px solid var(--color-veil-thin);
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
		background: var(--gradient-primary);
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
		color: var(--color-text-source);
	}

	.user-email {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.footer-actions {
		display: flex;
		gap: 0.5rem;
	}

	.main-content {
		flex: 1;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		background-color: var(--color-field-void);
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.sidebar {
			position: fixed;
			left: 0;
			top: 0;
			bottom: 0;
			z-index: 50;
			transform: translateX(-100%);
			transition: transform 0.3s ease;
		}

		.sidebar.open {
			transform: translateX(0);
		}

		.main-content {
			margin-left: 0;
		}
	}
</style>
