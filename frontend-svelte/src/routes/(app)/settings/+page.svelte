<script lang="ts">
	/**
	 * Settings Page - Redesigned Mobile-First UI
	 *
	 * Matches reality-transformer design principles:
	 * - Mobile-first with responsive breakpoints
	 * - Primary color system
	 * - Consistent border radius
	 * - Touch-friendly targets (min 48px)
	 */

	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user, credits, creditBalance, isLoadingCreditHistory, addToast } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';
	import { api } from '$lib/utils/api';

	// Types
	interface TeamMember {
		id: string;
		email: string;
		name: string | null;
		role: string;
		credits: number;
		creditsEnabled: boolean;
		creditQuota: number;
		createdAt: string;
		lastLoginAt: string | null;
	}

	interface OrganizationInfo {
		id: string;
		creditsPool: number;
		usedCredits: number;
		totalAllocated: number;
		availableForAllocation: number;
	}

	interface UsageEntry {
		date: string;
		operation: string;
		cost: number;
		balance: number;
	}

	interface CreditTransaction {
		id: string;
		type: 'redeemed' | 'spent';
		amount: number;
		description: string;
		createdAt: string;
	}

	// State
	let userRole: string | null = null;
	let userCredits = 0;
	let usageHistory: UsageEntry[] = [];
	let creditHistory: CreditTransaction[] = [];
	let showUsageHistory = false;
	let showCreditHistory = false;
	let loadingUsageHistory = false;
	let loadingCreditHistory = false;
	let promoCode = '';
	let isRedeeming = false;
	let isUpgrading = false;
	let showUpgradeModal = false;

	// Team management
	let teamMembers: TeamMember[] = [];
	let orgInfo: OrganizationInfo | null = null;
	let loadingTeam = false;
	let showCreateUserModal = false;
	let newUserEmail = '';
	let newUserName = '';
	let newUserQuota = 0;
	let isCreatingUser = false;

	// Password change
	let showPasswordModal = false;
	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';
	let isChangingPassword = false;
	let showCurrentPassword = false;
	let showNewPassword = false;
	let showConfirmPassword = false;

	$: isOrgAdmin = userRole === 'ORG_ADMIN' || userRole === 'ORG_OWNER';

	onMount(async () => {
		await fetchUserInfo();
		await credits.loadBalance();
		if ($creditBalance) {
			userCredits = $creditBalance.creditQuota || 0;
		}
	});

	async function fetchUserInfo() {
		try {
			const data = await api.get<{ role?: string; credits?: number }>('/api/auth/me');
			userRole = data.role ?? null;
			if (data.credits !== undefined) {
				userCredits = data.credits;
			}

			if (data.role === 'ORG_ADMIN' || data.role === 'ORG_OWNER') {
				loadTeamMembers();
			}
		} catch (error) {
			// Ignore errors
		}
	}

	async function loadTeamMembers() {
		loadingTeam = true;
		try {
			const data = await api.get<{
				success: boolean;
				users?: TeamMember[];
				organization?: OrganizationInfo;
				error?: string;
			}>('/api/org-admin/users/list');

			if (data.success) {
				teamMembers = data.users || [];
				orgInfo = data.organization ?? null;
			} else {
				addToast('error', data.error || 'Failed to load team members');
			}
		} catch (error) {
			// Ignore errors
		} finally {
			loadingTeam = false;
		}
	}

	async function loadUsageHistory() {
		if (showUsageHistory) {
			showUsageHistory = false;
			return;
		}

		showUsageHistory = true;
		loadingUsageHistory = true;
		try {
			const data = await api.get<{ success: boolean; history?: UsageEntry[] }>(
				'/api/credits/history'
			);
			if (data.success) {
				usageHistory = data.history || [];
			}
		} catch (error) {
			addToast('error', 'Failed to load usage history');
			showUsageHistory = false;
		} finally {
			loadingUsageHistory = false;
		}
	}

	async function loadCreditHistory() {
		if (showCreditHistory) {
			showCreditHistory = false;
			return;
		}

		showCreditHistory = true;
		loadingCreditHistory = true;
		try {
			const data = await api.get<{ success: boolean; transactions?: CreditTransaction[] }>(
				'/api/credits/history'
			);
			if (data.success) {
				creditHistory = data.transactions || [];
			}
		} catch (error) {
			addToast('error', 'Failed to load credit history');
			showCreditHistory = false;
		} finally {
			loadingCreditHistory = false;
		}
	}

	function handlePurchaseCredits(packageSize: number) {
		addToast('info', `Purchase ${packageSize} credits - Payment integration coming soon`);
	}

	async function handleRedeemPromoCode(e: Event) {
		e.preventDefault();
		if (!promoCode.trim()) {
			addToast('warning', 'Please enter a promo code');
			return;
		}

		isRedeeming = true;
		try {
			const redemption = await credits.redeemCode(promoCode.trim());
			addToast('success', `Successfully redeemed! +${redemption.credits} credits`);
			userCredits += redemption.credits;
			promoCode = '';
			goto('/chat');
		} catch (error: any) {
			addToast('error', error.message || 'Invalid promo code');
		} finally {
			isRedeeming = false;
		}
	}

	async function handleUpgradeToOrgAdmin() {
		isUpgrading = true;
		try {
			const data = await api.post<{ success: boolean; error?: string }>(
				'/api/org-admin/upgrade',
				{}
			);

			if (data.success) {
				addToast('success', 'Successfully upgraded to Organization Admin!');
				userRole = 'ORG_ADMIN';
				showUpgradeModal = false;
				loadTeamMembers();
			} else {
				addToast('error', data.error || 'Failed to upgrade');
			}
		} catch (error: any) {
			addToast('error', error.message || 'Failed to upgrade');
		} finally {
			isUpgrading = false;
		}
	}

	async function handleCreateUser(e: Event) {
		e.preventDefault();
		if (!newUserEmail.trim()) {
			addToast('warning', 'Please enter an email address');
			return;
		}

		isCreatingUser = true;
		try {
			const data = await api.post<{ success: boolean; error?: string }>(
				'/api/org-admin/users/create',
				{
					email: newUserEmail.trim(),
					name: newUserName.trim() || null,
					creditQuota: newUserQuota
				}
			);

			if (data.success) {
				addToast('success', 'Team member created successfully!');
				showCreateUserModal = false;
				newUserEmail = '';
				newUserName = '';
				newUserQuota = 0;
				loadTeamMembers();
			} else {
				addToast('error', data.error || 'Failed to create user');
			}
		} catch (error) {
			addToast('error', 'Failed to create user');
		} finally {
			isCreatingUser = false;
		}
	}

	async function handleChangePassword(e: Event) {
		e.preventDefault();

		if (!currentPassword || !newPassword || !confirmPassword) {
			addToast('warning', 'Please fill in all password fields');
			return;
		}

		if (newPassword.length < 8) {
			addToast('warning', 'New password must be at least 8 characters');
			return;
		}

		if (newPassword !== confirmPassword) {
			addToast('error', 'New passwords do not match');
			return;
		}

		isChangingPassword = true;
		try {
			const data = await api.post<{ success: boolean; error?: string }>(
				'/api/auth/change-password',
				{ currentPassword, newPassword }
			);

			if (data.success) {
				addToast('success', 'Password changed successfully!');
				closePasswordModal();
			} else {
				addToast('error', data.error || 'Failed to change password');
			}
		} catch (error: any) {
			addToast('error', error.message || 'Failed to change password');
		} finally {
			isChangingPassword = false;
		}
	}

	function closePasswordModal() {
		showPasswordModal = false;
		currentPassword = '';
		newPassword = '';
		confirmPassword = '';
		showCurrentPassword = false;
		showNewPassword = false;
		showConfirmPassword = false;
	}

	function getRoleDisplay(): string {
		if (userRole === 'ORG_OWNER') return 'Organization Owner';
		if (userRole === 'ORG_ADMIN') return 'Organization Admin';
		return 'User';
	}

	const purchasePackages = [
		{ credits: 1000, price: 10, label: null, discount: null },
		{ credits: 5000, price: 40, label: 'Popular', discount: '20%' },
		{ credits: 10000, price: 70, label: 'Best', discount: '30%' }
	];
</script>

<svelte:head>
	<title>Settings | Reality Transformer</title>
</svelte:head>

<div class="settings-page">
	<div class="settings-container">
		<!-- Header -->
		<div class="page-header">
			<div class="header-icon">
				<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
					<circle cx="12" cy="12" r="3"/>
				</svg>
			</div>
			<div class="header-text">
				<h1>Settings</h1>
				<p>Manage your account</p>
			</div>
		</div>

		<!-- Account Card -->
		<div class="card">
			<div class="card-header">
				<div class="card-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="12" cy="8" r="5"/>
						<path d="M20 21a8 8 0 0 0-16 0"/>
					</svg>
				</div>
				<h2>Account</h2>
			</div>

			<div class="info-rows">
				<div class="info-row">
					<span class="info-label">Email</span>
					<span class="info-value">{$user?.email || '-'}</span>
				</div>
				<div class="info-row">
					<span class="info-label">Name</span>
					<span class="info-value">{$user?.name || 'Not set'}</span>
				</div>
				<div class="info-row">
					<span class="info-label">Role</span>
					<span class="info-value">{getRoleDisplay()}</span>
				</div>
			</div>

			<div class="card-footer">
				<button class="btn btn-secondary" on:click={() => (showPasswordModal = true)}>
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"/>
						<path d="m21 2-9.6 9.6"/>
						<circle cx="7.5" cy="15.5" r="5.5"/>
					</svg>
					Change Password
				</button>
			</div>
		</div>

		<!-- Credits Card -->
		<div class="card">
			<div class="card-header">
				<div class="card-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect width="20" height="14" x="2" y="5" rx="2"/>
						<line x1="2" x2="22" y1="10" y2="10"/>
					</svg>
				</div>
				<div>
					<h2>Credits</h2>
					<p class="card-subtitle">{isOrgAdmin ? 'Organization balance' : 'Your balance'}</p>
				</div>
			</div>

			<!-- Credits Balance Display -->
			<div class="credits-balance" class:low-balance={userCredits < 500}>
				<div class="credits-amount">{userCredits.toLocaleString()}</div>
				<div class="credits-label">credits available</div>
				{#if userCredits < 500}
					<div class="low-balance-warning">
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>
							<path d="M12 9v4"/>
							<path d="M12 17h.01"/>
						</svg>
						<span>Low balance</span>
					</div>
				{/if}
			</div>

			<!-- Purchase Options -->
			<div class="purchase-section">
				<h3>Purchase Credits</h3>
				<div class="purchase-grid">
					{#each purchasePackages as pkg}
						<button
							class="purchase-option"
							class:featured={pkg.label}
							on:click={() => handlePurchaseCredits(pkg.credits)}
						>
							{#if pkg.label}
								<div class="purchase-label">{pkg.label}</div>
							{/if}
							<div class="purchase-credits">{(pkg.credits / 1000).toFixed(0)}K</div>
							<div class="purchase-price">${pkg.price}</div>
							{#if pkg.discount}
								<div class="purchase-discount">Save {pkg.discount}</div>
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<!-- Promo Code -->
			<div class="promo-section">
				<div class="promo-header">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
						<path d="M13 5v2"/>
						<path d="M13 17v2"/>
						<path d="M13 11v2"/>
					</svg>
					<span>Promo Code</span>
				</div>
				<form class="promo-form" on:submit={handleRedeemPromoCode}>
					<input
						type="text"
						id="settings-promo-code"
						name="settings-promo-code"
						bind:value={promoCode}
						placeholder="ENTER CODE"
						class="promo-input"
						disabled={isRedeeming}
					/>
					<button type="submit" class="btn btn-primary" disabled={!promoCode.trim() || isRedeeming}>
						{#if isRedeeming}
							<Spinner size="sm" />
						{:else}
							Redeem
						{/if}
					</button>
				</form>
			</div>
		</div>

		<!-- Upgrade to Org Admin (for USER role only) -->
		{#if userRole === 'USER'}
			<div class="card card-upgrade">
				<div class="upgrade-content">
					<div class="card-icon card-icon-green">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
							<circle cx="9" cy="7" r="4"/>
							<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
							<path d="M16 3.13a4 4 0 0 1 0 7.75"/>
						</svg>
					</div>
					<div class="upgrade-text">
						<h3>Manage a Team?</h3>
						<p>Upgrade to invite team members and allocate credits</p>
					</div>
				</div>
				<button class="btn btn-primary btn-sm" on:click={() => (showUpgradeModal = true)}>
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>
					</svg>
					Upgrade
				</button>
			</div>
		{/if}

		<!-- Team Management (for ORG_ADMIN/ORG_OWNER) -->
		{#if isOrgAdmin}
			<div class="card">
				<div class="card-header card-header-flex">
					<div class="card-header-left">
						<div class="card-icon card-icon-green">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
								<circle cx="9" cy="7" r="4"/>
								<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
								<path d="M16 3.13a4 4 0 0 1 0 7.75"/>
							</svg>
						</div>
						<div>
							<h2>Team</h2>
							<p class="card-subtitle">Manage members</p>
						</div>
					</div>
					<button class="btn btn-primary btn-sm" on:click={() => (showCreateUserModal = true)}>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M5 12h14"/>
							<path d="M12 5v14"/>
						</svg>
						<span class="hide-mobile">Add</span>
					</button>
				</div>

				<!-- Org Stats -->
				{#if orgInfo}
					<div class="org-stats">
						<div class="stat">
							<div class="stat-label">Pool</div>
							<div class="stat-value">{orgInfo.creditsPool.toLocaleString()}</div>
						</div>
						<div class="stat">
							<div class="stat-label">Allocated</div>
							<div class="stat-value stat-amber">{orgInfo.totalAllocated.toLocaleString()}</div>
						</div>
						<div class="stat">
							<div class="stat-label">Used</div>
							<div class="stat-value stat-red">{orgInfo.usedCredits.toLocaleString()}</div>
						</div>
						<div class="stat">
							<div class="stat-label">Available</div>
							<div class="stat-value stat-green">{orgInfo.availableForAllocation.toLocaleString()}</div>
						</div>
					</div>
				{/if}

				<!-- Team Members -->
				{#if loadingTeam}
					<div class="loading-state">
						<Spinner />
						<p>Loading team...</p>
					</div>
				{:else if teamMembers.length === 0}
					<div class="empty-state">No team members yet</div>
				{:else}
					<div class="team-list">
						{#each teamMembers as member}
							<div class="team-member">
								<div class="member-info">
									<div class="member-email">{member.email}</div>
									<div class="member-name">{member.name || member.role}</div>
								</div>
								<div class="member-quota">
									<div class="quota-value">{member.creditQuota.toLocaleString()}</div>
									<div class="quota-label">quota</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Usage History -->
		<div class="card">
			<button class="card-toggle" on:click={loadUsageHistory}>
				<div class="card-toggle-left">
					<div class="card-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<circle cx="12" cy="12" r="10"/>
							<polyline points="12 6 12 12 16 14"/>
						</svg>
					</div>
					<span class="toggle-title">Usage History</span>
				</div>
				<svg class="chevron" class:rotated={showUsageHistory} xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="m6 9 6 6 6-6"/>
				</svg>
			</button>

			{#if showUsageHistory}
				{#if loadingUsageHistory}
				<div style="display: flex; justify-content: center; padding: 1rem;">
					<Spinner size="sm" />
				</div>
			{:else if usageHistory.length > 0}
					<div class="history-list">
						{#each usageHistory.slice(0, 10) as entry}
							<div class="history-item">
								<div class="history-info">
									<div class="history-operation">{entry.operation}</div>
									<div class="history-date">{new Date(entry.date).toLocaleDateString()}</div>
								</div>
								<div class="history-cost">
									<div class="cost-value" class:positive={entry.cost > 0} class:negative={entry.cost <= 0}>
										{entry.cost > 0 ? '+' : ''}{entry.cost}
									</div>
									<div class="cost-balance">bal: {entry.balance.toLocaleString()}</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="empty-state">No usage history yet</div>
				{/if}
			{/if}
		</div>

		<!-- Credit History -->
		<div class="card">
			<button class="card-toggle" on:click={loadCreditHistory}>
				<div class="card-toggle-left">
					<div class="card-icon card-icon-green">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
							<path d="M13 5v2"/>
							<path d="M13 17v2"/>
							<path d="M13 11v2"/>
						</svg>
					</div>
					<span class="toggle-title">Credit History</span>
				</div>
				<svg class="chevron" class:rotated={showCreditHistory} xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="m6 9 6 6 6-6"/>
				</svg>
			</button>

			{#if showCreditHistory}
				{#if $isLoadingCreditHistory || loadingCreditHistory}
				<div style="display: flex; justify-content: center; padding: 1rem;">
					<Spinner size="sm" />
				</div>
			{:else if creditHistory.length > 0}
					<div class="history-list">
						{#each creditHistory.slice(0, 20) as txn}
							<div class="history-item">
								<div class="history-info">
									<div class="txn-badge" class:earned={txn.type === 'redeemed'} class:spent={txn.type === 'spent'}>
										{txn.type === 'redeemed' ? 'Earned' : 'Spent'}
									</div>
									<div class="history-operation">{txn.description}</div>
									<div class="history-date">{new Date(txn.createdAt).toLocaleDateString()} {new Date(txn.createdAt).toLocaleTimeString()}</div>
								</div>
								<div class="txn-amount" class:positive={txn.amount > 0} class:negative={txn.amount <= 0}>
									{txn.amount > 0 ? '+' : ''}{txn.amount.toLocaleString()}
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="empty-state">No credit transactions yet</div>
				{/if}
			{/if}
		</div>

		<!-- System Info -->
		<div class="card">
			<div class="card-header">
				<div class="card-icon card-icon-muted">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="12" cy="12" r="10"/>
						<path d="M12 16v-4"/>
						<path d="M12 8h.01"/>
					</svg>
				</div>
				<h2>System</h2>
			</div>
			<div class="info-rows">
				<div class="info-row">
					<span class="info-label">Version</span>
					<span class="info-value">1.0.0</span>
				</div>
				<div class="info-row">
					<span class="info-label">Environment</span>
					<span class="info-value">production</span>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- Upgrade Modal -->
{#if showUpgradeModal}
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div class="modal-overlay" on:click={() => (showUpgradeModal = false)} on:keydown={(e) => e.key === 'Escape' && (showUpgradeModal = false)} role="dialog" aria-modal="true" tabindex="-1">
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div class="modal" on:click|stopPropagation on:keydown|stopPropagation role="document">
			<h2>Upgrade to Org Admin</h2>
			<div class="modal-content">
				<div class="upgrade-benefits">
					<p>As an Organization Admin, you can:</p>
					<ul>
						<li>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
							Invite and manage team members
						</li>
						<li>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
							Allocate credits to your team
						</li>
						<li>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
							View team usage statistics
						</li>
					</ul>
				</div>
				<div class="modal-actions">
					<button class="btn btn-secondary" on:click={() => (showUpgradeModal = false)}>Cancel</button>
					<button class="btn btn-primary" on:click={handleUpgradeToOrgAdmin} disabled={isUpgrading}>
						{#if isUpgrading}
							<Spinner size="sm" />
						{:else}
							Confirm Upgrade
						{/if}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Create User Modal -->
{#if showCreateUserModal}
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div class="modal-overlay" on:click={() => (showCreateUserModal = false)} on:keydown={(e) => e.key === 'Escape' && (showCreateUserModal = false)} role="dialog" aria-modal="true" tabindex="-1">
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div class="modal" on:click|stopPropagation on:keydown|stopPropagation role="document">
			<h2>Add Team Member</h2>
			<form class="modal-form" on:submit={handleCreateUser}>
				<div class="form-group">
					<label for="newUserEmail">Email *</label>
					<input type="email" id="newUserEmail" bind:value={newUserEmail} placeholder="team@example.com" />
				</div>
				<div class="form-group">
					<label for="newUserName">Name</label>
					<input type="text" id="newUserName" bind:value={newUserName} placeholder="Full Name (optional)" />
				</div>
				<div class="form-group">
					<label for="newUserQuota">Credit Quota</label>
					<input type="number" id="newUserQuota" bind:value={newUserQuota} placeholder="0" />
					{#if orgInfo}
						<p class="form-hint">Available: {orgInfo.availableForAllocation.toLocaleString()} credits</p>
					{/if}
				</div>
				<div class="modal-actions">
					<button type="button" class="btn btn-secondary" on:click={() => { showCreateUserModal = false; newUserEmail = ''; newUserName = ''; newUserQuota = 0; }}>Cancel</button>
					<button type="submit" class="btn btn-primary" disabled={isCreatingUser}>
						{#if isCreatingUser}
							<Spinner size="sm" />
						{:else}
							Add Member
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Change Password Modal -->
{#if showPasswordModal}
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div class="modal-overlay" on:click={closePasswordModal} on:keydown={(e) => e.key === 'Escape' && closePasswordModal()} role="dialog" aria-modal="true" tabindex="-1">
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div class="modal" on:click|stopPropagation on:keydown|stopPropagation role="document">
			<h2>Change Password</h2>
			<form class="modal-form" on:submit={handleChangePassword}>
				<div class="form-group">
					<label for="currentPassword">Current Password *</label>
					<div class="password-input">
						{#if showCurrentPassword}
							<input
								type="text"
								id="currentPasswordText"
								bind:value={currentPassword}
								placeholder="Enter current password"
								disabled={isChangingPassword}
							/>
						{:else}
							<input
								type="password"
								id="currentPassword"
								bind:value={currentPassword}
								placeholder="Enter current password"
								disabled={isChangingPassword}
							/>
						{/if}
						<button type="button" class="password-toggle" on:click={() => (showCurrentPassword = !showCurrentPassword)}>
							{#if showCurrentPassword}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
							{/if}
						</button>
					</div>
				</div>
				<div class="form-group">
					<label for="newPassword">New Password *</label>
					<div class="password-input">
						{#if showNewPassword}
							<input
								type="text"
								id="newPasswordText"
								bind:value={newPassword}
								placeholder="Enter new password"
								disabled={isChangingPassword}
							/>
						{:else}
							<input
								type="password"
								id="newPassword"
								bind:value={newPassword}
								placeholder="Enter new password"
								disabled={isChangingPassword}
							/>
						{/if}
						<button type="button" class="password-toggle" on:click={() => (showNewPassword = !showNewPassword)}>
							{#if showNewPassword}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
							{/if}
						</button>
					</div>
					<p class="form-hint">Must be at least 8 characters</p>
				</div>
				<div class="form-group">
					<label for="confirmPassword">Confirm New Password *</label>
					<div class="password-input">
						{#if showConfirmPassword}
							<input
								type="text"
								id="confirmPasswordText"
								bind:value={confirmPassword}
								placeholder="Confirm new password"
								disabled={isChangingPassword}
							/>
						{:else}
							<input
								type="password"
								id="confirmPassword"
								bind:value={confirmPassword}
								placeholder="Confirm new password"
								disabled={isChangingPassword}
							/>
						{/if}
						<button type="button" class="password-toggle" on:click={() => (showConfirmPassword = !showConfirmPassword)}>
							{#if showConfirmPassword}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
							{/if}
						</button>
					</div>
					{#if confirmPassword && newPassword !== confirmPassword}
						<p class="form-error">Passwords do not match</p>
					{/if}
				</div>
				<div class="modal-actions">
					<button type="button" class="btn btn-secondary" on:click={closePasswordModal} disabled={isChangingPassword}>Cancel</button>
					<button type="submit" class="btn btn-primary" disabled={isChangingPassword || !currentPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword}>
						{#if isChangingPassword}
							<Spinner size="sm" />
						{:else}
							Change Password
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<style>
	.settings-page {
		width: 100%;
		height: 100%;
		background: var(--color-field-void);
		overflow-y: auto;
	}

	.settings-container {
		max-width: 42rem;
		margin: 0 auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	/* Page Header */
	.page-header {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.25rem 0;
	}

	.header-icon {
		width: 2rem;
		height: 2rem;
		border-radius: 0.5rem;
		background: var(--color-primary-500);
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		flex-shrink: 0;
	}

	.header-icon svg {
		width: 18px;
		height: 18px;
	}

	.header-text h1 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.header-text p {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Card */
	.card {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		padding: 0.875rem;
	}

	.card-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
	}

	.card-header-flex {
		justify-content: space-between;
	}

	.card-header-left {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.card-header h2 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.card-subtitle {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
		margin: 0;
	}

	.card-icon {
		width: 1.75rem;
		height: 1.75rem;
		border-radius: 0.375rem;
		background: var(--color-primary-100);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-primary-600);
		flex-shrink: 0;
	}

	.card-icon svg {
		width: 14px;
		height: 14px;
	}

	.card-icon-green {
		background: rgba(5, 150, 105, 0.1);
		color: #059669;
	}

	.card-icon-muted {
		background: var(--color-field-depth);
		color: var(--color-text-whisper);
	}

	.card-footer {
		margin-top: 0.75rem;
		padding-top: 0.75rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	/* Info Rows */
	.info-rows {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.info-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5rem 0.75rem;
		border-radius: 0.5rem;
		background: var(--color-field-depth);
	}

	.info-label {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-whisper);
	}

	.info-value {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-source);
		text-align: right;
		overflow: hidden;
		text-overflow: ellipsis;
		margin-left: 0.5rem;
	}

	/* Buttons */
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.375rem;
		font-weight: 500;
		border-radius: 0.5rem;
		transition: all 0.15s ease;
		cursor: pointer;
		border: none;
		padding: 0.5rem 0.75rem;
		font-size: 0.8125rem;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-primary {
		background: var(--color-primary-500);
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.btn-secondary {
		background: var(--color-field-elevated);
		color: var(--color-text-source);
		border: 1px solid var(--color-veil-thin);
	}

	.btn-secondary:hover:not(:disabled) {
		background: var(--color-field-depth);
	}

	.btn-sm {
		padding: 0.375rem 0.625rem;
		font-size: 0.75rem;
	}

	.hide-mobile {
		display: none;
	}

	@media (min-width: 480px) {
		.hide-mobile {
			display: inline;
		}
	}

	/* Credits Balance */
	.credits-balance {
		padding: 0.75rem 1rem;
		border-radius: 0.5rem;
		text-align: center;
		margin-bottom: 0.75rem;
		background: var(--color-primary-50);
		border: 1px solid var(--color-primary-200);
	}

	.credits-balance.low-balance {
		background: rgba(239, 68, 68, 0.05);
		border-color: rgba(239, 68, 68, 0.2);
	}

	.credits-amount {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.125rem;
	}

	.credits-label {
		font-size: 0.6875rem;
		font-weight: 500;
		color: var(--color-text-whisper);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.low-balance-warning {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.375rem;
		margin-top: 0.5rem;
		color: #dc2626;
		font-size: 0.75rem;
	}

	/* Purchase Section */
	.purchase-section {
		margin-bottom: 0.75rem;
	}

	.purchase-section h3 {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.purchase-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.5rem;
	}

	.purchase-option {
		padding: 0.5rem;
		border-radius: 0.5rem;
		border: 1px solid var(--color-veil-thin);
		background: transparent;
		cursor: pointer;
		text-align: center;
		transition: all 0.15s ease;
	}

	.purchase-option:hover {
		border-color: var(--color-primary-400);
	}

	.purchase-option.featured {
		border-color: var(--color-primary-500);
		background: var(--color-primary-50);
	}

	.purchase-label {
		font-size: 0.625rem;
		font-weight: 600;
		color: var(--color-primary-600);
		margin-bottom: 0.125rem;
	}

	.purchase-credits {
		font-size: 0.9375rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.purchase-price {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-primary-600);
	}

	.purchase-discount {
		font-size: 0.625rem;
		font-weight: 500;
		color: #059669;
	}

	/* Promo Section */
	.promo-section {
		padding: 0.75rem;
		border-radius: 0.5rem;
		background: var(--color-field-depth);
	}

	.promo-header {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		margin-bottom: 0.5rem;
		color: var(--color-primary-600);
		font-size: 0.75rem;
		font-weight: 600;
	}

	.promo-header svg {
		width: 14px;
		height: 14px;
	}

	.promo-form {
		display: flex;
		gap: 0.375rem;
	}

	.promo-input {
		flex: 1;
		padding: 0.5rem 0.75rem;
		background: var(--color-field-void);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		color: var(--color-text-source);
		font-size: 0.8125rem;
		text-transform: uppercase;
		font-family: monospace;
	}

	.promo-input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.promo-input::placeholder {
		color: var(--color-text-hint);
	}

	/* Upgrade Card */
	.card-upgrade {
		border-color: var(--color-primary-200);
		background: rgba(15, 23, 42, 0.03);
	}

	.upgrade-content {
		display: flex;
		align-items: flex-start;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.upgrade-text h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.125rem;
	}

	.upgrade-text p {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		margin: 0;
	}

	/* Org Stats */
	.org-stats {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.375rem;
		margin-bottom: 0.75rem;
	}

	.stat {
		padding: 0.375rem 0.5rem;
		border-radius: 0.375rem;
		background: var(--color-field-depth);
		text-align: center;
	}

	.stat-label {
		font-size: 0.625rem;
		color: var(--color-text-whisper);
		margin-bottom: 0.125rem;
	}

	.stat-value {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.stat-amber {
		color: #d97706;
	}

	.stat-red {
		color: #dc2626;
	}

	.stat-green {
		color: #059669;
	}

	/* Team List */
	.team-list {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.team-member {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5rem 0.625rem;
		border-radius: 0.375rem;
		background: var(--color-field-depth);
	}

	.member-info {
		min-width: 0;
		flex: 1;
	}

	.member-email {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-source);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.member-name {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
	}

	.member-quota {
		text-align: right;
		margin-left: 0.5rem;
	}

	.quota-value {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-primary-600);
	}

	.quota-label {
		font-size: 0.625rem;
		color: var(--color-text-whisper);
	}

	/* Loading & Empty States */
	.loading-state {
		padding: 1rem 0;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.loading-state p {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	.empty-state {
		padding: 1rem 0;
		text-align: center;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Card Toggle (Collapsible) */
	.card-toggle {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		color: inherit;
	}

	.card-toggle-left {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.toggle-title {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.chevron {
		color: var(--color-text-whisper);
		transition: transform 0.2s ease;
		width: 16px;
		height: 16px;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	/* History List */
	.history-list {
		margin-top: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.history-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5rem 0.625rem;
		border-radius: 0.375rem;
		background: var(--color-field-depth);
	}

	.history-info {
		min-width: 0;
		flex: 1;
	}

	.history-operation {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-source);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.history-date {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
	}

	.history-cost {
		text-align: right;
		margin-left: 0.5rem;
	}

	.cost-value {
		font-size: 0.8125rem;
		font-weight: 600;
	}

	.cost-value.positive {
		color: #059669;
	}

	.cost-value.negative {
		color: #dc2626;
	}

	.cost-balance {
		font-size: 0.625rem;
		color: var(--color-text-whisper);
	}

	.txn-badge {
		display: inline-block;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		font-size: 0.625rem;
		font-weight: 500;
		margin-bottom: 0.125rem;
	}

	.txn-badge.earned {
		background: rgba(5, 150, 105, 0.1);
		color: #059669;
	}

	.txn-badge.spent {
		background: rgba(220, 38, 38, 0.1);
		color: #dc2626;
	}

	.txn-amount {
		font-size: 0.875rem;
		font-weight: 600;
	}

	.txn-amount.positive {
		color: #059669;
	}

	.txn-amount.negative {
		color: #dc2626;
	}

	/* Modal */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 80;
		padding: 1rem;
	}

	.modal {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		box-shadow: var(--shadow-elevated);
		max-width: 90vw;
		width: 24rem;
		padding: 1rem;
		border: 1px solid var(--color-veil-thin);
		max-height: 85vh;
		overflow-y: auto;
	}

	.modal h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.75rem;
	}

	.modal-content {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.modal-form {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.modal-actions {
		display: flex;
		gap: 0.5rem;
		margin-top: 0.25rem;
	}

	.modal-actions .btn {
		flex: 1;
	}

	/* Upgrade Benefits */
	.upgrade-benefits {
		padding: 0.75rem;
		border-radius: 0.5rem;
		background: var(--color-primary-50);
	}

	.upgrade-benefits p {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		margin-bottom: 0.5rem;
	}

	.upgrade-benefits ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.upgrade-benefits li {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		font-size: 0.8125rem;
		color: var(--color-text-source);
	}

	.upgrade-benefits li svg {
		color: #059669;
		flex-shrink: 0;
		width: 14px;
		height: 14px;
	}

	/* Form Group */
	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.form-group label {
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-whisper);
	}

	.form-group input {
		width: 100%;
		padding: 0.5rem 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		color: var(--color-text-source);
		font-size: 0.8125rem;
		transition: border-color 0.15s ease;
	}

	.form-group input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.form-group input::placeholder {
		color: var(--color-text-hint);
	}

	.form-group input:disabled {
		opacity: 0.5;
	}

	.form-hint {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
		margin: 0;
	}

	.form-error {
		font-size: 0.6875rem;
		color: #dc2626;
		margin: 0;
	}

	/* Password Input */
	.password-input {
		position: relative;
	}

	.password-input input {
		width: 100%;
		padding-right: 2.5rem;
	}

	.password-toggle {
		position: absolute;
		right: 0.5rem;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		padding: 0.25rem;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: color 0.15s ease;
	}

	.password-toggle svg {
		width: 16px;
		height: 16px;
	}

	.password-toggle:hover {
		color: var(--color-text-source);
	}
</style>
