<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let open = false;
	export let title = 'Confirm';
	export let message = 'Are you sure?';
	export let confirmText = 'Delete';
	export let cancelText = 'Cancel';
	export let variant: 'danger' | 'warning' | 'default' = 'danger';

	const dispatch = createEventDispatcher<{ confirm: void; cancel: void }>();

	function handleConfirm() {
		dispatch('confirm');
		open = false;
	}

	function handleCancel() {
		dispatch('cancel');
		open = false;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') handleCancel();
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) handleCancel();
	}
</script>

{#if open}
	<div
		class="confirm-overlay"
		on:click={handleBackdropClick}
		on:keydown={handleKeydown}
		role="dialog"
		aria-modal="true"
		aria-labelledby="confirm-title"
		tabindex="-1"
	>
		<div class="confirm-dialog">
			<div class="confirm-icon" class:danger={variant === 'danger'} class:warning={variant === 'warning'}>
				{#if variant === 'danger'}
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
					</svg>
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" /><path d="M12 9v4" /><path d="M12 17h.01" />
					</svg>
				{/if}
			</div>
			<h3 id="confirm-title" class="confirm-title">{title}</h3>
			<p class="confirm-message">{message}</p>
			<div class="confirm-actions">
				<button class="btn-cancel" on:click={handleCancel}>{cancelText}</button>
				<button class="btn-confirm" class:danger={variant === 'danger'} class:warning={variant === 'warning'} on:click={handleConfirm}>
					{confirmText}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.confirm-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 1rem;
		animation: fadeIn 0.15s ease;
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	.confirm-dialog {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		padding: 1.5rem;
		width: 100%;
		max-width: 360px;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
		border: 1px solid var(--color-veil-thin);
		text-align: center;
		animation: slideUp 0.15s ease;
	}

	@keyframes slideUp {
		from { opacity: 0; transform: translateY(8px) scale(0.98); }
		to { opacity: 1; transform: translateY(0) scale(1); }
	}

	.confirm-icon {
		width: 48px;
		height: 48px;
		margin: 0 auto 1rem;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.confirm-icon.danger {
		background: var(--color-error-50);
		color: var(--color-error-500);
	}

	.confirm-icon.warning {
		background: rgba(217, 119, 6, 0.1);
		color: var(--color-warning-500);
	}

	.confirm-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.confirm-message {
		font-size: 0.875rem;
		color: var(--color-text-manifest);
		line-height: 1.5;
		margin-bottom: 1.25rem;
	}

	.confirm-actions {
		display: flex;
		gap: 0.625rem;
	}

	.btn-cancel,
	.btn-confirm {
		flex: 1;
		padding: 0.625rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.btn-cancel {
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-present);
		color: var(--color-text-manifest);
	}

	.btn-cancel:hover {
		background: var(--color-veil-present);
		color: var(--color-text-source);
	}

	.btn-confirm {
		background: var(--color-primary-500);
		border: none;
		color: white;
	}

	.btn-confirm:hover {
		background: var(--color-primary-600);
	}

	.btn-confirm.danger {
		background: var(--color-error-500);
	}

	.btn-confirm.danger:hover {
		background: var(--color-error-600);
	}

	.btn-confirm.warning {
		background: var(--color-warning-500);
	}

	.btn-confirm.warning:hover {
		background: var(--color-warning-600);
	}
</style>
