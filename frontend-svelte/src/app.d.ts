/// <reference types="@sveltejs/kit" />

declare global {
	namespace App {
		interface Locals {
			user: {
				id: string;
				email: string;
				name: string | null;
				role: string;
				organization_id: string;
				credits_enabled: boolean;
				credit_quota: number | null;
				isGlobalAdmin?: boolean;
			} | null;
			token: string | null;
		}

		interface PageData {
			user: App.Locals['user'];
		}
	}
}

export {};
