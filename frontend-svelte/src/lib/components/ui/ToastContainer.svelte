<script lang="ts">
	import { toast, type Toast } from '$lib/stores/toast';
	import { fly, fade } from 'svelte/transition';

	function getIcon(type: Toast['type']) {
		switch (type) {
			case 'success':
				return `<svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>`;
			case 'error':
				return `<svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>`;
			case 'warning':
				return `<svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
				</svg>`;
			case 'info':
			default:
				return `<svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>`;
		}
	}
</script>

<div
	class="toast-container"
	aria-live="polite"
	aria-atomic="true"
>
	{#each $toast as item (item.id)}
		<div
			class="toast toast-{item.type}"
			in:fly={{ x: 100, duration: 200 }}
			out:fade={{ duration: 150 }}
		>
			<div class="toast-icon">
				{@html getIcon(item.type)}
			</div>
			<p class="toast-message">{item.message}</p>
			<button
				class="toast-close"
				on:click={() => toast.remove(item.id)}
				aria-label="Dismiss"
			>
				<svg class="close-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
			</button>
		</div>
	{/each}
</div>

<style>
	.toast-container {
		position: fixed;
		bottom: 16px;
		right: 16px;
		z-index: 100;
		display: flex;
		flex-direction: column;
		gap: 8px;
		pointer-events: none;
	}

	.toast {
		pointer-events: auto;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 16px;
		border-radius: 12px;
		box-shadow: var(--shadow-lg);
		min-width: 280px;
		max-width: 400px;
		color: #ffffff;
	}

	.toast-success {
		background: var(--color-success-500);
	}

	.toast-error {
		background: var(--color-error-500);
	}

	.toast-warning {
		background: var(--color-warning-500);
	}

	.toast-info {
		background: var(--color-primary-500);
	}

	.toast-icon {
		flex-shrink: 0;
	}

	.toast-icon :global(.icon) {
		width: 20px;
		height: 20px;
	}

	.toast-message {
		flex: 1;
		font-size: 14px;
		font-weight: 500;
		margin: 0;
	}

	.toast-close {
		flex-shrink: 0;
		padding: 4px;
		background: transparent;
		border: none;
		border-radius: 50%;
		color: currentColor;
		cursor: pointer;
		transition: background-color var(--duration-fast) ease;
	}

	.toast-close:hover {
		background: rgba(255, 255, 255, 0.2);
	}

	.close-icon {
		width: 16px;
		height: 16px;
	}
</style>
