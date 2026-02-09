/**
 * Login Page Server
 * Handles authentication via form actions
 */

import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_COOKIE = 'auth_token';

export const load: PageServerLoad = async ({ locals }) => {
	// Already authenticated - redirect to app
	if (locals.user) {
		throw redirect(302, '/chat');
	}
	return {};
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const email = data.get('email')?.toString();
		const password = data.get('password')?.toString();

		if (!email || !password) {
			return fail(400, { error: 'Email and password are required', email });
		}

		try {
			const response = await fetch(`${BACKEND_URL}/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password })
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				const message =
					response.status >= 500
						? 'Server error — please try again later'
						: errorData.detail || errorData.error || 'Invalid email or password';
				return fail(response.status, { error: message, email });
			}

			const result = await response.json();

			// Set HttpOnly cookie
			cookies.set(AUTH_COOKIE, result.token, {
				path: '/',
				httpOnly: true,
				secure: process.env.NODE_ENV === 'production',
				sameSite: 'lax',
				maxAge: 60 * 60 * 24 * 7 // 7 days
			});

			// Super admins bypass credit requirements
			// Regular users with 0 credits go to add-credits
			if (
				!result.user?.isGlobalAdmin &&
				result.user?.credits_enabled &&
				(result.user?.credit_quota === 0 || result.user?.credit_quota === null)
			) {
				throw redirect(302, '/add-credits');
			}

			throw redirect(302, '/chat');
		} catch (error) {
			if (error instanceof Response || (error as any)?.status === 302) {
				throw error; // Re-throw redirects
			}
			return fail(500, { error: 'Login failed. Please try again.', email });
		}
	}
};
