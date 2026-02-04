<script lang="ts">
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let color: 'primary' | 'white' | 'current' = 'primary';
</script>

<svg
	class="spinner size-{size} color-{color}"
	xmlns="http://www.w3.org/2000/svg"
	fill="none"
	viewBox="0 0 24 24"
>
	<circle class="track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
	<path
		class="head"
		fill="currentColor"
		d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
	/>
</svg>

<style>
	.spinner {
		animation: spin 1s linear infinite;
	}

	/* Sizes */
	.size-sm {
		width: 16px;
		height: 16px;
	}

	.size-md {
		width: 24px;
		height: 24px;
	}

	.size-lg {
		width: 32px;
		height: 32px;
	}

	/* Colors */
	.color-primary {
		color: var(--color-primary-500);
	}

	.color-white {
		color: #ffffff;
	}

	.color-current {
		color: currentColor;
	}

	.track {
		opacity: 0.25;
	}

	.head {
		opacity: 0.75;
	}
</style>
