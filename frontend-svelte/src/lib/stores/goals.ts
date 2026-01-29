/**
 * Goals store - manages user goals and transformations
 */

import { writable, derived } from 'svelte/store';
import { api } from '$utils/api';

export interface Goal {
	id: string;
	userId: string;
	organizationId: string;
	sessionId: string | null;
	goalText: string;
	locked: boolean;
	lockedAt: Date | null;
	metricTargets: Record<string, any> | null;
	matrixRows: Record<string, any> | null;
	matrixColumns: Record<string, any> | null;
	intent: string | null;
	domain: string | null;
	createdAt: Date;
	updatedAt: Date;
}

export interface MatrixValue {
	id: string;
	goalId: string;
	valueId: string;
	cellRow: string;
	cellColumn: string;
	dimensionName: string;
	dimensionIndex: number;
	currentValue: number;
	targetValue: number;
	gap: number;
}

interface GoalsState {
	goals: Goal[];
	currentGoal: Goal | null;
	matrixValues: MatrixValue[];
	isLoading: boolean;
	error: string | null;
}

const initialState: GoalsState = {
	goals: [],
	currentGoal: null,
	matrixValues: [],
	isLoading: false,
	error: null,
};

function transformGoal(g: any): Goal {
	return {
		id: g.id,
		userId: g.user_id,
		organizationId: g.organization_id,
		sessionId: g.session_id,
		goalText: g.goal_text,
		locked: g.locked,
		lockedAt: g.locked_at ? new Date(g.locked_at) : null,
		metricTargets: g.metric_targets,
		matrixRows: g.matrix_rows,
		matrixColumns: g.matrix_columns,
		intent: g.intent,
		domain: g.domain,
		createdAt: new Date(g.created_at),
		updatedAt: new Date(g.updated_at),
	};
}

function createGoalsStore() {
	const { subscribe, set, update } = writable<GoalsState>(initialState);

	return {
		subscribe,

		async loadGoals(options: { locked?: boolean; limit?: number; offset?: number } = {}) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const params = new URLSearchParams();
				if (options.locked !== undefined) params.append('locked', options.locked.toString());
				if (options.limit) params.append('limit', options.limit.toString());
				if (options.offset) params.append('offset', options.offset.toString());

				const response = await api.get<{ goals: any[]; total: number }>(
					`/api/goals?${params.toString()}`
				);

				update(state => ({
					...state,
					goals: response.goals.map(transformGoal),
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

		async loadGoal(goalId: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.get<any>(`/api/goals/${goalId}`);
				const goal = transformGoal(response);
				update(state => ({
					...state,
					currentGoal: goal,
					isLoading: false,
				}));
				return goal;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async createGoal(data: {
			title: string;
			description?: string;
			sessionId?: string;
			intent?: string;
			domain?: string;
		}) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.post<any>('/api/goals', {
					goal_text: data.title + (data.description ? `\n${data.description}` : ''),
					session_id: data.sessionId,
					intent: data.intent,
					domain: data.domain,
				});
				const goal = transformGoal(response);
				update(state => ({
					...state,
					goals: [goal, ...state.goals],
					currentGoal: goal,
					isLoading: false,
				}));
				return goal;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async updateGoal(
			goalId: string,
			updates: {
				goalText?: string;
				locked?: boolean;
				metricTargets?: Record<string, any>;
				matrixRows?: Record<string, any>;
				matrixColumns?: Record<string, any>;
				intent?: string;
				domain?: string;
			}
		) {
			try {
				const response = await api.patch<any>(`/api/goals/${goalId}`, {
					goal_text: updates.goalText,
					locked: updates.locked,
					metric_targets: updates.metricTargets,
					matrix_rows: updates.matrixRows,
					matrix_columns: updates.matrixColumns,
					intent: updates.intent,
					domain: updates.domain,
				});
				const goal = transformGoal(response);
				update(state => ({
					...state,
					currentGoal: goal,
					goals: state.goals.map(g => (g.id === goalId ? goal : g)),
				}));
				return goal;
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
				return null;
			}
		},

		async lockGoal(goalId: string) {
			return this.updateGoal(goalId, { locked: true });
		},

		async unlockGoal(goalId: string) {
			return this.updateGoal(goalId, { locked: false });
		},

		async deleteGoal(goalId: string) {
			try {
				await api.delete(`/api/goals/${goalId}`);
				update(state => ({
					...state,
					goals: state.goals.filter(g => g.id !== goalId),
					currentGoal: state.currentGoal?.id === goalId ? null : state.currentGoal,
				}));
				return true;
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
				return false;
			}
		},

		async loadMatrix(goalId: string) {
			try {
				const response = await api.get<any[]>(`/api/goals/${goalId}/matrix`);
				update(state => ({
					...state,
					matrixValues: response.map(v => ({
						id: v.id,
						goalId: v.goal_id,
						valueId: v.value_id,
						cellRow: v.cell_row,
						cellColumn: v.cell_column,
						dimensionName: v.dimension_name,
						dimensionIndex: v.dimension_index,
						currentValue: v.current_value,
						targetValue: v.target_value,
						gap: v.gap,
					})),
				}));
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
			}
		},

		setCurrentGoal(goal: Goal | null) {
			update(state => ({ ...state, currentGoal: goal }));
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},

		reset() {
			set(initialState);
		},
	};
}

export const goals = createGoalsStore();

// Derived stores
export const currentGoal = derived(goals, $goals => $goals.currentGoal);
export const activeGoals = derived(goals, $goals =>
	$goals.goals.filter(g => !g.locked)
);
export const completedGoals = derived(goals, $goals =>
	$goals.goals.filter(g => g.locked)
);
