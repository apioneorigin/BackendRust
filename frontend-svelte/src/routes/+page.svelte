<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth, isAuthenticated } from '$lib/stores';

	// Accept SvelteKit props
	export let data: Record<string, unknown> = {};
	let _restProps = $$restProps;

	onMount(async () => {
		// Try to load user, redirect based on auth status
		const user = await auth.loadUser();
		if (user) {
			goto('/chat');
		} else {
			goto('/login');
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
