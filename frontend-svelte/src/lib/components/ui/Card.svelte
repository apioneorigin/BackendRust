<script lang="ts">
	export let variant: 'default' | 'floating' | 'elevated' | 'subtle' = 'default';
	export let padding: 'none' | 'sm' | 'md' | 'lg' = 'md';
	export let hoverable = false;
</script>

<div
	class="card card-{variant} padding-{padding}"
	class:hoverable
>
	<slot />
</div>

<style>
	.card {
		transition: all var(--duration-normal) var(--ease-out);
	}

	/* Variants */
	.card-default {
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 12px;
	}

	.card-floating {
		background: var(--color-field-surface);
		border-radius: 12px;
		box-shadow: var(--shadow-lg);
	}

	.card-elevated {
		background: var(--color-field-surface);
		box-shadow: var(--shadow-elevated);
		border-radius: 12px;
	}

	.card-subtle {
		background: var(--color-field-surface);
		border-radius: 8px;
	}

	/* Padding */
	.padding-none {
		padding: 0;
	}

	.padding-sm {
		padding: 12px;
	}

	.padding-md {
		padding: 16px;
	}

	.padding-lg {
		padding: 24px;
	}

	/* Hover state */
	.hoverable {
		cursor: pointer;
	}

	.hoverable:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-lg);
	}
</style>
