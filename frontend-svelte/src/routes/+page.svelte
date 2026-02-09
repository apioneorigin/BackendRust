<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import type { PageData } from './$types';

	export let data: PageData;

	let loadError = '';

	onMount(async () => {
		try {
			// User data comes from server (hooks.server.ts → layout.server.ts)
			// No client-side API call needed
			const userData = data.user || $user;

			if (!userData) {
				goto('/login');
				return;
			}

			// hooks.server.ts already redirects 0-credit users to /add-credits
			// Just send authenticated users to chat
			goto('/chat');
		} catch (error: any) {
			loadError = error.message || 'Failed to load. Please check your connection.';
		}
	});

	function retry() {
		loadError = '';
		location.reload();
	}
</script>

{#if loadError}
	<div class="loading-container">
		<p class="error-text">{loadError}</p>
		<button class="retry-btn" on:click={retry}>Retry</button>
	</div>
{:else}
	<div class="loading-container">
		<div class="spinner"></div>
		<p>Loading...</p>
	</div>
{/if}

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

	.error-text {
		color: var(--color-error-500);
		font-size: 0.9375rem;
		text-align: center;
		max-width: 300px;
	}

	.retry-btn {
		padding: 0.625rem 1.5rem;
		background: var(--gradient-primary);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: opacity 0.15s ease;
	}

	.retry-btn:hover {
		opacity: 0.9;
	}
</style>
