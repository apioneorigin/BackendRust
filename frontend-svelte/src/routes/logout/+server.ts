/**
 * Logout Server Endpoint
 * Clears the auth cookie and logs out
 */

import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_COOKIE = 'auth_token';

export const POST: RequestHandler = async ({ cookies, locals }) => {
	const token = locals.token;

	// Try to logout from backend
	if (token) {
		try {
			await fetch(`${BACKEND_URL}/api/auth/logout`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});
		} catch {
			// Ignore logout errors
		}
	}

	// Clear the cookie
	cookies.delete(AUTH_COOKIE, { path: '/' });

	throw redirect(302, '/login');
};
