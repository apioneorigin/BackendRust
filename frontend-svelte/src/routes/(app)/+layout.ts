/**
 * App Layout Client Load
 * Initializes client-side state from server data BEFORE rendering
 */

import type { LayoutLoad } from './$types';
import { chat } from '$lib/stores';
import { browser } from '$app/environment';

export const load: LayoutLoad = async ({ data }) => {
	// Initialize conversations store from server data (before component renders)
	if (browser && data.conversations) {
		chat.setConversations(data.conversations);
	}

	// Pass through server data
	return {
		user: data.user,
		organization: data.organization,
		conversations: data.conversations
	};
};
