<script lang="ts">
	export let variant: 'default' | 'floating' | 'elevated' | 'subtle' = 'default';
	export let padding: 'none' | 'sm' | 'md' | 'lg' = 'md';
	export let hoverable = false;

	$: variantClasses = {
		default: 'bg-field-surface border border-veil-thin rounded-xl',
		floating: 'card-floating',
		elevated: 'card-elevated',
		subtle: 'card-subtle'
	}[variant];

	$: paddingClasses = {
		none: '',
		sm: 'p-3',
		md: 'p-4',
		lg: 'p-6'
	}[padding];
</script>

<div
	class="
		{variantClasses}
		{paddingClasses}
		{hoverable ? 'hover-lift cursor-pointer' : ''}
		transition-all duration-gentle
	"
>
	<slot />
</div>
