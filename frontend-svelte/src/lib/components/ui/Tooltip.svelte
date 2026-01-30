<script lang="ts">
	export let content: string;
	export let position: 'top' | 'bottom' | 'left' | 'right' = 'top';
	export let delay = 200;

	let visible = false;
	let timeout: ReturnType<typeof setTimeout>;

	function show() {
		timeout = setTimeout(() => {
			visible = true;
		}, delay);
	}

	function hide() {
		clearTimeout(timeout);
		visible = false;
	}

	$: positionClasses = {
		top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
		bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
		left: 'right-full top-1/2 -translate-y-1/2 mr-2',
		right: 'left-full top-1/2 -translate-y-1/2 ml-2'
	}[position];

	$: arrowClasses = {
		top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900 border-x-transparent border-b-transparent',
		bottom:
			'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900 border-x-transparent border-t-transparent',
		left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900 border-y-transparent border-r-transparent',
		right:
			'right-full top-1/2 -translate-y-1/2 border-r-gray-900 border-y-transparent border-l-transparent'
	}[position];
</script>

<div
	class="relative inline-flex"
	on:mouseenter={show}
	on:mouseleave={hide}
	on:focus={show}
	on:blur={hide}
	role="tooltip"
>
	<slot />

	{#if visible && content}
		<div
			class="
				absolute z-50 {positionClasses}
				px-2.5 py-1.5
				text-xs font-medium text-white
				bg-gray-900 dark:bg-gray-800
				rounded-md shadow-lg
				whitespace-nowrap
				animate-fade-in
				pointer-events-none
			"
		>
			{content}
			<div
				class="absolute w-0 h-0 border-4 {arrowClasses}"
			/>
		</div>
	{/if}
</div>
