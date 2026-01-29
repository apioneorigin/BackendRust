/**
 * Authentication store - replaces AuthContext from React
 */

import { writable, derived, get } from 'svelte/store';
import { api } from '$utils/api';

export interface User {
	id: string;
	email: string;
	name: string | null;
	role: string;
	organization_id: string;
	credits_enabled: boolean;
	credit_quota: number | null;
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
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,

		// Alias for initialize - used by layout
		async loadUser() {
			return this.initialize();
		},

		async initialize() {
			update(state => ({ ...state, isLoading: true, error: null }));
			try {
				const user = await api.get<User>('/api/auth/me');
				const org = await api.get<Organization>('/api/organization');
				update(state => ({
					...state,
					user,
					organization: org,
					isAuthenticated: true,
					isLoading: false,
				}));
				return user;
			} catch (error) {
				update(state => ({
					...state,
					user: null,
					organization: null,
					isAuthenticated: false,
					isLoading: false,
				}));
				return null;
			}
		},

		async login(email: string, password: string) {
			update(state => ({ ...state, isLoading: true, error: null }));
			try {
				const response = await api.post<{ token: string; user: User }>('/api/auth/login', {
					email,
					password,
				});
				api.setToken(response.token);
				const org = await api.get<Organization>('/api/organization');
				update(state => ({
					...state,
					user: response.user,
					organization: org,
					isAuthenticated: true,
					isLoading: false,
				}));
				return true;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message || 'Login failed',
					isLoading: false,
				}));
				return false;
			}
		},

		async register(email: string, password: string, name?: string, organizationName?: string) {
			update(state => ({ ...state, isLoading: true, error: null }));
			try {
				const response = await api.post<{ token: string; user: User }>('/api/auth/register', {
					email,
					password,
					name,
					organization_name: organizationName,
				});
				api.setToken(response.token);
				const org = await api.get<Organization>('/api/organization');
				update(state => ({
					...state,
					user: response.user,
					organization: org,
					isAuthenticated: true,
					isLoading: false,
				}));
				return true;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message || 'Registration failed',
					isLoading: false,
				}));
				return false;
			}
		},

		async logout() {
			try {
				await api.post('/api/auth/logout', {});
			} catch (error) {
				// Ignore logout errors
			}
			api.clearToken();
			set(initialState);
			update(state => ({ ...state, isLoading: false }));
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
