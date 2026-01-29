/**
 * Documents store - manages document state
 */

import { writable, derived } from 'svelte/store';
import { api } from '$utils/api';

export interface Document {
	id: string;
	userId: string;
	organizationId: string;
	title: string;
	sections: Record<string, any>;
	format: string;
	domain: string | null;
	version: string;
	isActive: boolean;
	conversationId: string;
	goalTitle: string | null;
	goalId: string | null;
	name: string | null;
	cells: Record<string, any> | null;
	cascadeRules: Record<string, any> | null;
	createdAt: Date;
	lastUpdatedAt: Date;
}

interface DocumentsState {
	documents: Document[];
	currentDocument: Document | null;
	total: number;
	isLoading: boolean;
	error: string | null;
}

const initialState: DocumentsState = {
	documents: [],
	currentDocument: null,
	total: 0,
	isLoading: false,
	error: null,
};

function transformDocument(d: any): Document {
	return {
		id: d.id,
		userId: d.user_id,
		organizationId: d.organization_id,
		title: d.title,
		sections: d.sections,
		format: d.format,
		domain: d.domain,
		version: d.version,
		isActive: d.is_active,
		conversationId: d.conversation_id,
		goalTitle: d.goal_title,
		goalId: d.goal_id,
		name: d.name,
		cells: d.cells,
		cascadeRules: d.cascade_rules,
		createdAt: new Date(d.created_at),
		lastUpdatedAt: new Date(d.last_updated_at),
	};
}

function createDocumentsStore() {
	const { subscribe, set, update } = writable<DocumentsState>(initialState);

	return {
		subscribe,

		async loadDocuments(options: { limit?: number; offset?: number; domain?: string } = {}) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const params = new URLSearchParams();
				if (options.limit) params.append('limit', options.limit.toString());
				if (options.offset) params.append('offset', options.offset.toString());
				if (options.domain) params.append('domain', options.domain);

				const response = await api.get<{ documents: any[]; total: number }>(
					`/api/documents/?${params.toString()}`
				);

				update(state => ({
					...state,
					documents: response.documents.map(transformDocument),
					total: response.total,
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

		async loadDocument(documentId: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.get<any>(`/api/documents/${documentId}`);
				const document = transformDocument(response);
				update(state => ({
					...state,
					currentDocument: document,
					isLoading: false,
				}));
				return document;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async createDocument(data: {
			title: string;
			sections: Record<string, any>;
			conversationId: string;
			format?: string;
			domain?: string;
			goalTitle?: string;
			goalId?: string;
		}) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.post<any>('/api/documents/', {
					title: data.title,
					sections: data.sections,
					conversation_id: data.conversationId,
					format: data.format || 'structured_json',
					domain: data.domain,
					goal_title: data.goalTitle,
					goal_id: data.goalId,
				});
				const document = transformDocument(response);
				update(state => ({
					...state,
					documents: [document, ...state.documents],
					currentDocument: document,
					total: state.total + 1,
					isLoading: false,
				}));
				return document;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async updateDocument(
			documentId: string,
			updates: {
				title?: string;
				sections?: Record<string, any>;
				domain?: string;
				cells?: Record<string, any>;
				cascadeRules?: Record<string, any>;
			}
		) {
			try {
				const response = await api.patch<any>(`/api/documents/${documentId}`, {
					title: updates.title,
					sections: updates.sections,
					domain: updates.domain,
					cells: updates.cells,
					cascade_rules: updates.cascadeRules,
				});
				const document = transformDocument(response);
				update(state => ({
					...state,
					currentDocument: document,
					documents: state.documents.map(d =>
						d.id === documentId ? document : d
					),
				}));
				return document;
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
				return null;
			}
		},

		async deleteDocument(documentId: string) {
			try {
				await api.delete(`/api/documents/${documentId}`);
				update(state => ({
					...state,
					documents: state.documents.filter(d => d.id !== documentId),
					currentDocument:
						state.currentDocument?.id === documentId ? null : state.currentDocument,
					total: state.total - 1,
				}));
				return true;
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
				return false;
			}
		},

		setCurrentDocument(document: Document | null) {
			update(state => ({ ...state, currentDocument: document }));
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},

		reset() {
			set(initialState);
		},
	};
}

export const documents = createDocumentsStore();

// Derived stores
export const currentDocument = derived(documents, $documents => $documents.currentDocument);
export const documentList = derived(documents, $documents => $documents.documents);
