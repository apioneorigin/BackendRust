<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { theme, addToast, chat, conversations, currentConversation, messages } from '$lib/stores';
	import type { LayoutData } from './$types';

	export let data: LayoutData;

	// User guaranteed by hooks.server.ts guard - no fallback
	$: user = data.user;

	let mobileMenuOpen = false;
	let userMenuOpen = false;
	let sidebarCollapsed = false;
	let activeOptionsMenu: string | null = null;

	// Close menus on navigation
	$: if ($page.url.pathname) {
		mobileMenuOpen = false;
		userMenuOpen = false;
	}

	async function handleLogout() {
		// Call logout endpoint to clear cookie
		await fetch('/logout', { method: 'POST' });
		addToast('info', 'Signed out', 'You have been logged out');
		goto('/login');
	}

	function handleNewChat() {
		// Don't create conversation yet - just navigate to welcome page
		// Conversation will be created when user sends first message
		const isOnChatPage = $page.url.pathname === '/chat';

		if (isOnChatPage && $messages.length === 0 && !$currentConversation) {
			// Already on welcome page with no conversation - do nothing
			return;
		}

		chat.clearCurrentConversation();
		if (!isOnChatPage) {
			goto('/chat');
		}
	}

	async function handleSelectConversation(conversationId: string) {
		// Store handles cancellation of in-flight requests (no guard needed)
		if ($currentConversation?.id === conversationId) return;

		// Navigate first for instant feedback, then load data
		if (!$page.url.pathname.startsWith('/chat')) {
			goto('/chat');
		}
		await chat.selectConversation(conversationId);
	}

	function formatConversationDate(date: Date | string | undefined): string {
		if (!date) return '';
		try {
			const d = typeof date === 'string' ? new Date(date) : date;
			if (isNaN(d.getTime())) return '';
			const now = new Date();
			const diff = now.getTime() - d.getTime();
			const days = Math.floor(diff / (1000 * 60 * 60 * 24));

			if (days === 0) return 'Today';
			if (days === 1) return 'Yesterday';
			if (days < 7) return `${days} days ago`;
			return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		} catch {
			return '';
		}
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

	function toggleSidebar() {
		sidebarCollapsed = !sidebarCollapsed;
	}

	function toggleOptionsMenu(e: Event, conversationId: string) {
		e.stopPropagation();
		activeOptionsMenu = activeOptionsMenu === conversationId ? null : conversationId;
	}

	function closeOptionsMenu() {
		activeOptionsMenu = null;
	}

	async function handleDeleteConversation(e: Event, conversationId: string) {
		e.stopPropagation();
		activeOptionsMenu = null;

		try {
			await chat.deleteConversation(conversationId);
			addToast('success', 'Chat deleted');
		} catch (error: any) {
			addToast('error', error.message || 'Failed to delete chat');
		}
	}

	function handleShareConversation(e: Event, conversationId: string) {
		e.stopPropagation();
		activeOptionsMenu = null;

		const shareUrl = `${window.location.origin}/chat/${conversationId}`;
		navigator.clipboard.writeText(shareUrl).then(() => {
			addToast('success', 'Link copied to clipboard');
		}).catch(() => {
			addToast('error', 'Failed to copy link');
		});
	}
</script>

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

		<!-- Collapsible Sidebar (consistent across all pages) -->
		<aside class="sidebar" class:collapsed={sidebarCollapsed} class:open={mobileMenuOpen}>
			<!-- Sidebar header with logo and collapse toggle -->
			<div class="sidebar-header">
				{#if !sidebarCollapsed}
					<h2 class="logo">Reality Transformer</h2>
				{/if}
				<button class="collapse-btn" on:click={toggleSidebar} title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class:rotated={sidebarCollapsed}>
						<path d="m15 18-6-6 6-6"/>
					</svg>
				</button>
			</div>

			<!-- New Chat button -->
			<div class="new-chat-section">
				<button class="new-chat-btn" on:click={handleNewChat} title="New Chat">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M12 5v14"/>
						<path d="M5 12h14"/>
					</svg>
					{#if !sidebarCollapsed}<span>New Chat</span>{/if}
				</button>
			</div>

			<!-- Conversation list -->
			<div class="conversations-section">
				{#if !sidebarCollapsed}
					<div class="conversations-header">
						<span>Conversations</span>
					</div>
				{/if}
				<div class="conversations-list">
					{#each $conversations as conversation (conversation.id)}
						<div class="conversation-row" class:active={$currentConversation?.id === conversation.id}>
							<button
								type="button"
								class="conversation-item"
								class:active={$currentConversation?.id === conversation.id}
								disabled={isSelectingConversation}
								on:click|preventDefault|stopPropagation={() => handleSelectConversation(conversation.id)}
								title={conversation.title || 'New Chat'}
							>
								<span class="conversation-title">{conversation.title || 'New Chat'}</span>
							</button>
							{#if !sidebarCollapsed}
								<button
									class="options-btn"
									on:click={(e) => toggleOptionsMenu(e, conversation.id)}
									title="Options"
								>
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="m6 9 6 6 6-6"/>
									</svg>
								</button>
								{#if activeOptionsMenu === conversation.id}
									<div class="options-dropdown">
										<button class="option-item" on:click={(e) => handleShareConversation(e, conversation.id)}>
											<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
												<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
												<polyline points="16 6 12 2 8 6"/>
												<line x1="12" x2="12" y1="2" y2="15"/>
											</svg>
											<span>Share link</span>
										</button>
										<button class="option-item delete" on:click={(e) => handleDeleteConversation(e, conversation.id)}>
											<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
												<path d="M3 6h18"/>
												<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
												<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
											</svg>
											<span>Delete</span>
										</button>
									</div>
								{/if}
							{/if}
						</div>
					{:else}
						{#if !sidebarCollapsed}
							<div class="no-conversations">
								<p>No conversations yet</p>
							</div>
						{/if}
					{/each}
				</div>
			</div>

			<!-- Navigation (Admin only - other links in user menu) -->
			<nav class="sidebar-nav">
				{#if user?.isGlobalAdmin}
					<a href="/admin" class="nav-item" class:active={$page.url.pathname.startsWith('/admin')} title="Admin">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
						</svg>
						{#if !sidebarCollapsed}<span>Admin</span>{/if}
					</a>
				{/if}
			</nav>

			<!-- User menu section at bottom -->
			<div class="sidebar-footer">
				<button class="user-avatar-btn" on:click={toggleUserMenu} class:active={userMenuOpen} title={user?.name || 'User menu'}>
					<div class="user-avatar">
						{user?.name?.[0] || user?.email?.[0] || 'U'}
					</div>
					{#if !sidebarCollapsed}
						<span class="user-first-name">{user?.name?.trim().split(/\s+/)[0] || 'User'}</span>
						<svg class="chevron" class:rotated={userMenuOpen} xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="m6 15 6-6 6 6" />
						</svg>
					{/if}
				</button>

				<!-- User menu dropdown (always shows labels - it's a popup when collapsed) -->
				{#if userMenuOpen}
					<div class="user-menu" class:collapsed-menu={sidebarCollapsed}>
						<a href="/goals" class="user-menu-item">
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<circle cx="12" cy="12" r="10" />
								<circle cx="12" cy="12" r="6" />
								<circle cx="12" cy="12" r="2" />
							</svg>
							<span>Goal Discovery</span>
						</a>
						<a href="/documents" class="user-menu-item">
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
								<polyline points="14 2 14 8 20 8" />
							</svg>
							<span>Documents</span>
						</a>
						<a href="/settings" class="user-menu-item">
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
								<circle cx="12" cy="12" r="3" />
							</svg>
							<span>Settings</span>
						</a>
						<div class="user-menu-divider"></div>
						<button class="user-menu-item" on:click={toggleTheme}>
							{#if $theme.isDark}
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<circle cx="12" cy="12" r="4" />
									<path d="M12 2v2" /><path d="M12 20v2" />
									<path d="m4.93 4.93 1.41 1.41" /><path d="m17.66 17.66 1.41 1.41" />
									<path d="M2 12h2" /><path d="M20 12h2" />
									<path d="m6.34 17.66-1.41 1.41" /><path d="m19.07 4.93-1.41 1.41" />
								</svg>
								<span>Light Mode</span>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
								</svg>
								<span>Dark Mode</span>
							{/if}
						</button>
						<div class="user-menu-divider"></div>
						<button class="user-menu-item logout" on:click={handleLogout}>
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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

	<!-- Main content (shifts with sidebar) -->
	<main class="main-content">
		<slot />
	</main>
</div>

<style>
	.app-layout {
		display: flex;
		height: 100dvh;
		overflow: hidden;
	}

	/* Sidebar - minimal */
	.sidebar {
		width: 240px;
		min-width: 240px;
		height: 100dvh;
		background: var(--color-field-surface);
		border-right: 1px solid var(--color-veil-thin);
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
		transition: width 0.15s ease, min-width 0.15s ease;
		overflow: hidden;
	}

	.sidebar.collapsed {
		width: 56px;
		min-width: 56px;
	}

	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem;
		gap: 0.5rem;
	}

	.sidebar.collapsed .sidebar-header {
		justify-content: center;
		padding: 1rem 0.5rem;
	}

	.logo {
		font-family: var(--font-heading);
		font-size: 18px;
		font-weight: 600;
		color: var(--color-primary-500);
		white-space: nowrap;
		overflow: hidden;
		letter-spacing: -0.02em;
	}

	.collapse-btn {
		width: 28px;
		height: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		color: var(--color-text-hint);
		cursor: pointer;
		border-radius: 0.25rem;
		transition: all 0.1s ease;
		flex-shrink: 0;
	}

	.collapse-btn:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.collapse-btn svg.rotated {
		transform: rotate(180deg);
	}

	/* New Chat button - transparent with border (matches matrix toolbar) */
	.new-chat-section {
		padding: 0 0.75rem 0.5rem;
	}

	.new-chat-btn {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 0.75rem;
		background: transparent;
		border: 1px solid var(--color-accent);
		border-radius: 0.5rem;
		color: var(--color-accent);
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.new-chat-btn:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.new-chat-btn svg {
		color: var(--color-accent);
	}

	.new-chat-btn:hover svg {
		color: var(--color-text-source);
	}

	.sidebar.collapsed .new-chat-btn {
		width: 40px;
		height: 40px;
		padding: 0;
		justify-content: center;
		border: 1px solid var(--color-accent);
		background: transparent;
	}

	.sidebar.collapsed .new-chat-btn:hover {
		background: var(--color-accent-subtle);
	}

	.sidebar.collapsed .new-chat-btn span {
		display: none;
	}

	/* Hide conversations and user menu when collapsed - like Claude Code */
	.sidebar.collapsed .conversations-section {
		display: none;
	}

	.sidebar.collapsed .sidebar-footer {
		display: none;
	}

	/* Navigation */
	.sidebar-nav {
		padding: 0.5rem 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.nav-item {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.5rem 0.625rem;
		border-radius: 0.375rem;
		color: var(--color-text-manifest);
		text-decoration: none;
		transition: all 0.1s ease;
		font-weight: 400;
		font-size: 15px;
	}

	.sidebar.collapsed .nav-item {
		justify-content: center;
		padding: 0.5rem;
	}

	.nav-item:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.nav-item.active {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.nav-item svg {
		flex-shrink: 0;
	}

	/* Conversations section */
	.conversations-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		padding: 0 0.75rem;
	}

	.conversations-header {
		padding: 0.75rem 0.5rem 0.5rem;
		font-size: 13px;
		font-weight: 500;
		color: var(--color-text-whisper);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.conversations-list {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	/* Conversation row wrapper */
	.conversation-row {
		position: relative;
		display: flex;
		align-items: center;
		border-radius: 0.375rem;
	}

	.conversation-row:hover {
		background: var(--color-accent-subtle);
	}

	.conversation-row.active {
		background: var(--color-accent-subtle);
	}

	.conversation-item {
		flex: 1;
		min-width: 0;
		display: flex;
		align-items: center;
		padding: 0.5rem 0.625rem;
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		text-align: left;
		transition: all 0.1s ease;
		color: var(--color-text-manifest);
	}

	.sidebar.collapsed .conversation-item {
		justify-content: center;
		padding: 0.5rem;
	}

	.conversation-row:hover .conversation-item,
	.conversation-item.active {
		color: var(--color-text-source);
	}

	.conversation-item:disabled {
		opacity: 0.4;
		cursor: wait;
	}

	.conversation-title {
		font-size: 14px;
		font-weight: 400;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	/* Options button - appears on hover */
	.options-btn {
		position: absolute;
		right: 0.375rem;
		opacity: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		padding: 0;
		background: var(--color-field-surface);
		border: none;
		border-radius: 0.25rem;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: opacity 0.1s ease;
	}

	.conversation-row:hover .options-btn {
		opacity: 1;
	}

	.options-btn:hover {
		background: var(--color-veil-present);
		color: var(--color-text-source);
	}

	/* Options dropdown */
	.options-dropdown {
		position: absolute;
		top: 100%;
		right: 0;
		z-index: 50;
		min-width: 140px;
		padding: 0.25rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		box-shadow: var(--shadow-elevated);
	}

	.option-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.5rem 0.625rem;
		background: transparent;
		border: none;
		border-radius: 0.25rem;
		font-size: 13px;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.1s ease;
		text-align: left;
	}

	.option-item:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.option-item.delete:hover {
		background: var(--color-error-50);
		color: var(--color-error-500);
	}

	.option-item svg {
		flex-shrink: 0;
	}

	.no-conversations {
		padding: 1.5rem 0.5rem;
		text-align: center;
	}

	.no-conversations p {
		font-size: 14px;
		color: var(--color-text-whisper);
	}

	/* Sidebar footer / User menu - aligned with input panel controls border */
	.sidebar-footer {
		padding: 0 0.75rem 2.25rem 0.75rem; /* No top padding - border aligns with controls-row border */
		margin-top: auto;
		position: relative;
		border-top: 1px solid var(--color-veil-thin);
	}

	.user-avatar-btn {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.5rem;
		min-height: 44px; /* Match controls-row height */
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.1s ease;
		text-align: left;
	}

	.sidebar.collapsed .user-avatar-btn {
		justify-content: center;
	}

	.user-avatar-btn:hover,
	.user-avatar-btn.active {
		background: var(--color-accent-subtle);
	}

	.user-avatar {
		width: 28px;
		height: 28px;
		background: var(--color-primary-500);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #ffffff;
		font-weight: 600;
		font-size: 13px;
		flex-shrink: 0;
	}

	.user-first-name {
		flex: 1;
		font-weight: 500;
		font-size: 15px;
		color: var(--color-text-source);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.chevron {
		color: var(--color-text-whisper);
		transition: transform 0.2s ease;
		flex-shrink: 0;
		margin-left: auto;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	/* User menu dropdown */
	.user-menu {
		margin-top: 0.5rem;
		padding: 0.375rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
		animation: slideUp 0.15s ease;
	}

	.user-menu.collapsed-menu {
		position: absolute;
		bottom: 100%;
		left: 0;
		margin-bottom: 0.5rem;
		width: 180px;
		box-shadow: var(--shadow-elevated);
		z-index: 100;
		background: var(--color-field-surface);
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(8px);
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
		padding: 0.5rem 0.625rem;
		background: none;
		border: none;
		border-radius: 0.375rem;
		color: var(--color-text-manifest);
		text-decoration: none;
		font-size: 15px;
		font-weight: 400;
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
	}

	.user-menu-item:hover {
		background: var(--color-field-surface);
		color: var(--color-text-source);
	}

	.collapsed-menu .user-menu-item:hover {
		background: var(--color-field-depth);
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
		background: var(--color-field-void);
		margin: 0.375rem 0.625rem;
	}

	/* Main content */
	.main-content {
		flex: 1;
		min-width: 0;
		min-height: 0;
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
		box-shadow: var(--shadow-sm);
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
		color: var(--color-primary-500);
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
			width: 260px;
			min-width: 260px;
		}

		.sidebar.collapsed {
			width: 260px;
			min-width: 260px;
		}

		.sidebar.open {
			transform: translateX(0);
			box-shadow: var(--shadow-lg);
		}

		.sidebar-header {
			padding-top: 1.5rem;
		}

		.collapse-btn {
			display: none;
		}

		.sidebar.collapsed .sidebar-header {
			justify-content: flex-start;
			padding: 1.5rem 1rem 1rem;
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
