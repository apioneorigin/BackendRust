<script lang="ts">
	/**
	 * Add Credits Page - Onboarding Promo Code Redemption
	 *
	 * Shown to users after signup/login who have 0 credits.
	 * Users must redeem a promo code to access the app.
	 */

	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user, isAuthenticated, credits, creditBalance, addToast } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';

	export let params: Record<string, string> = {};

	let promoCode = '';
	let isRedeeming = false;
	let isCheckingCredits = true;

	let loadError = '';

	onMount(async () => {
		// Wait for auth to settle
		await new Promise((resolve) => setTimeout(resolve, 100));

		if (!$isAuthenticated) {
			goto('/login');
			return;
		}

		try {
			// Check current credits
			await credits.loadBalance();
			isCheckingCredits = false;

			// If user has credits, redirect to chat
			if ($creditBalance && $creditBalance.creditQuota && $creditBalance.creditQuota > 0) {
				goto('/chat');
			}
		} catch (error: any) {
			isCheckingCredits = false;
			loadError = error.message || 'Failed to load credits';
		}
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
			addToast('success', `Successfully redeemed! +${redemption.credits} credits`);
			promoCode = '';

			// Redirect to chat after successful redemption
			setTimeout(() => {
				goto('/chat');
			}, 1500);
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

	// Get first name from user
	$: firstName = $user?.name?.trim().split(/\s+/)[0] || '';
</script>

<svelte:head>
	<title>Add Credits | Reality Transformer</title>
</svelte:head>

<div class="add-credits-page">
	{#if isCheckingCredits}
		<div class="loading-container">
			<Spinner size="lg" />
		</div>
	{:else if loadError}
		<div class="loading-container">
			<p style="color: var(--color-error-500); margin-bottom: 1rem;">{loadError}</p>
			<button on:click={() => location.reload()} style="padding: 0.5rem 1rem; background: var(--gradient-primary); color: white; border: none; border-radius: 0.5rem; cursor: pointer;">Retry</button>
		</div>
	{:else}
		<div class="credits-card">
			<!-- Header -->
			<div class="card-header">
				<div class="icon-container">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="32"
						height="32"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path
							d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"
						/>
					</svg>
				</div>

				<div class="header-text">
					<h1>Welcome{firstName ? `, ${firstName}` : ''}!</h1>
					<p>Add credits to get started</p>
				</div>
			</div>

			<!-- Promo Code Form -->
			<form on:submit={handleRedeemCode} class="promo-form">
				<div class="form-group">
					<label for="promoCode">Enter your promo code</label>
					<div class="input-wrapper">
						<svg
							class="input-icon"
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
								d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"
							/>
							<path d="M13 5v2" />
							<path d="M13 17v2" />
							<path d="M13 11v2" />
						</svg>
						<input
							id="promoCode"
							type="text"
							value={promoCode}
							on:input={handleInputChange}
							placeholder="ENTER-CODE-HERE"
							disabled={isRedeeming}
							autocomplete="off"
						/>
					</div>
				</div>

				<button type="submit" class="submit-btn" disabled={!promoCode.trim() || isRedeeming}>
					{#if isRedeeming}
						<Spinner size="sm" />
						<span>Redeeming...</span>
					{:else}
						<span>Redeem Code</span>
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
							<path d="M5 12h14" />
							<path d="m12 5 7 7-7 7" />
						</svg>
					{/if}
				</button>
			</form>

			<!-- Info Box -->
			<div class="info-box">
				<svg
					class="info-icon"
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
						d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"
					/>
					<path d="M13 5v2" />
					<path d="M13 17v2" />
					<path d="M13 11v2" />
				</svg>
				<div class="info-content">
					<p class="info-title">Need a promo code?</p>
					<p class="info-text">Contact your admin to receive a promo code and start using the app.</p>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.add-credits-page {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 1rem;
		background: linear-gradient(
			135deg,
			var(--color-primary-50) 0%,
			var(--color-primary-100) 50%,
			var(--color-primary-200) 100%
		);
	}

	.loading-container {
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.credits-card {
		width: 100%;
		max-width: 28rem;
		background: var(--color-field-surface);
		border-radius: 1rem;
		box-shadow: var(--shadow-elevated);
		padding: 1.5rem;
	}

	@media (min-width: 480px) {
		.credits-card {
			padding: 2rem;
		}
	}

	.card-header {
		text-align: center;
		margin-bottom: 1.5rem;
	}

	.icon-container {
		width: 4rem;
		height: 4rem;
		margin: 0 auto 1rem;
		background: var(--gradient-primary);
		border-radius: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}

	.header-text h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	@media (min-width: 480px) {
		.header-text h1 {
			font-size: 1.875rem;
		}
	}

	.header-text p {
		font-size: 0.9375rem;
		color: var(--color-text-whisper);
	}

	.promo-form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.form-group label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.5rem;
	}

	.input-wrapper {
		position: relative;
	}

	.input-icon {
		position: absolute;
		left: 0.75rem;
		top: 50%;
		transform: translateY(-50%);
		color: var(--color-text-hint);
		pointer-events: none;
	}

	.input-wrapper input {
		width: 100%;
		padding: 0.75rem 1rem 0.75rem 2.75rem;
		font-size: 1rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.75rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
		transition: all 0.15s ease;
	}

	.input-wrapper input::placeholder {
		color: var(--color-text-hint);
	}

	.input-wrapper input:focus {
		outline: none;
		border-color: var(--color-primary-400);
		box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.1);
	}

	.input-wrapper input:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.submit-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.875rem 1.5rem;
		font-size: 1rem;
		font-weight: 600;
		color: white;
		background: var(--gradient-primary);
		border: none;
		border-radius: 0.75rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.submit-btn:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: var(--shadow-elevated);
	}

	.submit-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.info-box {
		display: flex;
		gap: 0.75rem;
		padding: 1rem;
		background: var(--color-primary-50);
		border-radius: 0.75rem;
	}

	.info-icon {
		flex-shrink: 0;
		color: var(--color-primary-600);
		margin-top: 0.125rem;
	}

	.info-content {
		font-size: 0.875rem;
	}

	.info-title {
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.25rem;
	}

	.info-text {
		color: var(--color-text-whisper);
	}
</style>
