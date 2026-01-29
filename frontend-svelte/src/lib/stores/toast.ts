/**
 * Toast notification store - replaces ToastContext from React
 */

import { writable, get } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
	id: string;
	type: ToastType;
	message: string;
	duration?: number;
}

function createToastStore() {
	const { subscribe, update } = writable<Toast[]>([]);

	function generateId(): string {
		return Math.random().toString(36).substring(2, 9);
	}

	function addToast(type: ToastType, message: string, duration: number = 5000) {
		const id = generateId();
		const toast: Toast = { id, type, message, duration };

		update(toasts => [...toasts, toast]);

		if (duration > 0) {
			setTimeout(() => {
				removeToast(id);
			}, duration);
		}

		return id;
	}

	function removeToast(id: string) {
		update(toasts => toasts.filter(t => t.id !== id));
	}

	return {
		subscribe,

		success(message: string, duration?: number) {
			return addToast('success', message, duration);
		},

		error(message: string, duration?: number) {
			return addToast('error', message, duration ?? 8000);
		},

		warning(message: string, duration?: number) {
			return addToast('warning', message, duration);
		},

		info(message: string, duration?: number) {
			return addToast('info', message, duration);
		},

		remove(id: string) {
			removeToast(id);
		},

		clear() {
			update(() => []);
		},
	};
}

export const toast = createToastStore();

// Export convenience functions for easier imports
export const addToast = (type: ToastType, title: string, message?: string) => {
	// Handle both (type, message) and (type, title, message) signatures
	const actualMessage = message ?? title;
	switch (type) {
		case 'success':
			return toast.success(actualMessage);
		case 'error':
			return toast.error(actualMessage);
		case 'warning':
			return toast.warning(actualMessage);
		case 'info':
			return toast.info(actualMessage);
	}
};

export const removeToast = (id: string) => toast.remove(id);
export const toasts = toast;
