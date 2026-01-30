<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { auth, isAuthenticated, user, theme, addToast } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';

	let isLoading = true;
	let mobileMenuOpen = false;
	let userMenuOpen = false;

	onMount(async () => {
		const currentUser = await auth.loadUser();
		if (!currentUser) {
			goto('/login');
			return;
		}
		isLoading = false;
	});

	// Close mobile menu on navigation
	$: if ($page.url.pathname) {
		mobileMenuOpen = false;
		userMenuOpen = false;
	}

	async function handleLogout() {
		await auth.logout();
		addToast('info', 'Signed out', 'You have been logged out');
		goto('/login');
	}

	function toggleTheme() {
		theme.toggle();
	}

	function toggleMobileMenu() {
		mobileMenuOpen = !mobileMenuOpen;
	}

	function closeMobileMenu() {
		mobileMenuOpen = false;
	}

	function toggleUserMenu() {
		userMenuOpen = !userMenuOpen;
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
		<!-- Mobile header -->
		<header class="mobile-header">
			<button class="hamburger-btn" on:click={toggleMobileMenu} aria-label="Toggle menu">
				{#if mobileMenuOpen}
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M18 6 6 18" />
						<path d="m6 6 12 12" />
					</svg>
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="4" x2="20" y1="12" y2="12" />
						<line x1="4" x2="20" y1="6" y2="6" />
						<line x1="4" x2="20" y1="18" y2="18" />
					</svg>
				{/if}
			</button>
			<h1 class="mobile-logo">Reality Transformer</h1>
			<div class="mobile-actions">
				<button class="mobile-icon-btn" on:click={toggleTheme} title="Toggle theme">
					{#if $theme.isDark}
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
						</svg>
					{/if}
				</button>
			</div>
		</header>

		<!-- Mobile overlay -->
		{#if mobileMenuOpen}
			<div class="mobile-overlay" on:click={closeMobileMenu} role="presentation"></div>
		{/if}

		<!-- Sidebar -->
		<aside class="sidebar" class:open={mobileMenuOpen}>
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
							<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
						</svg>
						<span>Admin</span>
					</a>
				{/if}
			</nav>

			<!-- User menu section -->
			<div class="sidebar-footer">
				<!-- User avatar button -->
				<button class="user-avatar-btn" on:click={toggleUserMenu} class:active={userMenuOpen}>
					<div class="user-avatar">
						{$user?.name?.[0] || $user?.email?.[0] || 'U'}
					</div>
					<div class="user-details">
						<span class="user-name">{$user?.name || 'User'}</span>
						<span class="user-email">{$user?.email}</span>
					</div>
					<svg
						class="chevron"
						class:rotated={userMenuOpen}
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
						<path d="m6 9 6 6 6-6" />
					</svg>
				</button>

				<!-- Collapsible user menu -->
				{#if userMenuOpen}
					<div class="user-menu">
						<a href="/documents" class="user-menu-item">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="18"
								height="18"
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
						<a href="/settings" class="user-menu-item">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="18"
								height="18"
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
						<button class="user-menu-item" on:click={toggleTheme}>
							{#if $theme.isDark}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="18"
									height="18"
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
								<span>Light Mode</span>
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
								</svg>
								<span>Dark Mode</span>
							{/if}
						</button>
						<div class="user-menu-divider"></div>
						<button class="user-menu-item logout" on:click={handleLogout}>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="18"
								height="18"
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
							<span>Sign Out</span>
						</button>
					</div>
				{/if}
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

	/* Sidebar footer / User menu */
	.sidebar-footer {
		padding: 0.75rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	.user-avatar-btn {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.625rem;
		background: none;
		border: none;
		border-radius: 0.625rem;
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
	}

	.user-avatar-btn:hover,
	.user-avatar-btn.active {
		background: var(--color-field-depth);
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
		flex-shrink: 0;
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

	.chevron {
		color: var(--color-text-whisper);
		transition: transform 0.2s ease;
		flex-shrink: 0;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	/* User menu dropdown */
	.user-menu {
		margin-top: 0.5rem;
		padding: 0.375rem;
		background: var(--color-field-depth);
		border-radius: 0.625rem;
		animation: slideDown 0.15s ease;
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.user-menu-item {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		width: 100%;
		padding: 0.625rem 0.75rem;
		background: none;
		border: none;
		border-radius: 0.5rem;
		color: var(--color-text-manifest);
		text-decoration: none;
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
	}

	.user-menu-item:hover {
		background: var(--color-field-surface);
		color: var(--color-text-source);
	}

	.user-menu-item.logout {
		color: var(--color-error-500);
	}

	.user-menu-item.logout:hover {
		background: var(--color-error-50);
		color: var(--color-error-600);
	}

	[data-theme='dark'] .user-menu-item.logout:hover {
		background: rgba(239, 68, 68, 0.1);
	}

	.user-menu-divider {
		height: 1px;
		background: var(--color-veil-thin);
		margin: 0.375rem 0.5rem;
	}

	.main-content {
		flex: 1;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		background-color: var(--color-field-void);
	}

	/* Mobile header */
	.mobile-header {
		display: none;
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 56px;
		background: var(--color-field-surface);
		border-bottom: 1px solid var(--color-veil-thin);
		padding: 0 1rem;
		align-items: center;
		justify-content: space-between;
		z-index: 40;
	}

	.hamburger-btn {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		border: none;
		color: var(--color-text-source);
		cursor: pointer;
		border-radius: 0.5rem;
		transition: background-color 0.15s ease;
	}

	.hamburger-btn:hover {
		background: var(--color-field-depth);
	}

	.mobile-logo {
		font-size: 1rem;
		font-weight: 700;
		background: var(--gradient-primary);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.mobile-actions {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.mobile-icon-btn {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		border: none;
		color: var(--color-text-manifest);
		cursor: pointer;
		border-radius: 0.5rem;
		transition: all 0.15s ease;
	}

	.mobile-icon-btn:hover {
		background: var(--color-field-depth);
		color: var(--color-text-source);
	}

	.mobile-overlay {
		display: none;
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		z-index: 45;
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.mobile-header {
			display: flex;
		}

		.mobile-overlay {
			display: block;
		}

		.app-layout {
			padding-top: 56px;
		}

		.sidebar {
			position: fixed;
			left: 0;
			top: 0;
			bottom: 0;
			z-index: 50;
			transform: translateX(-100%);
			transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
			box-shadow: none;
		}

		.sidebar.open {
			transform: translateX(0);
			box-shadow: var(--shadow-lg);
		}

		.sidebar-header {
			padding-top: 1.5rem;
		}

		.main-content {
			margin-left: 0;
		}
	}

	/* Touch target optimization */
	@media (pointer: coarse) {
		.nav-item {
			min-height: 48px;
		}

		.user-menu-item {
			min-height: 44px;
		}
	}
</style>
