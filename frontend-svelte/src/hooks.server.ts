/**
 * SvelteKit Server Hooks
 * Handles authentication middleware and request processing
 */

import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_COOKIE = 'auth_token';

// Routes that don't require authentication
const PUBLIC_ROUTES = ['/login', '/register', '/api', '/healthz'];

// Routes accessible with 0 credits (add-credits page + credits page for redeeming)
const ZERO_CREDIT_ROUTES = ['/add-credits', '/credits', '/logout'];

export const handle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get(AUTH_COOKIE);

	// Try to get user if token exists
	if (token) {
		try {
			const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				const user = await response.json();
				event.locals.user = user;
				event.locals.token = token;
			} else {
				// Invalid token - clear it
				event.cookies.delete(AUTH_COOKIE, { path: '/' });
				event.locals.user = null;
				event.locals.token = null;
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
