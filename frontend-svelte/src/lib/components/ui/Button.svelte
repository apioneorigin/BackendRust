<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let variant: 'primary' | 'secondary' | 'ghost' | 'outline' | 'danger' = 'primary';
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let disabled = false;
	export let loading = false;
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let fullWidth = false;

	const dispatch = createEventDispatcher();

	function handleClick(e: MouseEvent) {
		if (!disabled && !loading) {
			dispatch('click', e);
		}
	}
</script>

<button
	{type}
	{disabled}
	class="btn btn-{variant} btn-{size}"
	class:full-width={fullWidth}
	class:is-loading={loading}
	class:is-disabled={disabled || loading}
	on:click={handleClick}
>
	{#if loading}
		<svg
			class="spinner"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
		>
			<circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path
				class="spinner-head"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			/>
		</svg>
	{/if}
	<slot />
</button>

<style>
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-weight: 500;
		border: none;
		cursor: pointer;
		transition: all var(--duration-fast) var(--ease-out);
		min-width: var(--touch-target-min);
		min-height: var(--touch-target-min);
	}

	/* Sizes */
	.btn-sm {
		height: 32px;
		padding: 0 12px;
		font-size: 12px;
		border-radius: 8px;
		gap: 6px;
	}

	.btn-md {
		height: 40px;
		padding: 0 16px;
		font-size: 14px;
		border-radius: 8px;
		gap: 8px;
	}

	.btn-lg {
		height: 48px;
		padding: 0 24px;
		font-size: 16px;
		border-radius: 8px;
		gap: 10px;
	}

	/* Variants */
	.btn-primary {
		background: var(--color-primary-500);
		color: #ffffff;
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.btn-primary:active:not(:disabled) {
		background: var(--color-primary-700);
	}

	.btn-secondary {
		background: var(--color-field-elevated);
		color: var(--color-text-manifest);
		border: 1px solid var(--color-veil-thin);
	}

	.btn-secondary:hover:not(:disabled) {
		background: var(--color-field-depth);
	}

	.btn-secondary:active:not(:disabled) {
		background: var(--color-field-surface);
	}

	.btn-ghost {
		background: transparent;
		color: var(--color-text-flow);
	}

	.btn-ghost:hover:not(:disabled) {
		background: var(--color-field-depth);
		color: var(--color-text-manifest);
	}

	.btn-ghost:active:not(:disabled) {
		background: var(--color-field-elevated);
	}

	.btn-outline {
		background: transparent;
		border: 1px solid var(--color-veil-present);
		color: var(--color-text-manifest);
	}

	.btn-outline:hover:not(:disabled) {
		background: var(--color-field-depth);
		border-color: var(--color-veil-clear);
	}

	.btn-outline:active:not(:disabled) {
		background: var(--color-field-elevated);
	}

	.btn-danger {
		background: var(--color-error-500);
		color: #ffffff;
	}

	.btn-danger:hover:not(:disabled) {
		background: var(--color-error-600);
	}

	/* States */
	.full-width {
		width: 100%;
	}

	.is-disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.is-loading {
		pointer-events: none;
	}

	/* Spinner */
	.spinner {
		width: 16px;
		height: 16px;
		animation: spin 1s linear infinite;
	}

	.spinner-track {
		opacity: 0.25;
	}

	.spinner-head {
		opacity: 0.75;
	}
</style>
