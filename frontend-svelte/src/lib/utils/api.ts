/**
 * API client for communicating with Python FastAPI backend
 */

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
};

export { ApiError };
