/**
 * Chat store - replaces UnifiedChatContext from React
 * Handles conversations, messages, streaming, goals, insights, questions
 */

import { writable, derived } from 'svelte/store';
import { api } from '$utils/api';
import { matrix } from './matrix';

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
				value: number;  // 0 (Low), 50 (Medium), or 100 (High)
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
	// Guard flags to prevent concurrent operations that could cause reactive loops
	let isSelectingConversation = false;
	let isLoadingConversations = false;

	return {
		subscribe,

		async loadConversations() {
			// Prevent duplicate concurrent loads
			if (isLoadingConversations) return;
			isLoadingConversations = true;

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
			} finally {
				isLoadingConversations = false;
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
			// Guard against invalid ID or concurrent selection
			if (!conversationId || isSelectingConversation) return;

			// Check and set loading in single update to avoid get() subscription
			let shouldProceed = false;
			update(state => {
				if (state.currentConversation?.id === conversationId) {
					return state; // No change needed
				}
				shouldProceed = true;
				return { ...state, isLoading: true, error: null };
			});

			if (!shouldProceed) return;

			isSelectingConversation = true;

			try {
				// Load conversation, messages, documents, and questions in parallel
				const [conversation, messagesResponse, documentsResponse, questionsResponse] = await Promise.all([
					api.get<Conversation>(`/api/chat/conversations/${conversationId}`),
					api.get<Message[]>(`/api/chat/conversations/${conversationId}/messages`),
					api.get<any[]>(`/api/matrix/${conversationId}/documents`).catch(() => []),
					api.get<Question[]>(`/api/chat/conversations/${conversationId}/questions`).catch(() => []),
				]);

				// Transform questions from API format to store format
				const questions: Question[] = (Array.isArray(questionsResponse) ? questionsResponse : []).map(q => ({
					id: q.id,
					text: q.text,
					options: q.options,
					selectedOption: q.selectedOption
				}));

				update(state => ({
					...state,
					currentConversation: conversation,
					messages: Array.isArray(messagesResponse) ? messagesResponse : [],
					questions,
					isLoading: false,
				}));

				// Apply documents to matrix store if present (new architecture)
				const documents = Array.isArray(documentsResponse) ? documentsResponse : [];
				if (documents.length > 0) {
					matrix.populateFromStructuredData({ documents });
				} else {
					// Reset matrix to default state if no data
					matrix.initializeMatrix();
				}

				// Set conversation ID in matrix store for API calls
				matrix.setConversationId(conversationId);
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
			} finally {
				isSelectingConversation = false;
			}
		},

		async sendMessage(content: string, model: string = 'claude-opus-4-5-20251101', files: File[] = [], webSearch: boolean = true) {
			// Use update() to safely read state without creating synchronous subscription issues
			let isFirstMessage = false;
			let needsNewConversation = false;
			let conversationId: string | null = null;

			update(state => {
				isFirstMessage = state.messages.length === 0;
				needsNewConversation = !state.currentConversation;
				conversationId = state.currentConversation?.id || null;
				return state; // No changes, just reading
			});

			if (needsNewConversation) {
				// Create new conversation first
				const conv = await this.createConversation();
				if (!conv) return;
				conversationId = conv.id;
			}

			if (!conversationId) return; // Safety guard

			// Set conversation ID in matrix store for API calls
			matrix.setConversationId(conversationId);

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
				// Use direct backend connection for SSE (bypasses Vite proxy buffering)
				const response = await api.sseStream(
					`/api/chat/conversations/${conversationId}/messages`,
					{
						content,
						model,
						web_search_data: webSearch,
						web_search_insights: webSearch,
					},
					abortController.signal
				);

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
					if (done) {
						console.log('[SSE] Stream done');
						break;
					}

					const chunk = decoder.decode(value, { stream: true });
					console.log('[SSE] Received chunk:', chunk.length, 'bytes');
					buffer += chunk;
					// SSE uses \r\n per spec, normalize to \n for parsing
					buffer = buffer.replace(/\r\n/g, '\n');
					const events = buffer.split('\n\n');
					buffer = events.pop() || '';

					console.log('[SSE] Parsed events:', events.length);

					for (const event of events) {
						if (!event.trim()) continue;

						// Parse SSE event format: "event: type\ndata: json"
						const eventMatch = event.match(/^event:\s*(\w+)\ndata:\s*(.+)$/s);
						if (!eventMatch) {
							console.log('[SSE] No match for event:', event.substring(0, 100));
							continue;
						}

						const [, eventType, data] = eventMatch;
						console.log('[SSE] Event:', eventType);

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
									// Map backend field names to frontend interface
									const question = {
										id: parsed.question_id,
										text: parsed.question_text,
										options: parsed.options || [],
									};
									update(state => ({
										...state,
										questions: [...state.questions, question],
									}));
									break;

								case 'title':
									// Update conversation title (generated in Call 1)
									if (parsed.title && conversationId) {
										update(state => ({
											...state,
											currentConversation: state.currentConversation
												? { ...state.currentConversation, title: parsed.title }
												: null,
											conversations: state.conversations.map(c =>
												c.id === conversationId ? { ...c, title: parsed.title } : c
											),
										}));
									}
									break;

								case 'structured_data':
									// Store structured matrix/paths/documents data
									update(state => ({
										...state,
										structuredData: parsed,
									}));
									// Apply documents data to matrix store if present (new architecture)
									if (parsed.documents && parsed.documents.length > 0) {
										matrix.populateFromStructuredData(parsed);
									}
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

				// Title is now generated in Call 1 and sent via SSE 'title' event

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

		async generateTitle(conversationId: string) {
			try {
				const result = await api.post<{ title: string; conversation_id: string }>(
					`/api/chat/conversations/${conversationId}/generate-title`
				);
				// Update conversation title in state
				update(state => ({
					...state,
					currentConversation: state.currentConversation
						? { ...state.currentConversation, title: result.title }
						: null,
					conversations: state.conversations.map(c =>
						c.id === conversationId ? { ...c, title: result.title } : c
					),
				}));
			} catch (error) {
				// Title generation is non-critical, don't show error to user
				console.error('Failed to generate title:', error);
			}
		},

		async deleteConversation(conversationId: string) {
			try {
				await api.delete(`/api/chat/conversations/${conversationId}`);

				update(state => {
					const isCurrentConversation = state.currentConversation?.id === conversationId;
					return {
						...state,
						conversations: state.conversations.filter(c => c.id !== conversationId),
						// Clear current conversation if it was deleted
						currentConversation: isCurrentConversation ? null : state.currentConversation,
						messages: isCurrentConversation ? [] : state.messages,
						goals: isCurrentConversation ? [] : state.goals,
						insights: isCurrentConversation ? [] : state.insights,
						questions: isCurrentConversation ? [] : state.questions,
						structuredData: isCurrentConversation ? null : state.structuredData,
					};
				});
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
				}));
				throw error;
			}
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

		async answerQuestion(questionId: string, optionId: string) {
			// Update locally first for immediate UI response
			update(state => ({
				...state,
				questions: state.questions.map(q =>
					q.id === questionId ? { ...q, selectedOption: optionId } : q
				),
			}));

			// Persist to backend
			let conversationId: string | null = null;
			update(state => {
				conversationId = state.currentConversation?.id || null;
				return state;
			});

			if (conversationId) {
				try {
					await api.patch(`/api/chat/conversations/${conversationId}/questions/${questionId}`, {
						selected_option: optionId
					});
				} catch (error) {
					console.error('Failed to persist question answer:', error);
				}
			}
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},

		clearCurrentConversation() {
			// Clear current conversation without creating a new one
			// Used for "New Chat" - actual conversation created on first message
			update(state => ({
				...state,
				currentConversation: null,
				messages: [],
				goals: [],
				insights: [],
				questions: [],
				structuredData: null,
				error: null,
			}));
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
