/**
 * Theme store - replaces ThemeContext from React
 */

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
	theme: Theme;
	isDark: boolean;
}

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
	const initialTheme = getInitialTheme();
	const { subscribe, set, update } = writable<ThemeState>({
		theme: initialTheme,
		isDark: getEffectiveTheme(initialTheme) === 'dark'
	});

	function applyTheme(theme: Theme) {
		if (!browser) return;

		const effective = getEffectiveTheme(theme);
		document.documentElement.setAttribute('data-theme', effective);
		localStorage.setItem('theme', theme);
	}

	// Apply initial theme
	if (browser) {
		applyTheme(initialTheme);

		// Listen for system theme changes
		window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
			update(state => {
				if (state.theme === 'system') {
					applyTheme('system');
					return { ...state, isDark: getEffectiveTheme('system') === 'dark' };
				}
				return state;
			});
		});
	}

	return {
		subscribe,

		setTheme(newTheme: Theme) {
			applyTheme(newTheme);
			set({ theme: newTheme, isDark: getEffectiveTheme(newTheme) === 'dark' });
		},

		setLight() {
			this.setTheme('light');
		},

		setDark() {
			this.setTheme('dark');
		},

		toggle() {
			update(state => {
				const newTheme = state.isDark ? 'light' : 'dark';
				applyTheme(newTheme);
				return { theme: newTheme, isDark: newTheme === 'dark' };
			});
		},
	};
}

export const theme = createThemeStore();
