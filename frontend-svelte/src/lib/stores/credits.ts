/**
 * Credits store - manages credit balance and usage
 */

import { writable, derived } from 'svelte/store';
import { api } from '$utils/api';

export interface CreditBalance {
	creditsEnabled: boolean;
	creditQuota: number | null;
	organizationUsed: number;
	organizationMax: number;
	percentageUsed: number;
}

export interface Redemption {
	id: string;
	promoCodeId: string;
	credits: number;
	redeemedAt: Date;
}

export interface UsageRecord {
	id: string;
	usageType: string;
	quantity: number;
	metadata: Record<string, any> | null;
	createdAt: Date;
}

interface CreditsState {
	balance: CreditBalance | null;
	redemptions: Redemption[];
	usageHistory: UsageRecord[];
	isLoading: boolean;
	error: string | null;
}

const initialState: CreditsState = {
	balance: null,
	redemptions: [],
	usageHistory: [],
	isLoading: false,
	error: null,
};

function createCreditsStore() {
	const { subscribe, set, update } = writable<CreditsState>(initialState);

	return {
		subscribe,

		async loadBalance() {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.get<{
					credits_enabled: boolean;
					credit_quota: number | null;
					organization_used: number;
					organization_max: number;
					percentage_used: number;
				}>('/api/user/credits');
				update(state => ({
					...state,
					balance: {
						creditsEnabled: response.credits_enabled,
						creditQuota: response.credit_quota,
						organizationUsed: response.organization_used,
						organizationMax: response.organization_max,
						percentageUsed: response.percentage_used,
					},
					isLoading: false,
				}));
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
			}
		},

		async redeemCode(code: string) {
			update(state => ({ ...state, isLoading: true }));
			try {
				const response = await api.post<{
					id: string;
					promo_code_id: string;
					credits: number;
					redeemed_at: string;
				}>('/api/credits/redeem', { code });

				const redemption: Redemption = {
					id: response.id,
					promoCodeId: response.promo_code_id,
					credits: response.credits,
					redeemedAt: new Date(response.redeemed_at),
				};

				update(state => ({
					...state,
					redemptions: [redemption, ...state.redemptions],
					isLoading: false,
				}));

				// Reload balance after redemption
				this.loadBalance();

				return redemption;
			} catch (error: any) {
				update(state => ({
					...state,
					error: error.message,
					isLoading: false,
				}));
				throw error;
			}
		},

		async loadRedemptionHistory(limit: number = 20) {
			try {
				const response = await api.get<Array<{
					id: string;
					promo_code_id: string;
					credits: number;
					redeemed_at: string;
				}>>(`/api/credits/history?limit=${limit}`);

				update(state => ({
					...state,
					redemptions: response.map(r => ({
						id: r.id,
						promoCodeId: r.promo_code_id,
						credits: r.credits,
						redeemedAt: new Date(r.redeemed_at),
					})),
				}));
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
			}
		},

		async loadUsageHistory(limit: number = 50) {
			try {
				const response = await api.get<Array<{
					id: string;
					usage_type: string;
					quantity: number;
					metadata: Record<string, any> | null;
					created_at: string;
				}>>(`/api/usage/history?limit=${limit}`);

				update(state => ({
					...state,
					usageHistory: response.map(r => ({
						id: r.id,
						usageType: r.usage_type,
						quantity: r.quantity,
						metadata: r.metadata,
						createdAt: new Date(r.created_at),
					})),
				}));
			} catch (error: any) {
				update(state => ({ ...state, error: error.message }));
			}
		},

		clearError() {
			update(state => ({ ...state, error: null }));
		},

		reset() {
			set(initialState);
		},
	};
}

export const credits = createCreditsStore();

// Derived stores
export const creditBalance = derived(credits, $credits => $credits.balance);
export const isLowCredits = derived(credits, $credits => {
	if (!$credits.balance) return false;
	return $credits.balance.percentageUsed >= 80;
});
