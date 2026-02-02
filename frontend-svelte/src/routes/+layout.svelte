<script lang="ts">
	import { onMount } from 'svelte';
	import { auth, theme } from '$lib/stores';
	import { ToastContainer } from '$lib/components/ui';
	import '../styles/globals.css';

	// Initialize theme on mount
	onMount(() => {
		// Check for system preference
		const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		const savedTheme = localStorage.getItem('theme');

		if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
			theme.setDark();
		} else {
			theme.setLight();
		}

		// Try to load user on mount
		auth.loadUser();

		// Listen for system theme changes
		const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
		const handleChange = (e: MediaQueryListEvent) => {
			if (!localStorage.getItem('theme')) {
				if (e.matches) {
					theme.setDark();
				} else {
					theme.setLight();
				}
			}
		};
		mediaQuery.addEventListener('change', handleChange);

		return () => {
			mediaQuery.removeEventListener('change', handleChange);
		};
	});
</script>


<div class="app h-dvh" data-theme={$theme.isDark ? 'dark' : 'light'}>
	<slot />
	<ToastContainer />
</div>

<style>
	.app {
		min-height: 100dvh;
		background-color: var(--color-field-void);
		color: var(--color-text-manifest);
		transition:
			background-color 0.2s ease,
			color 0.2s ease;
		overflow: hidden;
	}
</style>
