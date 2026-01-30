/**
 * API Client for BackendRust
 *
 * Features:
 * - Automatic token handling
 * - Retry with exponential backoff
 * - Streaming support (SSE with async generator)
 * - Request timeout
 * - Error handling
 */

import { browser } from '$app/environment';
import { goto } from '$app/navigation';

const API_BASE_URL = '';  // Uses Vite proxy in dev, same origin in prod
const TOKEN_KEY = 'auth_token';

interface RequestOptions {
	headers?: Record<string, string>;
	timeout?: number;
	retries?: number;
}

class ApiError extends Error {
	constructor(
		message: string,
		public status: number,
		public data?: any
	) {
		super(message);
		this.name = 'ApiError';
	}
}

function getToken(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string): void {
	if (typeof window === 'undefined') return;
	localStorage.setItem(TOKEN_KEY, token);
}

function clearToken(): void {
	if (typeof window === 'undefined') return;
	localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(
	method: string,
	endpoint: string,
	data?: any,
	options: RequestOptions = {}
): Promise<T> {
	const { headers = {}, timeout = 30000, retries = 3 } = options;

	const token = getToken();
	const authHeaders: Record<string, string> = {};
	if (token) {
		authHeaders['Authorization'] = `Bearer ${token}`;
	}

	const config: RequestInit = {
		method,
		headers: {
			'Content-Type': 'application/json',
			...authHeaders,
			...headers,
		},
	};

	if (data && method !== 'GET') {
		config.body = JSON.stringify(data);
	}

	let lastError: Error | null = null;

	for (let attempt = 0; attempt < retries; attempt++) {
		try {
			const controller = new AbortController();
			const timeoutId = setTimeout(() => controller.abort(), timeout);
			config.signal = controller.signal;

			const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
			clearTimeout(timeoutId);

			if (!response.ok) {
				// Handle 401 - redirect to login
				if (response.status === 401) {
					clearToken();
					if (browser) {
						goto('/login');
					}
				}
				const errorData = await response.json().catch(() => ({}));
				throw new ApiError(
					errorData.detail || errorData.message || `Request failed with status ${response.status}`,
					response.status,
					errorData
				);
			}

			// Handle empty responses
			const text = await response.text();
			if (!text) return {} as T;

			return JSON.parse(text);
		} catch (error: any) {
			lastError = error;

			// Don't retry on client errors (4xx)
			if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
				throw error;
			}

			// Exponential backoff for retries
			if (attempt < retries - 1) {
				await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
			}
		}
	}

	throw lastError || new Error('Request failed');
}

export const api = {
	get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
		return request<T>('GET', endpoint, undefined, options);
	},

	post<T>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
		return request<T>('POST', endpoint, data, options);
	},

	put<T>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
		return request<T>('PUT', endpoint, data, options);
	},

	patch<T>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
		return request<T>('PATCH', endpoint, data, options);
	},

	delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
		return request<T>('DELETE', endpoint, undefined, options);
	},

	/**
	 * Raw fetch for streaming responses (SSE)
	 */
	async stream(endpoint: string, data?: any, options?: RequestOptions): Promise<Response> {
		const token = getToken();
		const authHeaders: Record<string, string> = {};
		if (token) {
			authHeaders['Authorization'] = `Bearer ${token}`;
		}

		const config: RequestInit = {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				...authHeaders,
				...options?.headers,
			},
		};

		if (data) {
			config.body = JSON.stringify(data);
		}

		return fetch(`${API_BASE_URL}${endpoint}`, config);
	},

	setToken,
	clearToken,
	getToken,

	/**
	 * Async generator for SSE streaming responses
	 * Yields parsed data from each SSE event
	 */
	async *streamGenerator(
		endpoint: string,
		data?: any,
		options?: RequestOptions
	): AsyncGenerator<string, void, unknown> {
		const token = getToken();
		const authHeaders: Record<string, string> = {};
		if (token) {
			authHeaders['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}${endpoint}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'text/event-stream',
				...authHeaders,
				...options?.headers,
			},
			body: data ? JSON.stringify(data) : undefined,
		});

		if (!response.ok) {
			throw new ApiError(
				`Stream request failed: ${response.status}`,
				response.status
			);
		}

		const reader = response.body?.getReader();
		if (!reader) {
			throw new Error('No response body');
		}

		const decoder = new TextDecoder();
		let buffer = '';

		try {
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || '';

				for (const line of lines) {
					if (line.startsWith('data: ')) {
						const eventData = line.slice(6);
						if (eventData === '[DONE]') {
							return;
						}
						yield eventData;
					}
				}
			}

			// Process any remaining data in buffer
			if (buffer.startsWith('data: ')) {
				const eventData = buffer.slice(6);
				if (eventData !== '[DONE]') {
					yield eventData;
				}
			}
		} finally {
			reader.releaseLock();
		}
	},
};

export { ApiError };
