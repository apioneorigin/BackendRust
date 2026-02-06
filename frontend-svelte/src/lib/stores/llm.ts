/**
 * LLM busy state — true when any LLM call is in flight.
 *
 * Used by app layout to block navigation and show not-allowed cursor.
 */

import { derived, writable } from 'svelte/store';
import { chat } from './chat';
import { matrix } from './matrix';

/** Writable flag for non-chat LLM calls (goal discovery, etc.) */
export const llmManualBusy = writable(false);

/** Derived: true when any LLM call is active (chat streaming, matrix processing, or manual) */
export const llmBusy = derived(
	[chat, matrix, llmManualBusy],
	([$chat, $matrix, $manual]) => $chat.isStreaming || $matrix.isProcessing || $manual
);
