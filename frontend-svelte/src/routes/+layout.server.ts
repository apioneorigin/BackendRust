/**
 * Root Layout Server
 * Provides user data to all pages via SSR
 */

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		user: locals.user
	};
};
