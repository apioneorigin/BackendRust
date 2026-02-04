/**
 * App Layout Client Load
 * Initializes client-side state from server data BEFORE rendering
 */

import type { LayoutLoad } from './$types';
import { api } from '$lib/utils/api';
import { chat } from '$lib/stores';
import { browser } from '$app/environment';

export const load: LayoutLoad = async ({ data }) => {
	// Set token for API calls (before any client-side requests)
	if (browser && data.token) {
		api.setToken(data.token);
	}

	// Initialize conversations store from server data (before component renders)
	if (browser && data.conversations) {
		chat.setConversations(data.conversations);
	}

	// Pass through server data
	return {
		user: data.user,
		token: data.token,
		organization: data.organization,
		conversations: data.conversations
	};
};
