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

import { browser, dev } from '$app/environment';
import { goto } from '$app/navigation';

const API_BASE_URL = '';  // Uses Vite proxy in dev, same origin in prod
const SSE_BASE_URL = dev ? 'http://localhost:8000' : '';  // Direct backend for SSE (bypasses proxy buffering)

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

// Token stored in memory for client-side API calls
// Token is passed from server via page data (from HttpOnly cookie)
let authToken: string | null = null;

function setToken(token: string | null): void {
	authToken = token;
}

function getToken(): string | null {
	return authToken;
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
				if (response.status === 401 && browser) {
					authToken = null;
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
	 * Set auth token for API calls
	 */
	setToken,

	/**
	 * Get current auth token
	 */
	getToken,

	/**
	 * Clear auth token
	 */
	clearToken(): void {
		authToken = null;
	},

	/**
	 * Raw fetch for streaming responses (SSE)
	 */
	async stream(endpoint: string, data?: any, options?: RequestOptions): Promise<Response> {
		const token = getToken();
		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
			...options?.headers,
		};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		return fetch(`${API_BASE_URL}${endpoint}`, {
			method: 'POST',
			headers,
			body: data ? JSON.stringify(data) : undefined,
		});
	},

	/**
	 * Get SSE base URL for direct backend connection
	 */
	getSSEBaseURL(): string {
		return SSE_BASE_URL;
	},

	/**
	 * SSE stream - uses direct backend with Bearer token
	 */
	async sseStream(endpoint: string, data?: any): Promise<Response> {
		const token = getToken();
		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
		};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		// Use direct backend URL in dev for SSE (avoids proxy buffering issues)
		const baseUrl = dev ? SSE_BASE_URL : API_BASE_URL;

		return fetch(`${baseUrl}${endpoint}`, {
			method: 'POST',
			headers,
			body: data ? JSON.stringify(data) : undefined,
		});
	},
};

export { ApiError };
