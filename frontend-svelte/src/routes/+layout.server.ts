/**
 * Root Layout Server
 * Provides user data and auth token to all pages via SSR
 */

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		user: locals.user,
		token: locals.token  // Pass token to client for API calls
	};
};
