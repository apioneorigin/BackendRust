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
</script>

<div
	class="tooltip-wrapper"
	on:mouseenter={show}
	on:mouseleave={hide}
	on:focus={show}
	on:blur={hide}
	role="tooltip"
>
	<slot />

	{#if visible && content}
		<div class="tooltip tooltip-{position}">
			{content}
			<div class="arrow arrow-{position}" />
		</div>
	{/if}
</div>

<style>
	.tooltip-wrapper {
		position: relative;
		display: inline-flex;
	}

	.tooltip {
		position: absolute;
		z-index: 50;
		padding: 6px 10px;
		font-size: 12px;
		font-weight: 500;
		color: #ffffff;
		background: #1f2937;
		border-radius: 6px;
		box-shadow: var(--shadow-lg);
		white-space: nowrap;
		animation: fadeIn 0.15s ease-out;
		pointer-events: none;
	}

	:global([data-theme='dark']) .tooltip {
		background: #374151;
	}

	/* Position variants */
	.tooltip-top {
		bottom: 100%;
		left: 50%;
		transform: translateX(-50%);
		margin-bottom: 8px;
	}

	.tooltip-bottom {
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		margin-top: 8px;
	}

	.tooltip-left {
		right: 100%;
		top: 50%;
		transform: translateY(-50%);
		margin-right: 8px;
	}

	.tooltip-right {
		left: 100%;
		top: 50%;
		transform: translateY(-50%);
		margin-left: 8px;
	}

	/* Arrow */
	.arrow {
		position: absolute;
		width: 0;
		height: 0;
		border: 4px solid transparent;
	}

	.arrow-top {
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		border-top-color: #1f2937;
	}

	.arrow-bottom {
		bottom: 100%;
		left: 50%;
		transform: translateX(-50%);
		border-bottom-color: #1f2937;
	}

	.arrow-left {
		left: 100%;
		top: 50%;
		transform: translateY(-50%);
		border-left-color: #1f2937;
	}

	.arrow-right {
		right: 100%;
		top: 50%;
		transform: translateY(-50%);
		border-right-color: #1f2937;
	}

	:global([data-theme='dark']) .arrow-top {
		border-top-color: #374151;
	}

	:global([data-theme='dark']) .arrow-bottom {
		border-bottom-color: #374151;
	}

	:global([data-theme='dark']) .arrow-left {
		border-left-color: #374151;
	}

	:global([data-theme='dark']) .arrow-right {
		border-right-color: #374151;
	}
</style>
