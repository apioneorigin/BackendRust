/**
 * App Layout Server
 * Loads user data and initial state for authenticated pages
 */

import type { LayoutServerLoad } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export const load: LayoutServerLoad = async ({ locals }) => {
	// User is guaranteed to exist here due to hooks.server.ts guard
	const user = locals.user;
	const token = locals.token;

	// Load organization data
	let organization = null;
	if (token) {
		try {
			const response = await fetch(`${BACKEND_URL}/api/organization`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});
			if (response.ok) {
				organization = await response.json();
			}
		} catch {
			// Organization fetch failed - continue without it
		}
	}

	// Load conversations
	let conversations: any[] = [];
	if (token) {
		try {
			const response = await fetch(`${BACKEND_URL}/api/chat/conversations`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});
			if (response.ok) {
				conversations = await response.json();
			}
		} catch {
			// Conversations fetch failed - continue without them
		}
	}

	return {
		user,
		token,  // Pass token to client for API calls
		organization,
		conversations
	};
};
