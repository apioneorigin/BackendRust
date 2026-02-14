/**
 * App Layout Server
 * Loads user data and initial state for authenticated pages.
 *
 * Uses SvelteKit's `fetch` (routes through hooks.server.ts proxy)
 * instead of hardcoded BACKEND_URL — single source of truth for
 * backend routing and auth in every environment.
 */

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, fetch }) => {
	// User is guaranteed to exist here due to hooks.server.ts guard
	const user = locals.user;

	// Load organization and conversations in parallel via SvelteKit proxy
	// (hooks.server.ts adds auth from cookie and routes to backend)
	const [orgResult, convsResult] = await Promise.allSettled([
		fetch('/api/organization').then(r => r.ok ? r.json() : null),
		fetch('/api/chat/conversations').then(r => r.ok ? r.json() : null),
	]);

	const organization = orgResult.status === 'fulfilled' ? orgResult.value : null;
	const convsData = convsResult.status === 'fulfilled' ? convsResult.value : null;
	const conversations = convsData?.conversations ?? [];

	return {
		user,
		organization,
		conversations
	};
};
