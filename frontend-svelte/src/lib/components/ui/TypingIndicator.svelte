<script lang="ts">
	export let size: 'sm' | 'md' | 'lg' = 'md';
</script>

<div class="typing-dots">
	<div class="typing-dot size-{size}"></div>
	<div class="typing-dot size-{size}"></div>
	<div class="typing-dot size-{size}"></div>
</div>

<style>
	.typing-dots {
		display: flex;
		gap: 4px;
		align-items: center;
	}

	.typing-dot {
		border-radius: 50%;
		background: var(--color-text-whisper);
		animation: typing-pulse 1.2s ease-in-out infinite;
	}

	.typing-dot:nth-child(1) { animation-delay: 0s; }
	.typing-dot:nth-child(2) { animation-delay: 0.15s; }
	.typing-dot:nth-child(3) { animation-delay: 0.3s; }

	/* Sizes */
	.size-sm {
		width: 6px;
		height: 6px;
	}

	.size-md {
		width: 8px;
		height: 8px;
	}

	.size-lg {
		width: 12px;
		height: 12px;
	}
</style>
