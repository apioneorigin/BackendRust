/**
 * Session store - manages transformation sessions
 */

import { writable, derived, get } from 'svelte/store';
import { api } from '$utils/api';

export interface Session {
	id: string;
	organizationId: string;
	userId: string | null;
	stage: number;
	completed: boolean;
	currentScreen: string;
	goalText: string | null;
	goalData: any | null;
	discoverData: any | null;
	decodeData: any | null;
	designData: any | null;
	dashboardData: any | null;
	lastConversationId: string | null;
	createdAt: Date;
	updatedAt: Date;
	lastAccessedAt: Date;
}

interface SessionState {
	sessions: Session[];
	currentSession: Session | null;
	isLoading: boolean;
	error: string | null;
}

const initialState: SessionState = {
	sessions: [],
	currentSession: null,
	isLoading: false,
	error: null,
};

function createSessionStore() {
	const { subscribe, set, update } = writable<SessionState>(initialState);

	return {
		subscribe,

		async loadSessions() {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.get<{ sessions: Session[] }>('/api/session/');
				update(state => ({
					...state,
					sessions: response.sessions,
					isLoading: false,
				}));
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
			}
		},

		async loadCurrentSession() {
			update(state => ({ ...state, isLoading: true }));
			try {
				const session = await api.get<Session | null>('/api/session/current');
				update(state => ({
					...state,
					currentSession: session,
					isLoading: false,
				}));
				return session;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async createSession(goalText?: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const session = await api.post<Session>('/api/session/create', {
					goal_text: goalText,
				});
				update(state => ({
					...state,
					sessions: [session, ...state.sessions],
					currentSession: session,
					isLoading: false,
				}));
				return session;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async selectSession(sessionId: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const session = await api.get<Session>(`/api/session/${sessionId}`);
				update(state => ({
					...state,
					currentSession: session,
					isLoading: false,
				}));
				return session;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async updateSession(sessionId: string, updates: Partial<Session>) {
			try {
				const session = await api.patch<Session>(`/api/session/${sessionId}`, updates);
				update(state => ({
					...state,
					currentSession: session,
					sessions: state.sessions.map(s =>
						s.id === sessionId ? session : s
					),
				}));
				return session;
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
				return null;
			}
		},

		setScreen(screen: string) {
			const state = get({ subscribe });
			if (state.currentSession) {
				this.updateSession(state.currentSession.id, { currentScreen: screen } as any);
			}
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},

		reset() {
			set(initialState);
		},
	};
}

export const session = createSessionStore();

// Derived stores
export const currentSession = derived(session, $session => $session.currentSession);
export const sessions = derived(session, $session => $session.sessions);
