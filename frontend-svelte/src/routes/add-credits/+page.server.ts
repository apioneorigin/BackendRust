import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const user = locals.user as any;
	// User already has credits — send them to chat
	if (user?.credit_quota && user.credit_quota > 0) {
		redirect(302, '/chat');
	}
};
