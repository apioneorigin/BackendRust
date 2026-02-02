/**
 * Store exports
 */

export { auth, user, isAuthenticated } from './auth';
export { theme } from './theme';
export { toast, toasts, addToast, removeToast } from './toast';
export { chat, messages, currentConversation, conversations, isStreaming, streamingContent, questions } from './chat';
export { session, currentSession, sessions } from './session';
export { credits, creditBalance, isLowCredits } from './credits';
export { documents, currentDocument, documentList } from './documents';
export { goals, currentGoal, activeGoals, completedGoals } from './goals';
export {
	matrix,
	matrixData,
	rowHeaders,
	columnHeaders,
	isMatrixGenerated,
	showRiskHeatmap,
	documentTabs,
	activeTab,
	isLoadingOptions,
	coherence,
	population,
	avgScore,
	powerSpots
} from './matrix';

// Re-export types
export type { User } from './auth';
export type { Toast, ToastType } from './toast';
export type { Message, Conversation } from './chat';
export type { Session } from './session';
export type { CreditBalance, Redemption, UsageRecord } from './credits';
export type { Document } from './documents';
export type { Goal, MatrixValue } from './goals';
export type { CellData, DimensionOption, DocumentTab } from './matrix';
