/**
 * Matrix store - manages multi-document transformation matrix state
 *
 * NEW ARCHITECTURE:
 * - Each document has its own 10x10 matrix (rows, columns, cells)
 * - Documents are displayed as tabs in Control Popup and Matrix Panel
 * - User can select 5 rows + 5 columns per document for display
 * - "+" button in Control Popup generates 3 more documents via gpt-5.2
 */

import { writable, derived, get } from 'svelte/store';
import { api } from '$utils/api';

export interface CellDimension {
	name: string;
	value: number;  // 0 (Low), 50 (Medium), or 100 (High)
}

export interface CellData {
	value: number;
	dimensions: CellDimension[];
	confidence: number;
	description: string;
	isLeveragePoint: boolean;
	riskLevel?: 'low' | 'medium' | 'high';
}

// Articulated Insight structure based on insight-articulation-final.pdf
// 3-component structure: THE TRUTH → YOUR TRUTH → THE MARK (160-250 words total)
export interface ArticulatedInsight {
	// Insight title (max 10 words) - displayed in popup header
	title: string;               // Max 10-word title phrase for this insight

	// THE TRUTH (80-120 words): Analogy from outside user's domain
	the_truth: string;           // Italicized analogy, present tense, sensory
	the_truth_law: string;       // Bold one-line universal law (15-25 words)

	// YOUR TRUTH (50-80 words): Recognition + future protection
	your_truth: string;          // "I see you" + "never miss again" trigger
	your_truth_revelation: string;  // Bold revelation - what's now visible

	// THE MARK (30-50 words): Install the insight as permanent pattern
	the_mark_name: string;       // Memorable name, 2-5 words (e.g., "The Permission Gap")
	the_mark_prediction: string; // Where they'll see this pattern
	the_mark_identity: string;   // Bold new capability/identity
}

export interface RowOption {
	id: string;
	label: string;
	insight: string;  // Short summary (backward compatible)
	articulated_insight?: ArticulatedInsight;  // Full 3-component insight (when document is fully populated)
}

export interface ColumnOption {
	id: string;
	label: string;
	insight: string;  // Short summary (backward compatible)
	articulated_insight?: ArticulatedInsight;  // Full 3-component insight (when document is fully populated)
}

// New: Document with its own matrix data
export interface Document {
	id: string;
	name: string;
	description: string;  // ~20 word description
	matrix_data: {
		row_options: RowOption[];
		column_options: ColumnOption[];
		selected_rows: number[];
		selected_columns: number[];
		cells: Record<string, {
			impact_score: number;
			relationship?: string;
			dimensions: {
				name: string;
				value: number;  // 0 (Low), 50 (Medium), or 100 (High)
			}[];
		}>;
	};
}

interface MatrixState {
	// All documents (each with its own matrix)
	documents: Document[];
	activeDocumentId: string | null;

	// Displayed 5x5 matrix (derived from active document's selections)
	displayedMatrixData: CellData[][];
	displayedRowHeaders: string[];
	displayedColumnHeaders: string[];
	displayedRowInsights: string[];
	displayedColumnInsights: string[];

	// Generation state
	isGenerated: boolean;
	isGenerating: boolean;
	isGeneratingMoreDocuments: boolean;

	// Risk heatmap state
	showRiskHeatmap: boolean;

	// Loading states
	isLoadingOptions: boolean;
	error: string | null;

	// Conversation ID for API calls
	conversationId: string | null;
}

const initialState: MatrixState = {
	documents: [],
	activeDocumentId: null,

	displayedMatrixData: [],
	displayedRowHeaders: ['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'],
	displayedColumnHeaders: ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5'],
	displayedRowInsights: ['', '', '', '', ''],
	displayedColumnInsights: ['', '', '', '', ''],

	isGenerated: false,
	isGenerating: false,
	isGeneratingMoreDocuments: false,

	showRiskHeatmap: false,
	isLoadingOptions: false,
	error: null,
	conversationId: null
};

function createMatrixStore() {
	const { subscribe, set, update } = writable<MatrixState>(initialState);

	// Helper to build displayed 5x5 from a document's selected rows/columns
	function buildDisplayedMatrix(doc: Document): {
		matrixData: CellData[][];
		rowHeaders: string[];
		columnHeaders: string[];
		rowInsights: string[];
		columnInsights: string[];
	} {
		const placeholderDimensions: CellDimension[] = Array.from({ length: 5 }, (_, i) => ({
			name: `Dimension ${i + 1}`,
			value: 50  // Medium
		}));

		const { row_options, column_options, selected_rows, selected_columns, cells } = doc.matrix_data;

		const rowHeaders = selected_rows.map(i => row_options[i]?.label || `Row ${i + 1}`);
		const columnHeaders = selected_columns.map(i => column_options[i]?.label || `Column ${i + 1}`);
		const rowInsights = selected_rows.map(i => row_options[i]?.insight || '');
		const columnInsights = selected_columns.map(i => column_options[i]?.insight || '');

		const matrixData: CellData[][] = selected_rows.map(rowIdx =>
			selected_columns.map(colIdx => {
				const cellKey = `${rowIdx}-${colIdx}`;
				const cell = cells[cellKey];

				if (!cell) {
					return {
						value: 50,
						dimensions: placeholderDimensions.map(d => ({ ...d })),
						confidence: 0.5,
						description: '',
						isLeveragePoint: false,
						riskLevel: 'low' as const
					};
				}

				let riskLevel: 'low' | 'medium' | 'high' = 'low';
				if (cell.impact_score >= 70) riskLevel = 'high';
				else if (cell.impact_score >= 40) riskLevel = 'medium';

				const isLeveragePoint = cell.impact_score >= 75 &&
					cell.dimensions?.some(d => d.value >= 75);

				const dimensions: CellDimension[] = cell.dimensions?.map(d => ({
					name: d.name,
					value: d.value
				})) || placeholderDimensions;

				return {
					value: cell.impact_score,
					dimensions: dimensions.length === 5 ? dimensions : placeholderDimensions,
					confidence: cell.impact_score / 100,
					description: cell.relationship || '',
					isLeveragePoint,
					riskLevel
				};
			})
		);

		return { matrixData, rowHeaders, columnHeaders, rowInsights, columnInsights };
	}

	return {
		subscribe,

		// Set conversation ID for API calls
		setConversationId(conversationId: string) {
			update(state => ({ ...state, conversationId }));
		},

		// Populate from structured data received from backend (documents array format)
		populateFromStructuredData(data: { documents?: Document[] }) {
			if (!data || !data.documents || data.documents.length === 0) return;

			const documents = data.documents;

			const activeDocumentId = documents[0].id;
			const activeDoc = documents[0];
			const displayed = buildDisplayedMatrix(activeDoc);

			update(state => ({
				...state,
				documents,
				activeDocumentId,
				displayedMatrixData: displayed.matrixData,
				displayedRowHeaders: displayed.rowHeaders,
				displayedColumnHeaders: displayed.columnHeaders,
				displayedRowInsights: displayed.rowInsights,
				displayedColumnInsights: displayed.columnInsights,
				isGenerated: true,
				isGenerating: false
			}));
		},

		// Switch active document tab
		setActiveDocument(documentId: string) {
			update(state => {
				const doc = state.documents.find(d => d.id === documentId);
				if (!doc) return state;

				const displayed = buildDisplayedMatrix(doc);

				return {
					...state,
					activeDocumentId: documentId,
					displayedMatrixData: displayed.matrixData,
					displayedRowHeaders: displayed.rowHeaders,
					displayedColumnHeaders: displayed.columnHeaders,
					displayedRowInsights: displayed.rowInsights,
					displayedColumnInsights: displayed.columnInsights
				};
			});
		},

		// Update row/column selection for active document
		async updateDocumentSelection(selectedRows: number[], selectedColumns: number[]) {
			const state = get({ subscribe });
			const activeDoc = state.documents.find(d => d.id === state.activeDocumentId);
			if (!activeDoc || !state.conversationId) return;

			// Update local state immediately
			update(s => {
				const docIndex = s.documents.findIndex(d => d.id === s.activeDocumentId);
				if (docIndex === -1) return s;

				const updatedDocs = [...s.documents];
				updatedDocs[docIndex] = {
					...updatedDocs[docIndex],
					matrix_data: {
						...updatedDocs[docIndex].matrix_data,
						selected_rows: selectedRows,
						selected_columns: selectedColumns
					}
				};

				const displayed = buildDisplayedMatrix(updatedDocs[docIndex]);

				return {
					...s,
					documents: updatedDocs,
					displayedMatrixData: displayed.matrixData,
					displayedRowHeaders: displayed.rowHeaders,
					displayedColumnHeaders: displayed.columnHeaders,
					displayedRowInsights: displayed.rowInsights,
					displayedColumnInsights: displayed.columnInsights
				};
			});

			// Persist to backend
			try {
				await api.patch(`/matrix/${state.conversationId}/document/${state.activeDocumentId}/selection`, {
					document_id: state.activeDocumentId,
					selected_rows: selectedRows,
					selected_columns: selectedColumns
				});
			} catch (error) {
				console.error('Failed to persist document selection:', error);
			}
		},

		// Generate 3 more documents via gpt-5.2 (called when user clicks "+" in Control Popup)
		async generateMoreDocuments() {
			const state = get({ subscribe });
			if (!state.conversationId) {
				console.error('No conversation ID set');
				return;
			}

			update(s => ({ ...s, isGeneratingMoreDocuments: true, error: null }));

			try {
				const response = await api.post(`/matrix/${state.conversationId}/documents/generate`);
				const { documents: newDocs, total_document_count } = response;

				update(s => ({
					...s,
					documents: [...s.documents, ...newDocs],
					isGeneratingMoreDocuments: false
				}));

				return newDocs;
			} catch (error: any) {
				update(s => ({
					...s,
					isGeneratingMoreDocuments: false,
					error: error.message || 'Failed to generate more documents'
				}));
				throw error;
			}
		},

		// Update cell dimension value
		updateCellDimension(rowIdx: number, colIdx: number, dimIdx: number, value: number) {
			update(state => {
				const newMatrixData = state.displayedMatrixData.map((row, r) =>
					row.map((cell, c) => {
						if (r === rowIdx && c === colIdx) {
							const newDimensions = cell.dimensions.map((dim, d) =>
								d === dimIdx ? { ...dim, value } : dim
							);
							return { ...cell, dimensions: newDimensions };
						}
						return cell;
					})
				);
				return { ...state, displayedMatrixData: newMatrixData };
			});
		},

		// Toggle risk heatmap
		toggleRiskHeatmap() {
			update(state => ({ ...state, showRiskHeatmap: !state.showRiskHeatmap }));
		},

		// Initialize matrix with placeholder data (before LLM generates real data)
		initializeMatrix() {
			const placeholderDimensions: CellDimension[] = Array.from({ length: 5 }, (_, i) => ({
				name: `Dimension ${i + 1}`,
				value: 50
			}));

			const placeholderCell: CellData = {
				value: 50,
				dimensions: placeholderDimensions,
				confidence: 0.5,
				description: '',
				isLeveragePoint: false,
				riskLevel: 'low'
			};

			const displayedMatrixData: CellData[][] = Array.from({ length: 5 }, () =>
				Array.from({ length: 5 }, () => ({ ...placeholderCell, dimensions: placeholderDimensions.map(d => ({ ...d })) }))
			);

			update(state => ({
				...state,
				displayedMatrixData,
				displayedRowHeaders: ['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'],
				displayedColumnHeaders: ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5'],
				displayedRowInsights: ['', '', '', '', ''],
				displayedColumnInsights: ['', '', '', '', ''],
				isGenerated: false
			}));
		},

		// Reset matrix
		reset() {
			set(initialState);
		}
	};
}

export const matrix = createMatrixStore();

// Derived stores
export const documents = derived(matrix, ($matrix) => $matrix.documents);
export const activeDocumentId = derived(matrix, ($matrix) => $matrix.activeDocumentId);
export const activeDocument = derived(matrix, ($matrix) =>
	$matrix.documents.find(d => d.id === $matrix.activeDocumentId) || null
);

export const matrixData = derived(matrix, ($matrix) => $matrix.displayedMatrixData);
export const rowHeaders = derived(matrix, ($matrix) => $matrix.displayedRowHeaders);
export const columnHeaders = derived(matrix, ($matrix) => $matrix.displayedColumnHeaders);
export const rowInsights = derived(matrix, ($matrix) => $matrix.displayedRowInsights);
export const columnInsights = derived(matrix, ($matrix) => $matrix.displayedColumnInsights);

export const isMatrixGenerated = derived(matrix, ($matrix) => $matrix.isGenerated);
export const isGeneratingMoreDocuments = derived(matrix, ($matrix) => $matrix.isGeneratingMoreDocuments);
export const showRiskHeatmap = derived(matrix, ($matrix) => $matrix.showRiskHeatmap);
export const isLoadingOptions = derived(matrix, ($matrix) => $matrix.isLoadingOptions);

// Computed metrics (from currently displayed matrix)
export const coherence = derived(matrix, ($matrix) => {
	if ($matrix.displayedMatrixData.length === 0) return 0;
	const cells = $matrix.displayedMatrixData.flat();
	return Math.round(cells.reduce((sum, cell) => sum + cell.confidence, 0) / cells.length * 100);
});

export const population = derived(matrix, ($matrix) => {
	if ($matrix.displayedMatrixData.length === 0) return 0;
	const cells = $matrix.displayedMatrixData.flat();
	return Math.round(cells.filter((c) => c.value > 0).length / cells.length * 100);
});

export const avgScore = derived(matrix, ($matrix) => {
	if ($matrix.displayedMatrixData.length === 0) return 0;
	const cells = $matrix.displayedMatrixData.flat();
	return Math.round(cells.reduce((sum, cell) => sum + cell.value, 0) / cells.length);
});

export const powerSpots = derived(matrix, ($matrix) => {
	if ($matrix.displayedMatrixData.length === 0) return 0;
	return $matrix.displayedMatrixData.flat().filter((c) => c.isLeveragePoint).length;
});

// Document tabs interface - used by CausationPopup and EffectPopup components
export const documentTabs = derived(matrix, ($matrix) =>
	$matrix.documents.map(d => ({
		id: d.id,
		name: d.name,
		type: 'primary' as const,
		causationOptions: [],
		effectOptions: [],
		selectedCausations: [],
		selectedEffects: []
	}))
);

export const activeTab = derived(matrix, ($matrix) => {
	const doc = $matrix.documents.find(d => d.id === $matrix.activeDocumentId);
	return doc ? {
		id: doc.id,
		name: doc.name,
		type: 'primary' as const,
		causationOptions: [],
		effectOptions: [],
		selectedCausations: [],
		selectedEffects: []
	} : null;
});
