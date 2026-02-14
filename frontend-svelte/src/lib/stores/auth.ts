/**
 * Authentication store
 *
 * Auth flow is fully SvelteKit-native:
 * - Login/register: SvelteKit form actions (+page.server.ts) set HttpOnly cookie
 * - Logout: POST /logout (+server.ts) clears cookie and calls backend
 * - Hydration: +layout.server.ts passes user/token from hooks.server.ts locals
 *
 * This store holds the client-side reactive state — it never calls the API directly.
 */

import { writable, derived } from 'svelte/store';

export interface User {
	id: string;
	email: string;
	name: string | null;
	role: string;
	organization_id: string;
	credits_enabled: boolean;
	credit_quota: number | null;
	isGlobalAdmin?: boolean;
}

export interface Organization {
	id: string;
	name: string;
	slug: string;
	subscription_tier: string;
	subscription_status: string;
}

interface AuthState {
	user: User | null;
	organization: Organization | null;
	isAuthenticated: boolean;
	isLoading: boolean;
	error: string | null;
}

const initialState: AuthState = {
	user: null,
	organization: null,
	isAuthenticated: false,
	isLoading: true,
	error: null,
};

function createAuthStore() {
	const { subscribe, update } = writable<AuthState>(initialState);

	return {
		subscribe,

		/**
		 * Hydrate auth store from server-side data (no API call needed).
		 * Called by +layout.svelte with data from +layout.server.ts.
		 */
		setFromServer(userData: User | null, org?: Organization | null) {
			update(state => ({
				...state,
				user: userData,
				organization: org !== undefined ? org : state.organization,
				isAuthenticated: !!userData,
				isLoading: false,
				error: null,
			}));
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},
	};
}

export const auth = createAuthStore();

// Derived stores for convenience
export const user = derived(auth, $auth => $auth.user);
export const organization = derived(auth, $auth => $auth.organization);
export const isAuthenticated = derived(auth, $auth => $auth.isAuthenticated);
export const isLoading = derived(auth, $auth => $auth.isLoading);
