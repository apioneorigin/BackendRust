<script lang="ts">
	export let size: 'sm' | 'md' | 'lg' = 'md';

	$: dotSize = {
		sm: 'w-1.5 h-1.5',
		md: 'w-2 h-2',
		lg: 'w-3 h-3'
	}[size];
</script>

<div class="typing-dots">
	<div class="typing-dot {dotSize}"></div>
	<div class="typing-dot {dotSize}"></div>
	<div class="typing-dot {dotSize}"></div>
</div>
