<script lang="ts">
	import { onMount } from 'svelte';
	import { auth, theme, toasts, removeToast, credits } from '$lib/stores';
	import '../styles/globals.css';

	// Initialize theme on mount
	onMount(() => {
		// Check for system preference
		const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		const savedTheme = localStorage.getItem('theme');

		if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
			theme.setDark();
		} else {
			theme.setLight();
		}

		// Try to load user on mount
		auth.loadUser();
	});

	// Toast auto-dismiss
	$: $toasts.forEach((toast) => {
		if (toast.duration && toast.duration > 0) {
			setTimeout(() => {
				removeToast(toast.id);
			}, toast.duration);
		}
	});
</script>

<div class="app" class:dark={$theme.isDark}>
	<slot />

	<!-- Toast notifications -->
	{#if $toasts.length > 0}
		<div class="toast-container">
			{#each $toasts as toast (toast.id)}
				<div class="toast toast-{toast.type}" role="alert">
					<div class="toast-content">
						{#if toast.title}
							<strong class="toast-title">{toast.title}</strong>
						{/if}
						<p class="toast-message">{toast.message}</p>
					</div>
					<button
						class="toast-close"
						on:click={() => removeToast(toast.id)}
						aria-label="Close"
					>
						&times;
					</button>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.app {
		min-height: 100vh;
		background-color: var(--background);
		color: var(--foreground);
		transition: background-color 0.3s, color 0.3s;
	}

	.app.dark {
		--background: 0 0% 3.9%;
		--foreground: 0 0% 98%;
		--card: 0 0% 3.9%;
		--card-foreground: 0 0% 98%;
		--primary: 0 0% 98%;
		--primary-foreground: 0 0% 9%;
		--secondary: 0 0% 14.9%;
		--secondary-foreground: 0 0% 98%;
		--muted: 0 0% 14.9%;
		--muted-foreground: 0 0% 63.9%;
		--accent: 0 0% 14.9%;
		--accent-foreground: 0 0% 98%;
		--destructive: 0 62.8% 30.6%;
		--destructive-foreground: 0 0% 98%;
		--border: 0 0% 14.9%;
		--input: 0 0% 14.9%;
		--ring: 0 0% 83.1%;
	}

	/* Toast container */
	.toast-container {
		position: fixed;
		bottom: 1rem;
		right: 1rem;
		z-index: 9999;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		max-width: 400px;
	}

	.toast {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 1rem;
		border-radius: 0.5rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		animation: slideIn 0.3s ease-out;
	}

	.toast-success {
		background-color: hsl(142 76% 36%);
		color: white;
	}

	.toast-error {
		background-color: hsl(0 84% 60%);
		color: white;
	}

	.toast-warning {
		background-color: hsl(38 92% 50%);
		color: white;
	}

	.toast-info {
		background-color: hsl(221 83% 53%);
		color: white;
	}

	.toast-content {
		flex: 1;
	}

	.toast-title {
		display: block;
		font-weight: 600;
		margin-bottom: 0.25rem;
	}

	.toast-message {
		font-size: 0.875rem;
		margin: 0;
	}

	.toast-close {
		background: none;
		border: none;
		color: inherit;
		font-size: 1.25rem;
		cursor: pointer;
		opacity: 0.7;
		padding: 0;
		line-height: 1;
	}

	.toast-close:hover {
		opacity: 1;
	}

	@keyframes slideIn {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}
</style>
