import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const user = locals.user as any;
	if (!user?.isGlobalAdmin) {
		redirect(302, '/chat');
	}
};
