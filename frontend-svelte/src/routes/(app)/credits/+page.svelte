<script lang="ts">
	import { onMount } from 'svelte';
	import { credits, creditBalance, isLoadingCreditHistory, addToast } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';

	let promoCode = '';
	let isRedeeming = false;
	let activeTab: 'overview' | 'history' | 'redeem' = 'overview';

	onMount(async () => {
		await credits.loadBalance();
		await credits.loadRedemptionHistory();
		await credits.loadUsageHistory();
	});

	async function handleRedeemCode(e: Event) {
		e.preventDefault();
		if (!promoCode.trim()) {
			addToast('warning', 'Please enter a promo code');
			return;
		}

		isRedeeming = true;
		try {
			const redemption = await credits.redeemCode(promoCode.trim());
			addToast('success', `+${redemption.credits} credits added!`);
			promoCode = '';
			activeTab = 'overview';
		} catch (error: any) {
			addToast('error', error.message || 'Invalid promo code');
		} finally {
			isRedeeming = false;
		}
	}

	function handleInputChange(e: Event) {
		const target = e.target as HTMLInputElement;
		promoCode = target.value.toUpperCase();
	}

	$: balance = $creditBalance;
	$: creditsRemaining = balance?.creditQuota ?? 0;
</script>

<svelte:head>
	<title>Credits | Reality Transformer</title>
</svelte:head>

<div class="credits-page">
	<div class="page-header">
		<h1>Credits</h1>
		<p class="subtitle">View your balance, usage, and redeem promo codes</p>
	</div>

	<!-- Balance card -->
	<div class="balance-card">
		<div class="balance-main">
			<span class="balance-label">Credits Remaining</span>
			<span class="balance-value">{creditsRemaining.toLocaleString()}</span>
		</div>
		{#if balance && balance.organizationMax > 0}
			<div class="balance-org">
				<span class="org-label">Organization usage</span>
				<div class="progress-bar-container">
					<div class="progress-bar" style="width: {Math.min(balance.percentageUsed, 100)}%"></div>
				</div>
				<span class="org-detail">{balance.organizationUsed.toLocaleString()} / {balance.organizationMax.toLocaleString()} used</span>
			</div>
		{/if}
		{#if creditsRemaining <= 10 && creditsRemaining > 0}
			<div class="low-credits-warning">
				Credits running low. Redeem a promo code to continue using the app.
			</div>
		{/if}
		{#if creditsRemaining === 0}
			<div class="no-credits-warning">
				No credits remaining. Redeem a promo code to continue.
			</div>
		{/if}
	</div>

	<!-- Tabs -->
	<div class="tabs">
		<button class="tab" class:active={activeTab === 'overview'} on:click={() => activeTab = 'overview'}>Usage</button>
		<button class="tab" class:active={activeTab === 'history'} on:click={() => activeTab = 'history'}>Redemptions</button>
		<button class="tab" class:active={activeTab === 'redeem'} on:click={() => activeTab = 'redeem'}>Redeem Code</button>
	</div>

	<!-- Tab content -->
	<div class="tab-content">
		{#if activeTab === 'overview'}
			<div class="usage-section">
				{#if $isLoadingCreditHistory}
					<div class="loading"><Spinner size="md" /></div>
				{:else}
					{#each $credits.usageHistory as record (record.id)}
						<div class="usage-row">
							<div class="usage-info">
								<span class="usage-type">{record.usageType.replace(/_/g, ' ')}</span>
								<span class="usage-date">{record.createdAt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
							</div>
							<span class="usage-qty">-{record.quantity}</span>
						</div>
					{:else}
						<p class="empty-state">No usage recorded yet</p>
					{/each}
				{/if}
			</div>

		{:else if activeTab === 'history'}
			<div class="redemptions-section">
				{#if $isLoadingCreditHistory}
					<div class="loading"><Spinner size="md" /></div>
				{:else}
					{#each $credits.redemptions as redemption (redemption.id)}
						<div class="redemption-row">
							<div class="redemption-info">
								<span class="redemption-code">Promo code redeemed</span>
								<span class="redemption-date">{redemption.redeemedAt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
							</div>
							<span class="redemption-credits">+{redemption.credits}</span>
						</div>
					{:else}
						<p class="empty-state">No redemptions yet</p>
					{/each}
				{/if}
			</div>

		{:else if activeTab === 'redeem'}
			<div class="redeem-section">
				<form on:submit={handleRedeemCode} class="redeem-form">
					<label for="promoCode">Enter promo code</label>
					<div class="input-row">
						<input
							id="promoCode"
							type="text"
							value={promoCode}
							on:input={handleInputChange}
							placeholder="ENTER-CODE-HERE"
							disabled={isRedeeming}
							autocomplete="off"
						/>
						<button type="submit" class="redeem-btn" disabled={!promoCode.trim() || isRedeeming}>
							{#if isRedeeming}
								<Spinner size="sm" />
							{:else}
								Redeem
							{/if}
						</button>
					</div>
				</form>
				<p class="redeem-help">Contact your admin if you need a promo code.</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.credits-page {
		max-width: 40rem;
		margin: 0 auto;
		padding: 2rem 1.5rem;
	}

	.page-header {
		margin-bottom: 1.5rem;
	}

	.page-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.25rem;
	}

	.subtitle {
		font-size: 0.875rem;
		color: var(--color-text-whisper);
	}

	/* Balance card */
	.balance-card {
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.75rem;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}

	.balance-main {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.balance-label {
		font-size: 0.875rem;
		color: var(--color-text-whisper);
		font-weight: 500;
	}

	.balance-value {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.balance-org {
		border-top: 1px solid var(--color-veil-thin);
		padding-top: 1rem;
	}

	.org-label {
		font-size: 0.8125rem;
		color: var(--color-text-hint);
		display: block;
		margin-bottom: 0.5rem;
	}

	.progress-bar-container {
		height: 6px;
		background: var(--color-veil-thin);
		border-radius: 3px;
		overflow: hidden;
		margin-bottom: 0.25rem;
	}

	.progress-bar {
		height: 100%;
		background: var(--gradient-primary);
		border-radius: 3px;
		transition: width 0.3s ease;
	}

	.org-detail {
		font-size: 0.75rem;
		color: var(--color-text-hint);
	}

	.low-credits-warning {
		margin-top: 1rem;
		padding: 0.75rem;
		background: rgba(234, 179, 8, 0.1);
		border: 1px solid rgba(234, 179, 8, 0.3);
		border-radius: 0.5rem;
		color: var(--color-text-manifest);
		font-size: 0.8125rem;
	}

	.no-credits-warning {
		margin-top: 1rem;
		padding: 0.75rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: 0.5rem;
		color: var(--color-text-manifest);
		font-size: 0.8125rem;
	}

	/* Tabs */
	.tabs {
		display: flex;
		gap: 0;
		border-bottom: 1px solid var(--color-veil-thin);
		margin-bottom: 1rem;
	}

	.tab {
		padding: 0.75rem 1.25rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-whisper);
		background: none;
		border: none;
		border-bottom: 2px solid transparent;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.tab:hover {
		color: var(--color-text-manifest);
	}

	.tab.active {
		color: var(--color-text-source);
		border-bottom-color: var(--color-primary-500);
	}

	/* Tab content */
	.tab-content {
		min-height: 200px;
	}

	.loading {
		display: flex;
		justify-content: center;
		padding: 2rem;
	}

	.empty-state {
		text-align: center;
		color: var(--color-text-hint);
		padding: 2rem;
		font-size: 0.875rem;
	}

	/* Usage rows */
	.usage-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 0;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.usage-row:last-child {
		border-bottom: none;
	}

	.usage-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.usage-type {
		font-size: 0.875rem;
		color: var(--color-text-manifest);
		text-transform: capitalize;
	}

	.usage-date {
		font-size: 0.75rem;
		color: var(--color-text-hint);
	}

	.usage-qty {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-error-500, #ef4444);
	}

	/* Redemption rows */
	.redemption-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 0;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.redemption-row:last-child {
		border-bottom: none;
	}

	.redemption-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.redemption-code {
		font-size: 0.875rem;
		color: var(--color-text-manifest);
	}

	.redemption-date {
		font-size: 0.75rem;
		color: var(--color-text-hint);
	}

	.redemption-credits {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-success-500, #22c55e);
	}

	/* Redeem form */
	.redeem-section {
		padding: 0.5rem 0;
	}

	.redeem-form label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.5rem;
	}

	.input-row {
		display: flex;
		gap: 0.5rem;
	}

	.input-row input {
		flex: 1;
		padding: 0.75rem 1rem;
		font-size: 0.9375rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
	}

	.input-row input::placeholder {
		color: var(--color-text-hint);
	}

	.input-row input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.input-row input:disabled {
		opacity: 0.6;
	}

	.redeem-btn {
		padding: 0.75rem 1.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		color: white;
		background: var(--gradient-primary);
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		white-space: nowrap;
	}

	.redeem-btn:hover:not(:disabled) {
		opacity: 0.9;
	}

	.redeem-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.redeem-help {
		margin-top: 0.75rem;
		font-size: 0.8125rem;
		color: var(--color-text-hint);
	}

	@media (max-width: 640px) {
		.credits-page {
			padding: 1rem;
		}

		.input-row {
			flex-direction: column;
		}

		.balance-value {
			font-size: 1.5rem;
		}
	}
</style>
