/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: ['selector', '[data-theme="dark"]'],
	theme: {
		extend: {
			colors: {
				primary: {
					50: 'var(--color-primary-50)',
					100: 'var(--color-primary-100)',
					200: 'var(--color-primary-200)',
					300: 'var(--color-primary-300)',
					400: 'var(--color-primary-400)',
					500: 'var(--color-primary-500)',
					600: 'var(--color-primary-600)',
					700: 'var(--color-primary-700)',
					800: 'var(--color-primary-800)',
					900: 'var(--color-primary-900)',
				},
				accent: 'var(--color-accent)',
				challenger: 'var(--color-challenger)',
				field: {
					DEFAULT: 'var(--color-field)',
					elevated: 'var(--color-field-elevated)',
					sunken: 'var(--color-field-sunken)',
				},
				text: {
					source: 'var(--color-text-source)',
					manifest: 'var(--color-text-manifest)',
					flow: 'var(--color-text-flow)',
					whisper: 'var(--color-text-whisper)',
					hint: 'var(--color-text-hint)',
				},
				veil: {
					DEFAULT: 'var(--color-veil)',
					soft: 'var(--color-veil-soft)',
					strong: 'var(--color-veil-strong)',
				},
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', 'sans-serif'],
				mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
			},
			screens: {
				xs: '375px',
				sm: '640px',
				md: '768px',
				lg: '1024px',
				xl: '1280px',
				'2xl': '1536px',
			},
			borderRadius: {
				xs: '4px',
				sm: '6px',
				md: '8px',
				lg: '12px',
				xl: '16px',
				'2xl': '20px',
				'3xl': '24px',
			},
			transitionDuration: {
				instant: '50ms',
				swift: '100ms',
				quick: '150ms',
				normal: '200ms',
				relaxed: '300ms',
				patient: '400ms',
			},
			animation: {
				'fade-in': 'fadeIn 0.2s ease-out',
				'slide-up': 'slideUp 0.3s ease-out',
				'thinking-pulse': 'thinkingPulse 1.5s ease-in-out infinite',
			},
			keyframes: {
				fadeIn: {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' },
				},
				slideUp: {
					'0%': { opacity: '0', transform: 'translateY(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' },
				},
				thinkingPulse: {
					'0%, 100%': { opacity: '0.4' },
					'50%': { opacity: '1' },
				},
			},
		},
	},
	plugins: [],
};
