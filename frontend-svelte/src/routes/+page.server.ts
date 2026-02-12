import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// hooks.server.ts guarantees only authenticated users reach here
	// (unauthenticated → /login, 0-credit → /add-credits already handled)
	redirect(302, '/chat');
};
