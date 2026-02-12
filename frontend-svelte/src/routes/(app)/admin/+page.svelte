<script lang="ts">
	import { onMount } from 'svelte';
	import { user, addToast } from '$lib/stores';
	import { Button, Card, Spinner } from '$lib/components/ui';
	import { api } from '$lib/utils/api';

	// --- Interfaces ---
	interface DashboardStats {
		totalUsers: number;
		totalOrganizations: number;
		totalSessions: number;
		totalConversations: number;
		activeUsers30d: number;
		apiCallsToday: number;
	}

	interface UserListItem {
		id: string;
		email: string;
		name: string | null;
		role: string;
		organizationId: string;
		creditsEnabled: boolean;
		creditQuota: number | null;
		createdAt: string;
		lastLoginAt: string | null;
	}

	interface PromoCode {
		id: string;
		code: string;
		credits: number;
		maxUses: number;
		usedCount: number;
		createdBy: string;
		createdAt: string;
		expiresAt: string | null;
		isActive: boolean;
	}

	interface GlobalSettings {
		freeTrialCredits: number;
		trialDurationDays: number;
		updatedAt: string;
		updatedBy: string | null;
	}

	// --- State ---
	let isLoading = true;
	let isRefreshing = false;
	let stats: DashboardStats | null = null;
	let users: UserListItem[] = [];
	let promoCodes: PromoCode[] = [];
	let settings: GlobalSettings | null = null;
	let selectedTab: 'overview' | 'users' | 'promo-codes' | 'settings' = 'overview';

	// Promo code form state
	let newPromoCode = '';
	let newPromoCredits = 100;
	let newPromoMaxUses = 1;
	let newPromoExpires = '';
	let isCreatingPromo = false;

	// User credit editing state
	let editingUserId: string | null = null;
	let editCreditValue = 0;
	let isSavingCredits = false;

	// Settings form state
	let settingsFreeTrialCredits = 0;
	let settingsTrialDays = 14;
	let isSavingSettings = false;

	// Loading states for individual tabs
	let isLoadingPromos = false;
	let isLoadingSettings = false;

	onMount(async () => {
		await loadDashboard();
	});

	async function loadDashboard() {
		const isInitialLoad = stats === null && users.length === 0;
		if (isInitialLoad) {
			isLoading = true;
		} else {
			isRefreshing = true;
		}
		try {
			const [dashboardData, usersData] = await Promise.all([
				api.get<DashboardStats>('/api/admin/dashboard'),
				api.get<{ users: UserListItem[] }>('/api/admin/users/list')
			]);
			stats = dashboardData;
			users = usersData.users || [];
		} catch (error: any) {
			addToast('error', error.message || 'Failed to load dashboard');
		} finally {
			isLoading = false;
			isRefreshing = false;
		}
	}

	// --- Promo code functions ---
	async function loadPromoCodes() {
		isLoadingPromos = true;
		try {
			promoCodes = await api.get<PromoCode[]>('/api/admin/promo-codes');
		} catch (error: any) {
			addToast('error', error.message || 'Failed to load promo codes');
		} finally {
			isLoadingPromos = false;
		}
	}

	async function createPromoCode(e: Event) {
		e.preventDefault();
		if (!newPromoCode.trim()) {
			addToast('warning', 'Please enter a promo code');
			return;
		}
		if (newPromoCredits <= 0) {
			addToast('warning', 'Credits must be greater than 0');
			return;
		}

		isCreatingPromo = true;
		try {
			const body: any = {
				code: newPromoCode.trim().toUpperCase(),
				credits: newPromoCredits,
				max_uses: newPromoMaxUses
			};
			if (newPromoExpires) {
				body.expires_at = new Date(newPromoExpires).toISOString();
			}
			await api.post('/api/admin/promo-codes', body);
			addToast('success', `Promo code "${body.code}" created`);
			newPromoCode = '';
			newPromoCredits = 100;
			newPromoMaxUses = 1;
			newPromoExpires = '';
			await loadPromoCodes();
		} catch (error: any) {
			addToast('error', error.message || 'Failed to create promo code');
		} finally {
			isCreatingPromo = false;
		}
	}

	async function togglePromoCode(code: PromoCode) {
		try {
			await api.patch(`/api/admin/promo-codes/${code.id}`, {
				is_active: !code.isActive
			});
			addToast('success', `Promo code ${code.isActive ? 'deactivated' : 'activated'}`);
			await loadPromoCodes();
		} catch (error: any) {
			addToast('error', error.message || 'Failed to update promo code');
		}
	}

	// --- User credit functions ---
	function startEditCredits(userItem: UserListItem) {
		editingUserId = userItem.id;
		editCreditValue = userItem.creditQuota ?? 0;
	}

	function cancelEditCredits() {
		editingUserId = null;
		editCreditValue = 0;
	}

	async function saveUserCredits(userItem: UserListItem) {
		isSavingCredits = true;
		try {
			await api.patch(`/api/admin/users/${userItem.id}/credits?credits=${editCreditValue}`);
			addToast('success', `Credits updated for ${userItem.email}`);
			// Update local state
			const idx = users.findIndex(u => u.id === userItem.id);
			if (idx >= 0) {
				users[idx] = { ...users[idx], creditQuota: editCreditValue };
				users = users;
			}
			editingUserId = null;
		} catch (error: any) {
			addToast('error', error.message || 'Failed to update credits');
		} finally {
			isSavingCredits = false;
		}
	}

	// --- Settings functions ---
	async function loadSettings() {
		isLoadingSettings = true;
		try {
			settings = await api.get<GlobalSettings>('/api/admin/settings');
			settingsFreeTrialCredits = settings.freeTrialCredits;
			settingsTrialDays = settings.trialDurationDays;
		} catch (error: any) {
			addToast('error', error.message || 'Failed to load settings');
		} finally {
			isLoadingSettings = false;
		}
	}

	async function saveSettings(e: Event) {
		e.preventDefault();
		isSavingSettings = true;
		try {
			settings = await api.patch<GlobalSettings>('/api/admin/settings', {
				free_trial_credits: settingsFreeTrialCredits,
				trial_duration_days: settingsTrialDays
			});
			addToast('success', 'Settings saved');
		} catch (error: any) {
			addToast('error', error.message || 'Failed to save settings');
		} finally {
			isSavingSettings = false;
		}
	}

	// --- Tab switching ---
	function switchTab(tab: typeof selectedTab) {
		selectedTab = tab;
		if (tab === 'promo-codes' && promoCodes.length === 0) {
			loadPromoCodes();
		}
		if (tab === 'settings' && !settings) {
			loadSettings();
		}
	}

	// --- Helpers ---
	function formatNumber(num: number): string {
		if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
		if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
		return num.toString();
	}

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return 'Never';
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function formatDateTime(dateStr: string | null): string {
		if (!dateStr) return 'Never';
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function handlePromoCodeInput(e: Event) {
		const target = e.target as HTMLInputElement;
		newPromoCode = target.value.toUpperCase();
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
		<Button variant="outline" on:click={loadDashboard} disabled={isRefreshing}>
			{#if isRefreshing}
				<Spinner size="sm" />
			{:else}
				<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
					<path d="M3 3v5h5" />
					<path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
					<path d="M16 16h5v5" />
				</svg>
			{/if}
			{isRefreshing ? 'Refreshing...' : 'Refresh'}
		</Button>
	</div>

	<!-- Tabs -->
	<div class="tabs">
		<button class="tab" class:active={selectedTab === 'overview'} on:click={() => switchTab('overview')}>Overview</button>
		<button class="tab" class:active={selectedTab === 'users'} on:click={() => switchTab('users')}>Users</button>
		<button class="tab" class:active={selectedTab === 'promo-codes'} on:click={() => switchTab('promo-codes')}>Promo Codes</button>
		<button class="tab" class:active={selectedTab === 'settings'} on:click={() => switchTab('settings')}>Settings</button>
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
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
								<circle cx="9" cy="7" r="4" />
								<path d="M22 21v-2a4 4 0 0 0-3-3.87" />
								<path d="M16 3.13a4 4 0 0 1 0 7.75" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalUsers ?? 0)}</span>
							<span class="stat-label">Total Users</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon active">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M22 12h-4l-3 9L9 3l-3 9H2" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.activeUsers30d ?? 0)}</span>
							<span class="stat-label">Active (30d)</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon conversations">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalConversations ?? 0)}</span>
							<span class="stat-label">Conversations</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon sessions">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<rect width="18" height="18" x="3" y="3" rx="2" />
								<path d="M3 9h18" />
								<path d="M9 21V9" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalSessions ?? 0)}</span>
							<span class="stat-label">Sessions</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon orgs">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M18 21H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2z" />
								<path d="m10 7 5 5-5 5" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.totalOrganizations ?? 0)}</span>
							<span class="stat-label">Organizations</span>
						</div>
					</div>
				</Card>

				<Card variant="floating" padding="lg">
					<div class="stat-card">
						<div class="stat-icon api-calls">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M3 3v18h18" />
								<path d="m19 9-5 5-4-4-3 3" />
							</svg>
						</div>
						<div class="stat-content">
							<span class="stat-value">{formatNumber(stats?.apiCallsToday ?? 0)}</span>
							<span class="stat-label">API Calls Today</span>
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
									<th>Last Login</th>
									<th>Actions</th>
								</tr>
							</thead>
							<tbody>
								{#each users as userItem (userItem.id)}
									<tr>
										<td>
											<div class="user-cell">
												<div class="user-avatar">
													{(userItem.name?.[0] || userItem.email[0]).toUpperCase()}
												</div>
												<div class="user-info">
													<span class="user-name">{userItem.name || 'No name'}</span>
													<span class="user-email">{userItem.email}</span>
												</div>
											</div>
										</td>
										<td>
											<span class="role-badge" class:admin={userItem.role === 'ADMIN' || userItem.role === 'SUPER_ADMIN'}>
												{userItem.role}
											</span>
										</td>
										<td>
											{#if editingUserId === userItem.id}
												<div class="credit-edit">
													<input
														type="number"
														class="credit-input"
														bind:value={editCreditValue}
														min="0"
														disabled={isSavingCredits}
													/>
													<button class="action-btn save" on:click={() => saveUserCredits(userItem)} disabled={isSavingCredits}>
														{#if isSavingCredits}<Spinner size="sm" />{:else}Save{/if}
													</button>
													<button class="action-btn cancel" on:click={cancelEditCredits} disabled={isSavingCredits}>
														Cancel
													</button>
												</div>
											{:else}
												<span class="credit-value" class:zero={userItem.creditQuota === 0}>
													{userItem.creditQuota ?? 'N/A'}
												</span>
											{/if}
										</td>
										<td>{formatDate(userItem.createdAt)}</td>
										<td>{formatDate(userItem.lastLoginAt)}</td>
										<td>
											{#if editingUserId !== userItem.id}
												<Button variant="ghost" size="sm" on:click={() => startEditCredits(userItem)}>
													Edit Credits
												</Button>
											{/if}
										</td>
									</tr>
								{:else}
									<tr>
										<td colspan="6" class="empty-state">
											<p>No users found</p>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</Card>
			</div>
		{/if}

		<!-- Promo Codes Tab -->
		{#if selectedTab === 'promo-codes'}
			<div class="promo-section">
				<!-- Create promo code form -->
				<Card variant="floating" padding="lg">
					<h3 class="section-title">Create Promo Code</h3>
					<form on:submit={createPromoCode} class="promo-form">
						<div class="form-grid">
							<div class="form-group">
								<label for="promoCode">Code</label>
								<input
									id="promoCode"
									type="text"
									value={newPromoCode}
									on:input={handlePromoCodeInput}
									placeholder="WELCOME100"
									disabled={isCreatingPromo}
									autocomplete="off"
								/>
							</div>
							<div class="form-group">
								<label for="promoCredits">Credits</label>
								<input
									id="promoCredits"
									type="number"
									bind:value={newPromoCredits}
									min="1"
									placeholder="100"
									disabled={isCreatingPromo}
								/>
							</div>
							<div class="form-group">
								<label for="promoMaxUses">Max Uses</label>
								<input
									id="promoMaxUses"
									type="number"
									bind:value={newPromoMaxUses}
									min="1"
									placeholder="1"
									disabled={isCreatingPromo}
								/>
							</div>
							<div class="form-group">
								<label for="promoExpires">Expires (optional)</label>
								<input
									id="promoExpires"
									type="date"
									bind:value={newPromoExpires}
									disabled={isCreatingPromo}
								/>
							</div>
						</div>
						<div class="form-actions">
							<Button variant="primary" type="submit" loading={isCreatingPromo} disabled={!newPromoCode.trim() || newPromoCredits <= 0}>
								Create Promo Code
							</Button>
						</div>
					</form>
				</Card>

				<!-- Promo code list -->
				<div class="promo-list-header">
					<h3 class="section-title">Existing Promo Codes</h3>
					<Button variant="ghost" size="sm" on:click={loadPromoCodes} disabled={isLoadingPromos}>
						Refresh
					</Button>
				</div>

				{#if isLoadingPromos}
					<div class="loading-state small">
						<Spinner size="md" />
					</div>
				{:else}
					<Card variant="default" padding="none">
						<div class="table-container">
							<table class="promo-table">
								<thead>
									<tr>
										<th>Code</th>
										<th>Credits</th>
										<th>Uses</th>
										<th>Created</th>
										<th>Expires</th>
										<th>Status</th>
										<th>Actions</th>
									</tr>
								</thead>
								<tbody>
									{#each promoCodes as code (code.id)}
										<tr class:inactive={!code.isActive}>
											<td><span class="code-text">{code.code}</span></td>
											<td><span class="credit-badge">+{code.credits}</span></td>
											<td>{code.usedCount} / {code.maxUses}</td>
											<td>{formatDate(code.createdAt)}</td>
											<td>{code.expiresAt ? formatDate(code.expiresAt) : 'Never'}</td>
											<td>
												<span class="status-badge" class:active={code.isActive} class:disabled={!code.isActive}>
													{code.isActive ? 'Active' : 'Inactive'}
												</span>
											</td>
											<td>
												<Button
													variant={code.isActive ? 'ghost' : 'outline'}
													size="sm"
													on:click={() => togglePromoCode(code)}
												>
													{code.isActive ? 'Deactivate' : 'Activate'}
												</Button>
											</td>
										</tr>
									{:else}
										<tr>
											<td colspan="7" class="empty-state">
												<p>No promo codes yet. Create one above.</p>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</Card>
				{/if}
			</div>
		{/if}

		<!-- Settings Tab -->
		{#if selectedTab === 'settings'}
			<div class="settings-section">
				{#if isLoadingSettings}
					<div class="loading-state small">
						<Spinner size="md" />
					</div>
				{:else}
					<Card variant="floating" padding="lg">
						<h3 class="section-title">Global Settings</h3>
						<form on:submit={saveSettings} class="settings-form">
							<div class="form-grid two-col">
								<div class="form-group">
									<label for="freeTrialCredits">Free Trial Credits</label>
									<input
										id="freeTrialCredits"
										type="number"
										bind:value={settingsFreeTrialCredits}
										min="0"
										disabled={isSavingSettings}
									/>
									<span class="form-hint">Credits given to new users on registration</span>
								</div>
								<div class="form-group">
									<label for="trialDays">Trial Duration (days)</label>
									<input
										id="trialDays"
										type="number"
										bind:value={settingsTrialDays}
										min="1"
										disabled={isSavingSettings}
									/>
									<span class="form-hint">How long the free trial period lasts</span>
								</div>
							</div>
							{#if settings}
								<div class="settings-meta">
									<span>Last updated: {formatDateTime(settings.updatedAt)}</span>
									{#if settings.updatedBy}
										<span>by {settings.updatedBy}</span>
									{/if}
								</div>
							{/if}
							<div class="form-actions">
								<Button variant="primary" type="submit" loading={isSavingSettings}>
									Save Settings
								</Button>
							</div>
						</form>
					</Card>
				{/if}
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

	/* Tabs */
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

	/* Loading states */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem;
		gap: 1rem;
		color: var(--color-text-whisper);
	}

	.loading-state.small {
		padding: 2rem;
	}

	/* Stats grid */
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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

	.stat-icon.users { background: var(--color-primary-100); color: var(--color-primary-600); }
	.stat-icon.active { background: #d1fae5; color: #059669; }
	.stat-icon.conversations { background: rgba(6, 182, 212, 0.1); color: #0891b2; }
	.stat-icon.sessions { background: #fce7f3; color: #db2777; }
	.stat-icon.orgs { background: #fef3c7; color: #d97706; }
	.stat-icon.api-calls { background: #ede9fe; color: #7c3aed; }

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

	/* Tables shared */
	.table-container {
		overflow-x: auto;
	}

	.users-table,
	.promo-table {
		width: 100%;
		border-collapse: collapse;
	}

	.users-table th,
	.users-table td,
	.promo-table th,
	.promo-table td {
		padding: 0.875rem 1rem;
		text-align: left;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.users-table th,
	.promo-table th {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-whisper);
		background: var(--color-field-depth);
	}

	/* User cells */
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

	/* Credit editing */
	.credit-value {
		font-weight: 500;
		color: var(--color-text-manifest);
	}

	.credit-value.zero {
		color: var(--color-error-500, #ef4444);
	}

	.credit-edit {
		display: flex;
		align-items: center;
		gap: 0.375rem;
	}

	.credit-input {
		width: 80px;
		padding: 0.375rem 0.5rem;
		font-size: 0.875rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
	}

	.credit-input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.action-btn {
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		white-space: nowrap;
	}

	.action-btn.save {
		background: var(--color-primary-500);
		color: white;
	}

	.action-btn.save:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.action-btn.cancel {
		background: var(--color-field-depth);
		color: var(--color-text-manifest);
	}

	.action-btn.cancel:hover:not(:disabled) {
		background: var(--color-field-elevated);
	}

	.action-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Promo codes section */
	.promo-section {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.section-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 1rem;
	}

	.promo-list-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.promo-list-header .section-title {
		margin-bottom: 0;
	}

	.promo-form .form-grid,
	.settings-form .form-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.settings-form .form-grid.two-col {
		grid-template-columns: repeat(2, 1fr);
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.form-group label {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-manifest);
	}

	.form-group input {
		padding: 0.625rem 0.75rem;
		font-size: 0.875rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
	}

	.form-group input::placeholder {
		color: var(--color-text-hint);
	}

	.form-group input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.form-group input:disabled {
		opacity: 0.6;
	}

	.form-hint {
		font-size: 0.75rem;
		color: var(--color-text-hint);
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
	}

	/* Promo table specific */
	.code-text {
		font-family: monospace;
		font-weight: 600;
		color: var(--color-text-source);
		letter-spacing: 0.025em;
	}

	.credit-badge {
		font-weight: 600;
		color: var(--color-success-500, #22c55e);
	}

	.status-badge {
		padding: 0.25rem 0.625rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.status-badge.active {
		background: rgba(34, 197, 94, 0.1);
		color: #16a34a;
	}

	.status-badge.disabled {
		background: rgba(239, 68, 68, 0.1);
		color: #dc2626;
	}

	tr.inactive {
		opacity: 0.6;
	}

	/* Settings section */
	.settings-section {
		max-width: 600px;
	}

	.settings-meta {
		display: flex;
		gap: 0.5rem;
		font-size: 0.75rem;
		color: var(--color-text-hint);
		margin-bottom: 1rem;
	}

	/* Empty state */
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-text-whisper);
	}

	.empty-state p {
		font-size: 0.875rem;
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

		.settings-form .form-grid.two-col {
			grid-template-columns: 1fr;
		}

		.credit-edit {
			flex-wrap: wrap;
		}
	}
</style>
