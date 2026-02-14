/**
 * Root Layout Client Load
 * Passes server data through to pages
 */

import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ data }) => {
	return {
		user: data.user
	};
};
