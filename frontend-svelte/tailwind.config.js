/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: ['selector', '[data-theme="dark"]'],
	theme: {
		// Mobile-first breakpoints
		screens: {
			xs: '375px',
			sm: '640px',
			md: '768px',
			lg: '1024px',
			xl: '1280px',
			'2xl': '1536px'
		},
		extend: {
			colors: {
				// Primary (Gunmetal Gray - sophistication, depth, modernity)
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
					950: 'var(--color-primary-950)'
				},
				// Accent (Gunmetal Gray)
				accent: 'var(--color-accent)',
				// Challenger (Warm Orange)
				challenger: 'var(--color-challenger)',
				// Field colors
				field: {
					void: 'var(--color-field-void)',
					depth: 'var(--color-field-depth)',
					surface: 'var(--color-field-surface)',
					elevated: 'var(--color-field-elevated)',
					'void-dark': 'var(--color-field-void)',
					'depth-dark': 'var(--color-field-depth)',
					'surface-dark': 'var(--color-field-surface)',
					'elevated-dark': 'var(--color-field-elevated)'
				},
				// Text colors
				text: {
					source: 'var(--color-text-source)',
					manifest: 'var(--color-text-manifest)',
					flow: 'var(--color-text-flow)',
					whisper: 'var(--color-text-whisper)',
					hint: 'var(--color-text-hint)',
					'source-dark': 'var(--color-text-source)',
					'manifest-dark': 'var(--color-text-manifest)',
					'flow-dark': 'var(--color-text-flow)',
					'whisper-dark': 'var(--color-text-whisper)',
					'hint-dark': 'var(--color-text-hint)'
				},
				// Veil (borders)
				veil: {
					thin: 'var(--color-veil-thin)',
					present: 'var(--color-veil-present)',
					clear: 'var(--color-veil-clear)',
					'thin-dark': 'var(--color-veil-thin)',
					'present-dark': 'var(--color-veil-present)',
					'clear-dark': 'var(--color-veil-clear)'
				},
				// Glow
				glow: {
					whisper: 'var(--color-glow-whisper)',
					breath: 'var(--color-glow-breath)',
					pulse: 'var(--color-glow-pulse)',
					radiance: 'var(--color-glow-radiance)',
					luminance: 'var(--color-glow-luminance)'
				},
				// Semantic colors
				error: {
					500: 'var(--color-error-500)',
					600: 'var(--color-error-600)',
					700: 'var(--color-error-700)'
				},
				success: {
					500: 'var(--color-success-500)',
					600: 'var(--color-success-600)'
				},
				warning: {
					500: 'var(--color-warning-500)',
					600: 'var(--color-warning-600)'
				}
			},
			fontFamily: {
				sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
				mono: ['JetBrains Mono', 'Fira Code', 'monospace']
			},
			fontSize: {
				'2xs': ['0.75rem', { lineHeight: '1rem' }],
				xs: ['0.8125rem', { lineHeight: '1.125rem' }],
				sm: ['0.875rem', { lineHeight: '1.25rem' }],
				base: ['1rem', { lineHeight: '1.5rem' }],
				lg: ['1.125rem', { lineHeight: '1.75rem' }],
				xl: ['1.25rem', { lineHeight: '1.75rem' }],
				'2xl': ['1.5rem', { lineHeight: '2rem' }],
				'3xl': ['1.875rem', { lineHeight: '2.25rem' }]
			},
			spacing: {
				0.5: '2px',
				1: '4px',
				1.5: '6px',
				2: '8px',
				2.5: '10px',
				3: '12px',
				3.5: '14px',
				4: '16px',
				5: '20px',
				6: '24px',
				7: '28px',
				8: '32px',
				10: '40px',
				11: '44px',
				12: '48px',
				13: '52px',
				14: '56px',
				16: '64px',
				20: '80px',
				'safe-top': 'env(safe-area-inset-top, 0px)',
				'safe-bottom': 'env(safe-area-inset-bottom, 0px)',
				'safe-left': 'env(safe-area-inset-left, 0px)',
				'safe-right': 'env(safe-area-inset-right, 0px)'
			},
			height: {
				touch: '44px',
				'touch-comfortable': '48px',
				'touch-large': '56px',
				'input-mobile': '52px',
				'input-desktop': '48px',
				'tab-mobile': '56px',
				'tab-desktop': '48px',
				dvh: '100dvh',
				svh: '100svh',
				lvh: '100lvh'
			},
			minHeight: {
				touch: '44px',
				'touch-comfortable': '48px',
				'touch-large': '56px',
				'input-mobile': '52px'
			},
			minWidth: {
				touch: '44px',
				'touch-comfortable': '48px',
				'touch-large': '56px'
			},
			borderRadius: {
				xs: '4px',
				sm: '6px',
				DEFAULT: '8px',
				md: '8px',
				lg: '12px',
				xl: '16px',
				'2xl': '20px',
				'3xl': '24px'
			},
			boxShadow: {
				xs: 'var(--shadow-xs)',
				sm: 'var(--shadow-sm)',
				DEFAULT: 'var(--shadow-md)',
				md: 'var(--shadow-md)',
				lg: 'var(--shadow-lg)',
				xl: 'var(--shadow-xl)',
				'glow-whisper': 'var(--shadow-glow-whisper)',
				'glow-breath': 'var(--shadow-glow-breath)',
				'glow-pulse': 'var(--shadow-glow-pulse)',
				'glow-radiance': 'var(--shadow-glow-radiance)',
				card: 'var(--shadow-card)',
				'card-hover': 'var(--shadow-card-hover)',
				'card-active': 'var(--shadow-card-active)',
				'btn-primary': 'var(--shadow-btn-primary)',
				'btn-primary-hover': 'var(--shadow-btn-primary-hover)',
				inner: 'var(--shadow-inner)'
			},
			transitionDuration: {
				instant: '50ms',
				swift: '100ms',
				smooth: '150ms',
				gentle: '200ms',
				graceful: '300ms',
				patient: '400ms'
			},
			transitionTimingFunction: {
				'ease-out': 'cubic-bezier(0.33, 1, 0.68, 1)',
				'ease-in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
				spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)'
			},
			animation: {
				spin: 'spin 1s linear infinite',
				'fade-in': 'fadeIn 0.2s ease-out',
				'slide-up': 'slideUp 0.25s ease-out',
				'slide-down': 'slideDown 0.25s ease-out',
				'scale-in': 'scaleIn 0.2s ease-out',
				'typing-pulse': 'typing-pulse 1.2s ease-in-out infinite',
				'skeleton-pulse': 'skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
			},
			keyframes: {
				fadeIn: {
					from: { opacity: '0', transform: 'translateY(-4px)' },
					to: { opacity: '1', transform: 'translateY(0)' }
				},
				slideUp: {
					from: { opacity: '0', transform: 'translateY(8px)' },
					to: { opacity: '1', transform: 'translateY(0)' }
				},
				slideDown: {
					from: { opacity: '0', transform: 'translateY(-8px)' },
					to: { opacity: '1', transform: 'translateY(0)' }
				},
				scaleIn: {
					from: { opacity: '0', transform: 'scale(0.95)' },
					to: { opacity: '1', transform: 'scale(1)' }
				},
				'typing-pulse': {
					'0%, 80%, 100%': { transform: 'scale(0.8)', opacity: '0.4' },
					'40%': { transform: 'scale(1)', opacity: '1' }
				},
				'skeleton-pulse': {
					'0%, 100%': { opacity: '1' },
					'50%': { opacity: '0.4' }
				}
			},
			backgroundImage: {
				'gradient-primary': 'var(--gradient-primary)',
				'gradient-accent': 'var(--gradient-accent)',
				'gradient-field-presence': 'var(--gradient-field-presence)'
			},
			zIndex: {
				60: '60',
				70: '70',
				80: '80',
				90: '90',
				100: '100'
			}
		}
	},
	plugins: []
};
