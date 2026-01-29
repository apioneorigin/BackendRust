/**
 * Theme store - replaces ThemeContext from React
 */

import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark' | 'system';

function getInitialTheme(): Theme {
	if (!browser) return 'system';

	const stored = localStorage.getItem('theme');
	if (stored === 'light' || stored === 'dark' || stored === 'system') {
		return stored;
	}
	return 'system';
}

function getEffectiveTheme(theme: Theme): 'light' | 'dark' {
	if (theme === 'system') {
		if (!browser) return 'light';
		return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
	}
	return theme;
}

function createThemeStore() {
	const { subscribe, set, update } = writable<Theme>(getInitialTheme());

	function applyTheme(theme: Theme) {
		if (!browser) return;

		const effective = getEffectiveTheme(theme);
		document.documentElement.setAttribute('data-theme', effective);
		localStorage.setItem('theme', theme);
	}

	// Apply initial theme
	if (browser) {
		applyTheme(get({ subscribe }));

		// Listen for system theme changes
		window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
			const current = get({ subscribe });
			if (current === 'system') {
				applyTheme('system');
			}
		});
	}

	return {
		subscribe,

		setTheme(theme: Theme) {
			set(theme);
			applyTheme(theme);
		},

		toggle() {
			update(current => {
				const newTheme = getEffectiveTheme(current) === 'dark' ? 'light' : 'dark';
				applyTheme(newTheme);
				return newTheme;
			});
		},
	};
}

export const theme = createThemeStore();
