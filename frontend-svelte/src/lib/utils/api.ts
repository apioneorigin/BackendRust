/**
 * API Client for BackendRust
 *
 * Auth is handled entirely server-side by hooks.server.ts:
 *   - Reads HttpOnly auth cookie
 *   - Adds Authorization header to backend proxy
 *   - No client-side token storage needed (eliminates token leak surface)
 *
 * Features:
 * - Retry with exponential backoff
 * - Streaming support (SSE)
 * - Request timeout
 * - Error handling
 */

import { browser } from '$app/environment';
import { goto } from '$app/navigation';

// All API calls go through SvelteKit (same origin)
// hooks.server.ts proxies /api/* to backend with auth from HttpOnly cookie
const API_BASE_URL = '';

interface RequestOptions {
	headers?: Record<string, string>;
	timeout?: number;
	retries?: number;
	signal?: AbortSignal;
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

async function request<T>(
	method: string,
	endpoint: string,
	data?: any,
	options: RequestOptions = {}
): Promise<T> {
	const { headers = {}, timeout = 30000, retries = 3, signal: externalSignal } = options;

	// Bail immediately if already aborted
	if (externalSignal?.aborted) {
		throw new DOMException('The operation was aborted.', 'AbortError');
	}

	const config: RequestInit = {
		method,
		headers: {
			'Content-Type': 'application/json',
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

			// Forward external signal to internal controller
			if (externalSignal) {
				externalSignal.addEventListener('abort', () => controller.abort(), { once: true });
			}

			config.signal = controller.signal;

			const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
			clearTimeout(timeoutId);

			if (!response.ok) {
				// Handle 401 - redirect to login
				if (response.status === 401 && browser) {
					goto('/login');
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

			// Don't retry on abort or client errors (4xx)
			if (error.name === 'AbortError') {
				throw error;
			}
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
	 * SSE stream — same-origin SvelteKit routes, hooks.server.ts adds auth
	 */
	async sseStream(endpoint: string, data?: any, signal?: AbortSignal): Promise<Response> {
		return fetch(`${API_BASE_URL}${endpoint}`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: data ? JSON.stringify(data) : undefined,
			signal,
		});
	},
};

export { ApiError };
