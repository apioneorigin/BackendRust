/**
 * Register Page Server
 * Handles user registration via form actions
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
		const name = data.get('name')?.toString() || undefined;
		const email = data.get('email')?.toString();
		const password = data.get('password')?.toString();
		const confirmPassword = data.get('confirmPassword')?.toString();

		if (!email || !password) {
			return fail(400, { error: 'Email and password are required', email, name });
		}

		if (password !== confirmPassword) {
			return fail(400, { error: 'Passwords do not match', email, name });
		}

		if (password.length < 8) {
			return fail(400, { error: 'Password must be at least 8 characters', email, name });
		}

		try {
			const response = await fetch(`${BACKEND_URL}/auth/register`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password, name })
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return fail(response.status, {
					error: errorData.detail || 'Registration failed',
					email,
					name
				});
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
			if (result.user?.isGlobalAdmin) {
				throw redirect(302, '/chat');
			}

			// Regular new users need to add credits
			throw redirect(302, '/add-credits');
		} catch (error) {
			if (error instanceof Response || (error as any)?.status === 302) {
				throw error; // Re-throw redirects
			}
			return fail(500, { error: 'Registration failed. Please try again.', email, name });
		}
	}
};
