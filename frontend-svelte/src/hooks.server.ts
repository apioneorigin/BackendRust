/**
 * SvelteKit Server Hooks
 *
 * Handles:
 * 1. API proxy — ALL /api/* requests are proxied to the backend with
 *    auth from HttpOnly cookies, /api prefix stripped, and native SSE
 *    streaming support. This is the single source of truth for API
 *    routing in every environment (dev, docker, DO App Platform).
 * 2. Auth middleware — validates tokens and guards protected routes.
 */

import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_COOKIE = 'auth_token';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

// Routes that don't require authentication
const PUBLIC_ROUTES = ['/login', '/register', '/api', '/healthz'];

// Routes accessible with 0 credits (add-credits page + credits page for redeeming)
const ZERO_CREDIT_ROUTES = ['/add-credits', '/credits', '/logout'];

/** Set (or refresh) the auth cookie with a rolling maxAge. */
function setCookie(cookies: any, token: string) {
	cookies.set(AUTH_COOKIE, token, {
		path: '/',
		httpOnly: true,
		secure: process.env.NODE_ENV === 'production',
		sameSite: 'lax' as const,
		maxAge: COOKIE_MAX_AGE,
	});
}

/**
 * Try to refresh an expired token via the backend /auth/refresh endpoint.
 * Returns the new token on success, or null if refresh failed.
 */
async function tryRefreshToken(oldToken: string): Promise<string | null> {
	try {
		const response = await fetch(`${BACKEND_URL}/auth/refresh`, {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${oldToken}`,
				'Content-Type': 'application/json',
			},
		});
		if (response.ok) {
			const data = await response.json();
			return data.token || null;
		}
	} catch {
		// Refresh failed — caller will handle
	}
	return null;
}

export const handle: Handle = async ({ event, resolve }) => {
	// ── API Proxy ────────────────────────────────────────────────────────
	// Intercept ALL /api/* requests and proxy to the backend.
	// Strips the /api prefix: /api/chat/... → BACKEND_URL/chat/...
	// Attaches auth token from HttpOnly cookie as Bearer header.
	// Streams SSE responses natively — no buffering, no external proxy needed.
	if (event.url.pathname.startsWith('/api/')) {
		const token = event.cookies.get(AUTH_COOKIE);
		const backendPath = event.url.pathname.replace(/^\/api/, '') + event.url.search;

		const headers: Record<string, string> = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		// Forward client IP for backend rate limiting + session logging
		// (backend reads X-Forwarded-For via security/middleware.py get_client_ip)
		const clientIp = event.request.headers.get('x-forwarded-for')
			|| event.getClientAddress();
		headers['X-Forwarded-For'] = clientIp;

		// Forward content-type and body for non-GET requests
		const contentType = event.request.headers.get('content-type');
		if (contentType) {
			headers['Content-Type'] = contentType;
		}

		const init: RequestInit = {
			method: event.request.method,
			headers,
		};

		// Forward body for methods that have one
		if (event.request.method !== 'GET' && event.request.method !== 'HEAD') {
			init.body = event.request.body;
			// @ts-expect-error -- Node fetch supports duplex streaming
			init.duplex = 'half';
		}

		let backendResponse: Response;
		try {
			backendResponse = await fetch(`${BACKEND_URL}${backendPath}`, init);
		} catch {
			return new Response(
				JSON.stringify({ detail: 'Backend unavailable' }),
				{ status: 502, headers: { 'Content-Type': 'application/json' } }
			);
		}

		// On 401, try to refresh the token and retry the request once.
		// The backend accepts expired JWTs if the DB session is still valid,
		// so this handles the case where the JWT expired but the session
		// was extended by the sliding window.
		if (backendResponse.status === 401 && token) {
			const newToken = await tryRefreshToken(token);
			if (newToken) {
				// Update cookie with fresh token
				setCookie(event.cookies, newToken);

				// Retry the original request with the new token
				const retryHeaders = { ...headers, 'Authorization': `Bearer ${newToken}` };
				try {
					backendResponse = await fetch(`${BACKEND_URL}${backendPath}`, {
						...init,
						headers: retryHeaders,
					});
				} catch {
					return new Response(
						JSON.stringify({ detail: 'Backend unavailable' }),
						{ status: 502, headers: { 'Content-Type': 'application/json' } }
					);
				}
			}
		}

		// Rolling cookie: extend maxAge on every successful API call so
		// active users never have their cookie expire from under them.
		if (token && backendResponse.status >= 200 && backendResponse.status < 400) {
			setCookie(event.cookies, token);
		}

		// Stream the response back with original headers
		const responseHeaders = new Headers();
		const backendContentType = backendResponse.headers.get('content-type') || '';
		responseHeaders.set('Content-Type', backendContentType);

		// SSE-specific headers — disable all buffering
		if (backendContentType.includes('text/event-stream')) {
			responseHeaders.set('Cache-Control', 'no-cache, no-transform');
			responseHeaders.set('Connection', 'keep-alive');
			responseHeaders.set('X-Accel-Buffering', 'no');
		}

		return new Response(backendResponse.body, {
			status: backendResponse.status,
			headers: responseHeaders,
		});
	}

	// ── Auth Middleware ───────────────────────────────────────────────────
	let token = event.cookies.get(AUTH_COOKIE);

	// Try to get user if token exists
	if (token) {
		try {
			const response = await fetch(`${BACKEND_URL}/auth/me`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				const user = await response.json();
				event.locals.user = user;
				event.locals.token = token;

				// Rolling cookie: extend maxAge on every page load so the
				// cookie lifetime slides forward with user activity.
				setCookie(event.cookies, token);
			} else {
				// Token might be expired — try to refresh before giving up
				const newToken = await tryRefreshToken(token);
				if (newToken) {
					// Retry /auth/me with the new token
					const retryResponse = await fetch(`${BACKEND_URL}/auth/me`, {
						headers: {
							'Authorization': `Bearer ${newToken}`,
							'Content-Type': 'application/json'
						}
					});
					if (retryResponse.ok) {
						const user = await retryResponse.json();
						event.locals.user = user;
						event.locals.token = newToken;
						setCookie(event.cookies, newToken);
						token = newToken;
					} else {
						// Refresh succeeded but /auth/me still failed — clear cookie
						event.cookies.delete(AUTH_COOKIE, { path: '/' });
						event.locals.user = null;
						event.locals.token = null;
					}
				} else {
					// Refresh failed — clear cookie and force re-login
					event.cookies.delete(AUTH_COOKIE, { path: '/' });
					event.locals.user = null;
					event.locals.token = null;
				}
			}
		} catch {
			// Backend unreachable
			event.locals.user = null;
			event.locals.token = null;
		}
	} else {
		event.locals.user = null;
		event.locals.token = null;
	}

	// Check if route requires auth
	const isPublicRoute = PUBLIC_ROUTES.some(route => event.url.pathname.startsWith(route));
	const isAuthPage = event.url.pathname === '/login' || event.url.pathname === '/register';

	// Redirect authenticated users away from auth pages
	if (isAuthPage && event.locals.user) {
		throw redirect(302, '/chat');
	}

	// Redirect unauthenticated users to login (except public routes)
	if (!isPublicRoute && !event.locals.user) {
		throw redirect(302, '/login');
	}

	// Redirect 0-credit users to add-credits page (skip for allowed routes)
	if (event.locals.user && !isPublicRoute) {
		const user = event.locals.user as any;
		const isZeroCreditRoute = ZERO_CREDIT_ROUTES.some(route => event.url.pathname.startsWith(route));
		if (
			user.credits_enabled &&
			(user.credit_quota === 0 || user.credit_quota === null) &&
			!user.isGlobalAdmin &&
			user.role !== 'SUPER_ADMIN' &&
			!isZeroCreditRoute
		) {
			throw redirect(302, '/add-credits');
		}
	}

	return resolve(event);
};
