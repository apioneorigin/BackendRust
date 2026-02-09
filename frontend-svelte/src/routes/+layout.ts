/**
 * Root Layout Client Load
 * Sets API token for pages outside the (app) group (e.g. /add-credits)
 */

import type { LayoutLoad } from './$types';
import { api } from '$lib/utils/api';
import { browser } from '$app/environment';

export const load: LayoutLoad = async ({ data }) => {
	if (browser && data.token) {
		api.setToken(data.token);
	}

	return {
		user: data.user,
		token: data.token
	};
};
