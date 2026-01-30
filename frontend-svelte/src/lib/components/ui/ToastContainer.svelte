<script lang="ts">
	import { toast, type Toast } from '$lib/stores/toast';
	import { fly, fade } from 'svelte/transition';

	function getIcon(type: Toast['type']) {
		switch (type) {
			case 'success':
				return `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>`;
			case 'error':
				return `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>`;
			case 'warning':
				return `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
				</svg>`;
			case 'info':
			default:
				return `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>`;
		}
	}

	function getColorClasses(type: Toast['type']) {
		switch (type) {
			case 'success':
				return 'bg-success-500 text-white';
			case 'error':
				return 'bg-error-500 text-white';
			case 'warning':
				return 'bg-warning-500 text-white';
			case 'info':
			default:
				return 'bg-primary-500 text-white';
		}
	}
</script>

<div
	class="fixed bottom-4 right-4 z-100 flex flex-col gap-2 pointer-events-none"
	aria-live="polite"
	aria-atomic="true"
>
	{#each $toast as item (item.id)}
		<div
			class="
				pointer-events-auto
				flex items-center gap-3
				px-4 py-3
				rounded-xl
				shadow-lg
				{getColorClasses(item.type)}
				min-w-[280px] max-w-[400px]
			"
			in:fly={{ x: 100, duration: 200 }}
			out:fade={{ duration: 150 }}
		>
			<div class="flex-shrink-0">
				{@html getIcon(item.type)}
			</div>
			<p class="flex-1 text-sm font-medium">{item.message}</p>
			<button
				class="flex-shrink-0 p-1 rounded-full hover:bg-white/20 transition-colors"
				on:click={() => toast.remove(item.id)}
				aria-label="Dismiss"
			>
				<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
