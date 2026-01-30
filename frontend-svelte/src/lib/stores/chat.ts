/**
 * Chat store - replaces UnifiedChatContext from React
 * Handles conversations, messages, streaming, goals, insights, questions
 */

import { writable, derived, get } from 'svelte/store';
import { api } from '$utils/api';

export interface Message {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	cosData?: any;
	createdAt: Date;
}

export interface Conversation {
	id: string;
	title: string | null;
	sessionId: string | null;
	isActive: boolean;
	totalTokens: number;
	createdAt: Date;
	updatedAt: Date;
}

export interface Goal {
	id: string;
	text: string;
	category: string;
	confidence: number;
	rating?: 'accept' | 'reject';
}

export interface Insight {
	id: string;
	text: string;
	type: string;
	rating?: 'accept' | 'reject';
}

export interface Question {
	id: string;
	text: string;
	options: { id: string; text: string }[];
	selectedOption?: string;
}

export interface StructuredData {
	matrix_data?: {
		row_options: { id: string; label: string; description?: string }[];
		column_options: { id: string; label: string; description?: string }[];
		cells: Record<string, {
			impact_score: number;
			relationship?: string;
			dimensions: {
				name: string;
				value: number;  // One of [0, 25, 50, 75, 100]
				step_labels: string[];  // 5 contextual labels for this dimension
			}[];
		}>;
	};
	paths?: {
		id: string;
		name: string;
		description?: string;
		risk_level?: string;
		time_horizon?: string;
		steps: { order: number; action: string; rationale?: string }[];
	}[];
	documents?: {
		id: string;
		type: string;
		title: string;
		summary?: string;
		sections?: Record<string, string>;
	}[];
}

interface ChatState {
	conversations: Conversation[];
	currentConversation: Conversation | null;
	messages: Message[];
	goals: Goal[];
	insights: Insight[];
	questions: Question[];
	structuredData: StructuredData | null;
	isLoading: boolean;
	isStreaming: boolean;
	streamingContent: string;
	error: string | null;
}

const initialState: ChatState = {
	conversations: [],
	currentConversation: null,
	messages: [],
	goals: [],
	insights: [],
	questions: [],
	structuredData: null,
	isLoading: false,
	isStreaming: false,
	streamingContent: '',
	error: null,
};

function createChatStore() {
	const { subscribe, set, update } = writable<ChatState>(initialState);

	let abortController: AbortController | null = null;

	return {
		subscribe,

		async loadConversations() {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.get<{ conversations: Conversation[] }>('/api/chat/conversations');
				update(state => ({
					...state,
					conversations: response.conversations,
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

		async createConversation(sessionId?: string, title?: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const conversation = await api.post<Conversation>('/api/chat/conversations', {
					session_id: sessionId,
					title,
				});
				update(state => ({
					...state,
					conversations: [conversation, ...state.conversations],
					currentConversation: conversation,
					messages: [],
					goals: [],
					insights: [],
					questions: [],
					isLoading: false,
				}));
				return conversation;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				return null;
			}
		},

		async selectConversation(conversationId: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const [conversation, messagesResponse] = await Promise.all([
					api.get<Conversation>(`/api/chat/conversations/${conversationId}`),
					api.get<Message[]>(`/api/chat/conversations/${conversationId}/messages`),
				]);
				update(state => ({
					...state,
					currentConversation: conversation,
					messages: messagesResponse,
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

		async sendMessage(content: string, model: string = 'claude-opus-4-5-20251101', files: File[] = [], webSearch: boolean = true) {
			const state = get({ subscribe });
			if (!state.currentConversation) {
				// Create new conversation first
				const conv = await this.createConversation();
				if (!conv) return;
			}

			const currentState = get({ subscribe });
			const conversationId = currentState.currentConversation!.id;

			// Add user message immediately
			const userMessage: Message = {
				id: `temp-${Date.now()}`,
				role: 'user',
				content,
				createdAt: new Date(),
			};

			update(state => ({
				...state,
				messages: [...state.messages, userMessage],
				isStreaming: true,
				streamingContent: '',
			}));

			// Cancel any existing stream
			if (abortController) {
				abortController.abort();
			}
			abortController = new AbortController();

			try {
				const response = await fetch(`/api/chat/conversations/${conversationId}/messages`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					credentials: 'include',
					body: JSON.stringify({
						content,
						model,
						web_search_data: webSearch,
						web_search_insights: webSearch,
					}),
					signal: abortController.signal,
				});

				if (!response.ok) {
					throw new Error('Failed to send message');
				}

				const reader = response.body?.getReader();
				const decoder = new TextDecoder();

				if (!reader) {
					throw new Error('No response body');
				}

				let fullContent = '';
				let buffer = '';

				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					buffer += decoder.decode(value, { stream: true });
					const lines = buffer.split('\n\n');
					buffer = lines.pop() || '';

					for (const line of lines) {
						if (!line.startsWith('event:')) continue;

						const eventMatch = line.match(/^event: (\w+)\ndata: (.+)$/s);
						if (!eventMatch) continue;

						const [, eventType, data] = eventMatch;

						try {
							const parsed = JSON.parse(data);

							switch (eventType) {
								case 'token':
									fullContent += parsed.text || '';
									update(state => ({
										...state,
										streamingContent: fullContent,
									}));
									break;

								case 'goals':
									update(state => ({
										...state,
										goals: [...state.goals, ...parsed],
									}));
									break;

								case 'insights':
									update(state => ({
										...state,
										insights: [...state.insights, ...parsed],
									}));
									break;

								case 'question':
									update(state => ({
										...state,
										questions: [...state.questions, parsed],
									}));
									break;

								case 'structured_data':
									// Store structured matrix/paths/documents data
									update(state => ({
										...state,
										structuredData: parsed,
									}));
									break;

								case 'done':
									// Message complete
									break;
							}
						} catch (e) {
							// Skip unparseable events
						}
					}
				}

				// Add final assistant message
				const assistantMessage: Message = {
					id: `msg-${Date.now()}`,
					role: 'assistant',
					content: fullContent,
					createdAt: new Date(),
				};

				update(state => ({
					...state,
					messages: [...state.messages, assistantMessage],
					isStreaming: false,
					streamingContent: '',
				}));

			} catch (error: any) {
				if (error.name === 'AbortError') {
					update(state => ({
						...state,
						isStreaming: false,
						streamingContent: '',
					}));
					return;
				}

				update(state => ({
					...state,
					error: error.message,
					isStreaming: false,
					streamingContent: '',
				}));
			}
		},

		stopStreaming() {
			if (abortController) {
				abortController.abort();
				abortController = null;
			}
			update(state => ({
				...state,
				isStreaming: false,
				streamingContent: '',
			}));
		},

		rateGoal(goalId: string, rating: 'accept' | 'reject') {
			update(state => ({
				...state,
				goals: state.goals.map(g =>
					g.id === goalId ? { ...g, rating } : g
				),
			}));
		},

		rateInsight(insightId: string, rating: 'accept' | 'reject') {
			update(state => ({
				...state,
				insights: state.insights.map(i =>
					i.id === insightId ? { ...i, rating } : i
				),
			}));
		},

		answerQuestion(questionId: string, optionId: string) {
			update(state => ({
				...state,
				questions: state.questions.map(q =>
					q.id === questionId ? { ...q, selectedOption: optionId } : q
				),
			}));
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},

		reset() {
			if (abortController) {
				abortController.abort();
			}
			set(initialState);
		},
	};
}

export const chat = createChatStore();

// Derived stores
export const currentConversation = derived(chat, $chat => $chat.currentConversation);
export const conversations = derived(chat, $chat => $chat.conversations);
export const messages = derived(chat, $chat => $chat.messages);
export const goals = derived(chat, $chat => $chat.goals);
export const insights = derived(chat, $chat => $chat.insights);
export const questions = derived(chat, $chat => $chat.questions);
export const isStreaming = derived(chat, $chat => $chat.isStreaming);
export const streamingContent = derived(chat, $chat => $chat.streamingContent);
