<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth, credits, creditBalance } from '$lib/stores';

	export let params: Record<string, string> = {};

	// Super admin bypasses credit check
	const SUPER_ADMIN_EMAIL = 'raghavan.vinod@gmail.com';

	onMount(async () => {
		// Try to load user, redirect based on auth status
		const user = await auth.loadUser();

		if (!user) {
			goto('/login');
			return;
		}

		// Super admin bypasses credit check
		if (user.email === SUPER_ADMIN_EMAIL) {
			goto('/chat');
			return;
		}

		// User is authenticated - check credits
		await credits.loadBalance();

		// If user has no credits, redirect to add-credits page
		if (!$creditBalance?.creditQuota || $creditBalance.creditQuota < 1) {
			goto('/add-credits');
		} else {
			// User has credits, go to chat
			goto('/chat');
		}
	});
</script>

<div class="loading-container">
	<div class="spinner"></div>
	<p>Loading...</p>
</div>

<style>
	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		gap: 1rem;
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

	p {
		color: hsl(var(--muted-foreground));
	}
</style>
