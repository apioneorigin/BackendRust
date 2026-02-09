<script lang="ts">
	import { onMount } from 'svelte';
	import { auth, theme } from '$lib/stores';
	import { ToastContainer } from '$lib/components/ui';
	import type { LayoutData } from './$types';
	import '../styles/globals.css';

	export let data: LayoutData;

	// Hydrate auth store from server data (avoids client-side /api/auth/me call)
	$: if (data.user) {
		auth.setFromServer(data.user as any);
	}

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


<div class="app" data-theme={$theme.isDark ? 'dark' : 'light'}>
	<slot />
	<ToastContainer />
</div>

<style>
	.app {
		height: 100dvh;
		min-height: 100dvh;
		background-color: var(--color-field-void);
		color: var(--color-text-manifest);
		transition:
			background-color 0.2s ease,
			color 0.2s ease;
		overflow: hidden;
	}
</style>
