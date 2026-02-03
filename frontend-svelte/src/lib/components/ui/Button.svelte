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

	$: variantClasses = {
		primary:
			'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 shadow-btn-primary hover:shadow-btn-primary-hover',
		secondary:
			'bg-field-elevated text-text-manifest border border-veil-thin hover:bg-field-depth active:bg-field-surface',
		ghost:
			'bg-transparent text-text-flow hover:bg-field-depth hover:text-text-manifest active:bg-field-elevated',
		outline:
			'bg-transparent border border-veil-present text-text-manifest hover:bg-field-depth hover:border-veil-clear active:bg-field-elevated',
		danger:
			'bg-error-500 text-white hover:bg-error-600 active:bg-error-700'
	}[variant];

	$: sizeClasses = {
		sm: 'h-8 px-3 text-xs rounded-lg gap-1.5',
		md: 'h-10 px-4 text-sm rounded-lg gap-2',
		lg: 'h-12 px-6 text-base rounded-lg gap-2.5'
	}[size];
</script>

<button
	{type}
	{disabled}
	class="
		inline-flex items-center justify-center font-medium
		transition-all duration-swift ease-out
		touch-target
		{variantClasses}
		{sizeClasses}
		{fullWidth ? 'w-full' : ''}
		{disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
	"
	class:pointer-events-none={loading}
	on:click={handleClick}
>
	{#if loading}
		<svg
			class="animate-spin h-4 w-4"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
		>
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			/>
		</svg>
	{/if}
	<slot />
</button>
