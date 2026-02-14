/**
 * Chat store - replaces UnifiedChatContext from React
 * Handles conversations, messages, streaming, goals, insights, questions
 */

import { writable, derived } from 'svelte/store';
import { api } from '$utils/api';
import { matrix } from './matrix';
import { addToast } from './toast';

export interface Message {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	cosData?: any;
	feedback?: 'up' | 'down' | null;
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
	messageId?: string;
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

// Message cache for instant conversation switching (LRU, max 20 entries)
const MAX_CACHE_SIZE = 20;
const messageCache = new Map<string, { messages: Message[]; questions: Question[]; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes cache validity

function cacheSet(key: string, value: { messages: Message[]; questions: Question[]; timestamp: number }) {
	// Delete first so re-insertion moves key to end (Map preserves insertion order)
	messageCache.delete(key);
	messageCache.set(key, value);
	// Evict oldest entries if over limit
	if (messageCache.size > MAX_CACHE_SIZE) {
		const oldest = messageCache.keys().next().value;
		if (oldest !== undefined) messageCache.delete(oldest);
	}
}

function createChatStore() {
	const { subscribe, set, update } = writable<ChatState>(initialState);

	// AbortControllers for cancellable operations (SvelteKit-native pattern)
	let selectConversationController: AbortController | null = null;
	let loadConversationsController: AbortController | null = null;
	let streamController: AbortController | null = null;
	let streamReader: ReadableStreamDefaultReader<Uint8Array> | null = null;

	return {
		subscribe,

		// Set conversations from server data (SSR)
		setConversations(convs: Conversation[]) {
			update(state => ({
				...state,
				conversations: convs
			}));
		},

		async loadConversations() {
			// Cancel any in-flight request
			if (loadConversationsController) {
				loadConversationsController.abort();
			}
			loadConversationsController = new AbortController();
			const { signal } = loadConversationsController;

			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.get<{ conversations: Conversation[] }>('/api/chat/conversations', { signal });
				update(state => ({
					...state,
					conversations: response.conversations,
					isLoading: false,
				}));
			} catch (error: any) {
				// Ignore abort errors (expected when cancelling)
				if (error.name === 'AbortError') return;
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
			} finally {
				loadConversationsController = null;
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
			// Guard against invalid ID
			if (!conversationId) return;

			// Check if already viewing this conversation
			let shouldProceed = false;
			update(state => {
				if (state.currentConversation?.id === conversationId) {
					return state; // No change needed
				}
				shouldProceed = true;
				return { ...state, isLoading: true, error: null };
			});

			if (!shouldProceed) return;

			// Cancel any in-flight selection request (allows rapid clicks)
			if (selectConversationController) {
				selectConversationController.abort();
			}
			selectConversationController = new AbortController();
			const { signal } = selectConversationController;

			// Check cache for instant display
			const cached = messageCache.get(conversationId);
			const isCacheValid = cached && (Date.now() - cached.timestamp) < CACHE_TTL;

			if (isCacheValid) {
				// Instant display from cache
				update(state => ({
					...state,
					messages: cached.messages,
					questions: cached.questions,
					isLoading: false,
				}));
			}

			try {
				// Load all data in parallel — conversation+messages are required, documents+questions are optional
				const results = await Promise.allSettled([
					api.get<Conversation>(`/api/chat/conversations/${conversationId}`, { signal }),
					api.get<Message[]>(`/api/chat/conversations/${conversationId}/messages`, { signal }),
					api.get<any[]>(`/api/matrix/${conversationId}/documents`, { signal }),
					api.get<Question[]>(`/api/chat/conversations/${conversationId}/questions`, { signal }),
				]);

				if (signal.aborted) return;

				// Required: conversation and messages must succeed
				if (results[0].status === 'rejected') throw results[0].reason;
				if (results[1].status === 'rejected') throw results[1].reason;

				const conversation = results[0].value;
				const messagesResponse = results[1].value;

				// Optional: documents and questions can fail gracefully
				let documentsResponse: any[] = [];
				let questionsResponse: Question[] = [];

				if (results[2].status === 'fulfilled') {
					documentsResponse = results[2].value;
				} else if ((results[2].reason as any)?.name !== 'AbortError') {
					console.error('Failed to load documents:', results[2].reason);
				}

				if (results[3].status === 'fulfilled') {
					questionsResponse = results[3].value;
				} else if ((results[3].reason as any)?.name !== 'AbortError') {
					console.error('Failed to load questions:', results[3].reason);
				}

				// Transform questions from API format to store format
				const questions: Question[] = (Array.isArray(questionsResponse) ? questionsResponse : []).map(q => ({
					id: q.id,
					text: q.text,
					options: q.options,
					selectedOption: q.selectedOption,
					messageId: q.messageId
				}));

				const messages = Array.isArray(messagesResponse) ? messagesResponse : [];

				// Update cache (LRU eviction)
				cacheSet(conversationId, {
					messages,
					questions,
					timestamp: Date.now()
				});

				update(state => ({
					...state,
					currentConversation: conversation,
					messages,
					questions,
					isLoading: false,
				}));

				// Reset matrix and set conversation ID — must run before any matrix operations
				// initializeMatrix clears stale docs from the previous conversation
				matrix.initializeMatrix();
				matrix.setConversationId(conversationId);

				// Apply documents to matrix store if present (new architecture)
				const documents = Array.isArray(documentsResponse) ? documentsResponse : [];
				if (documents.length > 0) {
					matrix.populateFromStructuredData({ documents });
				}
			} catch (error: any) {
				// Ignore abort errors (expected when user clicks rapidly)
				if (error.name === 'AbortError') return;
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
			} finally {
				selectConversationController = null;
			}
		},

		async sendMessage(content: string, model: string = 'claude-opus-4-5-20251101', attachments: { name: string; content: string; type: string; encoding: string }[] = [], webSearch: boolean = true) {
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
				// Clear stale matrix data from the previous conversation
				matrix.initializeMatrix();
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

			streamController = new AbortController();

			try {
				// Use direct backend connection for SSE (bypasses Vite proxy buffering)
				const response = await api.sseStream(
					`/api/chat/conversations/${conversationId}/messages`,
					{
						content,
						model,
						web_search_data: webSearch,
						web_search_insights: webSearch,
						attachments: attachments.length > 0 ? attachments : undefined,
					},
					streamController.signal
				);

				if (!response.ok) {
					throw new Error('Failed to send message');
				}

				const reader = response.body?.getReader();
				streamReader = reader ?? null;
				const decoder = new TextDecoder();

				if (!reader) {
					throw new Error('No response body');
				}

				let fullContent = '';
				let buffer = '';

				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					const chunk = decoder.decode(value, { stream: true });
					buffer += chunk;
					// SSE uses \r\n per spec, normalize to \n for parsing
					buffer = buffer.replace(/\r\n/g, '\n');
					const events = buffer.split('\n\n');
					buffer = events.pop() || '';

					for (const event of events) {
						if (!event.trim()) continue;

						// Parse SSE event format: "event: type\ndata: json"
						const eventMatch = event.match(/^event:\s*(\w+)\ndata:\s*(.+)$/s);
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

								case 'error':
									// Backend pipeline error — surface to user
									update(state => ({
										...state,
										error: parsed.message || 'An error occurred',
										isStreaming: false,
										streamingContent: '',
									}));
									addToast('error', parsed.message || 'An error occurred');
									break;
								case 'done':
									// Message complete
									break;
							}
						} catch {
							// Malformed SSE event — skip
						}
					}
				}

				// Only add assistant message if content was received (skip on error/empty)
				if (fullContent) {
					const assistantMessage: Message = {
						id: `msg-${Date.now()}`,
						role: 'assistant',
						content: fullContent,
						createdAt: new Date(),
					};

					update(state => {
						const updatedMessages = [...state.messages, assistantMessage];
						const updatedQuestions = state.questions.map(q =>
							!q.messageId ? { ...q, messageId: assistantMessage.id } : q
						);

						// Update LRU cache so conversation switch-back shows current data
						if (conversationId) {
							cacheSet(conversationId, {
								messages: updatedMessages,
								questions: updatedQuestions,
								timestamp: Date.now()
							});
						}

						return {
							...state,
							messages: updatedMessages,
							isStreaming: false,
							streamingContent: '',
							questions: updatedQuestions,
						};
					});
				} else {
					update(state => ({
						...state,
						isStreaming: false,
						streamingContent: '',
					}));
				}

				// Title is now generated in Call 1 and sent via SSE 'title' event

			} catch (error: any) {
				if (error.name === 'AbortError') {
					// User cancelled — keep partial content as a message if any
					update(state => {
						const partial = state.streamingContent;
						const partialMsgId = `msg-${Date.now()}`;
						return {
							...state,
							messages: partial
								? [...state.messages, { id: partialMsgId, role: 'assistant' as const, content: partial, createdAt: new Date() }]
								: state.messages,
							isStreaming: false,
							streamingContent: '',
							// Link stream questions to partial message (or leave unlinked if no content)
							questions: partial
								? state.questions.map(q => !q.messageId ? { ...q, messageId: partialMsgId } : q)
								: state.questions,
						};
					});
				} else {
					update(state => ({
						...state,
						error: error.message,
						isStreaming: false,
						streamingContent: '',
					}));
				}
			} finally {
				streamController = null;
				streamReader = null;
			}
		},

		stopStreaming() {
			if (streamReader) {
				streamReader.cancel().catch(() => {});
			}
			if (streamController) {
				streamController.abort();
			}
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
			// Save previous selection for rollback
			let previousOption: string | undefined;
			update(state => {
				const q = state.questions.find(q => q.id === questionId);
				previousOption = q?.selectedOption;
				return {
					...state,
					questions: state.questions.map(q =>
						q.id === questionId ? { ...q, selectedOption: optionId } : q
					),
				};
			});

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
					// Rollback on failure
					update(state => ({
						...state,
						questions: state.questions.map(q =>
							q.id === questionId ? { ...q, selectedOption: previousOption } : q
						),
					}));
					addToast('error', 'Failed to save answer');
				}
			}
		},

		async rateMessage(messageId: string, feedback: 'up' | 'down' | null) {
			// Save previous feedback for rollback
			let previousFeedback: 'up' | 'down' | null | undefined;
			update(state => {
				const m = state.messages.find(m => m.id === messageId);
				previousFeedback = m?.feedback ?? null;
				return {
					...state,
					messages: state.messages.map(m =>
						m.id === messageId ? { ...m, feedback } : m
					),
				};
			});

			// Persist to backend
			let conversationId: string | null = null;
			update(state => {
				conversationId = state.currentConversation?.id || null;
				return state;
			});

			if (conversationId) {
				try {
					await api.patch(`/api/chat/conversations/${conversationId}/messages/${messageId}/feedback`, {
						feedback
					});
				} catch (error) {
					console.error('Failed to persist message feedback:', error);
					// Rollback on failure
					update(state => ({
						...state,
						messages: state.messages.map(m =>
							m.id === messageId ? { ...m, feedback: previousFeedback ?? null } : m
						),
					}));
					addToast('error', 'Failed to save feedback');
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
			set(initialState);
		},
	};
}

export const chat = createChatStore();

// Derived stores - always return valid types, never undefined
export const currentConversation = derived(chat, $chat => $chat.currentConversation);
export const conversations = derived(chat, $chat => $chat.conversations ?? []);
export const messages = derived(chat, $chat => $chat.messages ?? []);
export const goals = derived(chat, $chat => $chat.goals);
export const insights = derived(chat, $chat => $chat.insights);
export const questions = derived(chat, $chat => $chat.questions);
export const isStreaming = derived(chat, $chat => $chat.isStreaming);
export const streamingContent = derived(chat, $chat => $chat.streamingContent);
