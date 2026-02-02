/**
 * Matrix store - manages transformation matrix state
 *
 * Handles:
 * - Matrix data (5x5 cells)
 * - Row headers (causation dimensions)
 * - Column headers (effect dimensions)
 * - Available dimension options (up to 10 each for rows/columns)
 * - Document tabs for Causation/Effect popups
 */

import { writable, derived, get } from 'svelte/store';
import { api } from '$utils/api';

export interface CellDimension {
	name: string;
	value: number;
	stepLabels: string[];
}

export interface CellData {
	value: number;
	dimensions: CellDimension[];
	confidence: number;
	description: string;
	isLeveragePoint: boolean;
	riskLevel?: 'low' | 'medium' | 'high';
}

export interface DimensionOption {
	id: string;
	label: string;
	description?: string;
	isSelected: boolean;
}

export interface DocumentTab {
	id: string;
	name: string;
	type: 'primary' | 'secondary' | 'custom';
	causationOptions: DimensionOption[];
	effectOptions: DimensionOption[];
	selectedCausations: string[];
	selectedEffects: string[];
}

interface MatrixState {
	// Matrix data
	matrixData: CellData[][];
	rowHeaders: string[];
	columnHeaders: string[];

	// Context insights - explains why each row/column was generated
	rowInsights: string[];
	columnInsights: string[];

	// Generation state
	isGenerated: boolean;
	isGenerating: boolean;

	// Document tabs for Causation/Effect selection
	documentTabs: DocumentTab[];
	activeTabId: string | null;

	// Risk heatmap state
	showRiskHeatmap: boolean;

	// Loading states
	isLoadingOptions: boolean;
	error: string | null;
}

const DEFAULT_DOCUMENTS: DocumentTab[] = [
	{
		id: 'doc-1',
		name: 'Strategy Document',
		type: 'primary',
		causationOptions: [],
		effectOptions: [],
		selectedCausations: [],
		selectedEffects: []
	},
	{
		id: 'doc-2',
		name: 'Analysis Report',
		type: 'secondary',
		causationOptions: [],
		effectOptions: [],
		selectedCausations: [],
		selectedEffects: []
	},
	{
		id: 'doc-3',
		name: 'Implementation Plan',
		type: 'secondary',
		causationOptions: [],
		effectOptions: [],
		selectedCausations: [],
		selectedEffects: []
	}
];

const initialState: MatrixState = {
	matrixData: [],
	rowHeaders: ['Context 1', 'Context 2', 'Context 3', 'Context 4', 'Context 5'],
	columnHeaders: ['Context 6', 'Context 7', 'Context 8', 'Context 9', 'Context 10'],
	rowInsights: ['', '', '', '', ''],
	columnInsights: ['', '', '', '', ''],
	isGenerated: false,
	isGenerating: false,
	documentTabs: DEFAULT_DOCUMENTS,
	activeTabId: 'doc-1',
	showRiskHeatmap: false,
	isLoadingOptions: false,
	error: null
};

function generateCellId(): string {
	return Math.random().toString(36).substring(2, 9);
}

function createMatrixStore() {
	const { subscribe, set, update } = writable<MatrixState>(initialState);

	return {
		subscribe,

		// Initialize matrix with placeholder data (awaiting LLM response)
		initializeMatrix() {
			const leveragePoints = [
				{ row: 1, col: 2 },
				{ row: 2, col: 3 },
				{ row: 3, col: 1 }
			];

			// Placeholder dimensions - will be replaced by LLM-generated contextual data
			const matrixData: CellData[][] = Array.from({ length: 5 }, (_, rowIdx) =>
				Array.from({ length: 5 }, (_, colIdx) => ({
					value: Math.floor(Math.random() * 50) + 25,
					dimensions: Array.from({ length: 5 }, (_, dimIdx) => ({
						name: `Dimension ${dimIdx + 1}`,
						value: [0, 25, 50, 75, 100][Math.floor(Math.random() * 5)],
						stepLabels: ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5']
					})),
					confidence: Math.random() * 0.5 + 0.5,
					description: `Cell R${rowIdx}C${colIdx}`,
					isLeveragePoint: leveragePoints.some(
						(lp) => lp.row === rowIdx && lp.col === colIdx
					),
					riskLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as
						| 'low'
						| 'medium'
						| 'high'
				}))
			);

			// Generate initial causation/effect options for each document tab
			const documentTabs = DEFAULT_DOCUMENTS.map((tab) => ({
				...tab,
				causationOptions: generateInitialCausationOptions(),
				effectOptions: generateInitialEffectOptions(),
				selectedCausations: ['c1', 'c2', 'c3', 'c4', 'c5'],
				selectedEffects: ['e1', 'e2', 'e3', 'e4', 'e5']
			}));

			update((state) => ({
				...state,
				matrixData,
				isGenerated: true,
				documentTabs
			}));
		},

		// Update cell value
		updateCellValue(row: number, col: number, value: number) {
			update((state) => {
				const newMatrixData = [...state.matrixData];
				if (newMatrixData[row] && newMatrixData[row][col]) {
					newMatrixData[row][col] = {
						...newMatrixData[row][col],
						value: Math.max(0, Math.min(100, value))
					};
				}
				return { ...state, matrixData: newMatrixData };
			});
		},

		// Update row headers (causation dimensions)
		updateRowHeaders(headers: string[]) {
			update((state) => ({
				...state,
				rowHeaders: headers.slice(0, 5)
			}));
		},

		// Update column headers (effect dimensions)
		updateColumnHeaders(headers: string[]) {
			update((state) => ({
				...state,
				columnHeaders: headers.slice(0, 5)
			}));
		},

		// Toggle risk heatmap
		toggleRiskHeatmap(enabled?: boolean) {
			update((state) => ({
				...state,
				showRiskHeatmap: enabled !== undefined ? enabled : !state.showRiskHeatmap
			}));
		},

		// Set active document tab
		setActiveTab(tabId: string) {
			update((state) => ({
				...state,
				activeTabId: tabId
			}));
		},

		// Add new document tab
		addDocumentTab(name: string) {
			const newTab: DocumentTab = {
				id: `doc-${Date.now()}`,
				name,
				type: 'custom',
				causationOptions: generateInitialCausationOptions(),
				effectOptions: generateInitialEffectOptions(),
				selectedCausations: ['c1', 'c2', 'c3', 'c4', 'c5'],
				selectedEffects: ['e1', 'e2', 'e3', 'e4', 'e5']
			};

			update((state) => ({
				...state,
				documentTabs: [...state.documentTabs, newTab],
				activeTabId: newTab.id
			}));
		},

		// Remove document tab
		removeDocumentTab(tabId: string) {
			update((state) => {
				const tabs = state.documentTabs.filter((t) => t.id !== tabId);
				return {
					...state,
					documentTabs: tabs,
					activeTabId: tabs.length > 0 ? tabs[0].id : null
				};
			});
		},

		// Toggle causation option selection for a tab
		toggleCausationSelection(tabId: string, optionId: string) {
			update((state) => {
				const tabs = state.documentTabs.map((tab) => {
					if (tab.id !== tabId) return tab;

					const isSelected = tab.selectedCausations.includes(optionId);
					let newSelected: string[];

					if (isSelected) {
						// Only allow deselection if more than 5 are selected
						if (tab.selectedCausations.length > 5) {
							newSelected = tab.selectedCausations.filter((id) => id !== optionId);
						} else {
							newSelected = tab.selectedCausations;
						}
					} else {
						// Only allow selection if less than 5 are selected
						if (tab.selectedCausations.length < 5) {
							newSelected = [...tab.selectedCausations, optionId];
						} else {
							newSelected = tab.selectedCausations;
						}
					}

					return {
						...tab,
						selectedCausations: newSelected,
						causationOptions: tab.causationOptions.map((opt) => ({
							...opt,
							isSelected: newSelected.includes(opt.id)
						}))
					};
				});

				return { ...state, documentTabs: tabs };
			});
		},

		// Toggle effect option selection for a tab
		toggleEffectSelection(tabId: string, optionId: string) {
			update((state) => {
				const tabs = state.documentTabs.map((tab) => {
					if (tab.id !== tabId) return tab;

					const isSelected = tab.selectedEffects.includes(optionId);
					let newSelected: string[];

					if (isSelected) {
						if (tab.selectedEffects.length > 5) {
							newSelected = tab.selectedEffects.filter((id) => id !== optionId);
						} else {
							newSelected = tab.selectedEffects;
						}
					} else {
						if (tab.selectedEffects.length < 5) {
							newSelected = [...tab.selectedEffects, optionId];
						} else {
							newSelected = tab.selectedEffects;
						}
					}

					return {
						...tab,
						selectedEffects: newSelected,
						effectOptions: tab.effectOptions.map((opt) => ({
							...opt,
							isSelected: newSelected.includes(opt.id)
						}))
					};
				});

				return { ...state, documentTabs: tabs };
			});
		},

		// Generate more causation options (LLM call)
		async generateMoreCausationOptions(tabId: string) {
			update((state) => ({ ...state, isLoadingOptions: true }));

			try {
				// In a real implementation, this would call an LLM API
				// For now, simulate with generated options
				await new Promise((resolve) => setTimeout(resolve, 1000));

				const newOptions = generateAdditionalCausationOptions();

				update((state) => {
					const tabs = state.documentTabs.map((tab) => {
						if (tab.id !== tabId) return tab;

						// Max 10 options total, only add up to 5 new ones
						const currentCount = tab.causationOptions.length;
						const slotsAvailable = 10 - currentCount;
						const optionsToAdd = newOptions.slice(0, Math.min(5, slotsAvailable));

						return {
							...tab,
							causationOptions: [...tab.causationOptions, ...optionsToAdd]
						};
					});

					return { ...state, documentTabs: tabs, isLoadingOptions: false };
				});
			} catch (error: any) {
				update((state) => ({
					...state,
					isLoadingOptions: false,
					error: error.message
				}));
			}
		},

		// Generate more effect options (LLM call)
		async generateMoreEffectOptions(tabId: string) {
			update((state) => ({ ...state, isLoadingOptions: true }));

			try {
				await new Promise((resolve) => setTimeout(resolve, 1000));

				const newOptions = generateAdditionalEffectOptions();

				update((state) => {
					const tabs = state.documentTabs.map((tab) => {
						if (tab.id !== tabId) return tab;

						const currentCount = tab.effectOptions.length;
						const slotsAvailable = 10 - currentCount;
						const optionsToAdd = newOptions.slice(0, Math.min(5, slotsAvailable));

						return {
							...tab,
							effectOptions: [...tab.effectOptions, ...optionsToAdd]
						};
					});

					return { ...state, documentTabs: tabs, isLoadingOptions: false };
				});
			} catch (error: any) {
				update((state) => ({
					...state,
					isLoadingOptions: false,
					error: error.message
				}));
			}
		},

		// Submit causation selection for a tab
		submitCausationSelection(tabId: string) {
			const state = get({ subscribe });
			const tab = state.documentTabs.find((t) => t.id === tabId);

			if (tab && tab.selectedCausations.length === 5) {
				const selectedOptions = tab.causationOptions.filter((opt) =>
					tab.selectedCausations.includes(opt.id)
				);
				const newHeaders = selectedOptions.map((opt) => opt.label);

				update((s) => ({
					...s,
					rowHeaders: newHeaders
				}));

				return true;
			}
			return false;
		},

		// Submit effect selection for a tab
		submitEffectSelection(tabId: string) {
			const state = get({ subscribe });
			const tab = state.documentTabs.find((t) => t.id === tabId);

			if (tab && tab.selectedEffects.length === 5) {
				const selectedOptions = tab.effectOptions.filter((opt) =>
					tab.selectedEffects.includes(opt.id)
				);
				const newHeaders = selectedOptions.map((opt) => opt.label);

				update((s) => ({
					...s,
					columnHeaders: newHeaders
				}));

				return true;
			}
			return false;
		},

		// Populate matrix from structured data received from backend
		populateFromStructuredData(matrixData: {
			row_options: { id: string; label: string; description?: string; insight?: string }[];
			column_options: { id: string; label: string; description?: string; insight?: string }[];
			cells: Record<string, {
				impact_score: number;
				relationship?: string;
				dimensions: {
					name: string;
					value: number;
					step_labels: string[];
				}[];
			}>;
		}) {
			if (!matrixData) return;

			const rowCount = Math.min(matrixData.row_options.length, 5);
			const colCount = Math.min(matrixData.column_options.length, 5);

			// Extract row and column headers with insights
			const rowHeaders = matrixData.row_options.slice(0, 5).map(opt => opt.label);
			const columnHeaders = matrixData.column_options.slice(0, 5).map(opt => opt.label);
			const rowInsights = matrixData.row_options.slice(0, 5).map(opt => opt.insight || opt.description || '');
			const columnInsights = matrixData.column_options.slice(0, 5).map(opt => opt.insight || opt.description || '');

			// Placeholder dimensions - only used if LLM data is missing (should not happen)
			const placeholderDimensions: CellDimension[] = Array.from({ length: 5 }, (_, i) => ({
				name: `Dimension ${i + 1}`,
				value: 50,
				stepLabels: ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5']
			}));

			// Build the matrix data from cells
			const cellData: CellData[][] = Array.from({ length: rowCount }, (_, rowIdx) =>
				Array.from({ length: colCount }, (_, colIdx) => {
					const cellKey = `${rowIdx}-${colIdx}`;
					const cell = matrixData.cells[cellKey];

					if (cell) {
						// Determine risk level based on impact score
						let riskLevel: 'low' | 'medium' | 'high' = 'low';
						if (cell.impact_score >= 70) riskLevel = 'high';
						else if (cell.impact_score >= 40) riskLevel = 'medium';

						// Check if this is a leverage point (high impact with certain characteristics)
						const isLeveragePoint = cell.impact_score >= 75 &&
							cell.dimensions.some(d => d.value >= 75);

						// Convert backend dimension format to frontend format
						// LLM must provide contextual names and step labels - no fallbacks
						const dimensions: CellDimension[] = cell.dimensions.map(d => ({
							name: d.name,
							value: d.value,
							stepLabels: d.step_labels
						}));

						return {
							value: cell.impact_score,
							dimensions: dimensions.length === 5 ? dimensions : placeholderDimensions,
							confidence: cell.impact_score / 100,
							description: cell.relationship || `Cell R${rowIdx}C${colIdx}`,
							isLeveragePoint,
							riskLevel
						};
					}

					// Default cell if not found in structured data
					return {
						value: 50,
						dimensions: placeholderDimensions.map(d => ({ ...d })),
						confidence: 0.5,
						description: `Cell R${rowIdx}C${colIdx}`,
						isLeveragePoint: false,
						riskLevel: 'low' as const
					};
				})
			);

			update((state) => ({
				...state,
				matrixData: cellData,
				rowHeaders,
				columnHeaders,
				rowInsights,
				columnInsights,
				isGenerated: true,
				isGenerating: false
			}));
		},

		// Reset matrix
		reset() {
			set(initialState);
		},

		// Generate more context titles (for unified Context Control popup)
		async generateMoreContextTitles(type: 'row' | 'column') {
			update((state) => ({ ...state, isLoadingOptions: true }));

			try {
				// TODO: Call backend API to generate more context titles
				// For now, generate placeholder titles
				const newTitles = type === 'row'
					? ['New Context A', 'New Context B', 'New Context C', 'New Context D', 'New Context E']
					: ['New Context F', 'New Context G', 'New Context H', 'New Context I', 'New Context J'];

				const newInsights = [
					'Generated based on matrix analysis',
					'Derived from pattern recognition',
					'Identified through correlation',
					'Suggested by leverage analysis',
					'Recommended for completeness'
				];

				update((state) => {
					if (type === 'row') {
						return {
							...state,
							rowHeaders: [...state.rowHeaders, ...newTitles.slice(0, 5 - state.rowHeaders.length % 5)],
							rowInsights: [...state.rowInsights, ...newInsights.slice(0, 5 - state.rowInsights.length % 5)],
							isLoadingOptions: false
						};
					} else {
						return {
							...state,
							columnHeaders: [...state.columnHeaders, ...newTitles.slice(0, 5 - state.columnHeaders.length % 5)],
							columnInsights: [...state.columnInsights, ...newInsights.slice(0, 5 - state.columnInsights.length % 5)],
							isLoadingOptions: false
						};
					}
				});
			} catch (error) {
				update((state) => ({
					...state,
					isLoadingOptions: false,
					error: 'Failed to generate more context titles'
				}));
			}
		},

		// Update context selection (from unified Context Control popup)
		updateContextSelection(selectedRows: string[], selectedCols: string[]) {
			update((state) => ({
				...state,
				rowHeaders: selectedRows.slice(0, 5),
				columnHeaders: selectedCols.slice(0, 5)
			}));
		}
	};
}

// Helper functions to generate dimension options
function generateInitialCausationOptions(): DimensionOption[] {
	return [
		{ id: 'c1', label: 'Strategic Vision', description: 'Long-term direction and goals', isSelected: true },
		{ id: 'c2', label: 'Resource Allocation', description: 'Distribution of assets and capital', isSelected: true },
		{ id: 'c3', label: 'Team Capability', description: 'Skills and expertise available', isSelected: true },
		{ id: 'c4', label: 'Market Position', description: 'Competitive standing and reach', isSelected: true },
		{ id: 'c5', label: 'Technology Stack', description: 'Technical infrastructure and tools', isSelected: true }
	];
}

function generateInitialEffectOptions(): DimensionOption[] {
	return [
		{ id: 'e1', label: 'Revenue Growth', description: 'Income increase potential', isSelected: true },
		{ id: 'e2', label: 'Cost Efficiency', description: 'Expense optimization', isSelected: true },
		{ id: 'e3', label: 'Customer Satisfaction', description: 'Client happiness metrics', isSelected: true },
		{ id: 'e4', label: 'Innovation Rate', description: 'New product/feature velocity', isSelected: true },
		{ id: 'e5', label: 'Risk Mitigation', description: 'Threat reduction capability', isSelected: true }
	];
}

function generateAdditionalCausationOptions(): DimensionOption[] {
	const options = [
		{ id: `c${Date.now()}1`, label: 'Leadership Quality', description: 'Management effectiveness', isSelected: false },
		{ id: `c${Date.now()}2`, label: 'Process Maturity', description: 'Operational refinement level', isSelected: false },
		{ id: `c${Date.now()}3`, label: 'Data Infrastructure', description: 'Information systems quality', isSelected: false },
		{ id: `c${Date.now()}4`, label: 'Partner Network', description: 'External collaboration strength', isSelected: false },
		{ id: `c${Date.now()}5`, label: 'Culture Alignment', description: 'Values and behavior consistency', isSelected: false }
	];
	return options;
}

function generateAdditionalEffectOptions(): DimensionOption[] {
	const options = [
		{ id: `e${Date.now()}1`, label: 'Market Share', description: 'Segment dominance', isSelected: false },
		{ id: `e${Date.now()}2`, label: 'Employee Retention', description: 'Talent stability', isSelected: false },
		{ id: `e${Date.now()}3`, label: 'Brand Value', description: 'Market perception strength', isSelected: false },
		{ id: `e${Date.now()}4`, label: 'Operational Speed', description: 'Execution velocity', isSelected: false },
		{ id: `e${Date.now()}5`, label: 'Compliance Level', description: 'Regulatory adherence', isSelected: false }
	];
	return options;
}

export const matrix = createMatrixStore();

// Derived stores
export const matrixData = derived(matrix, ($matrix) => $matrix.matrixData);
export const rowHeaders = derived(matrix, ($matrix) => $matrix.rowHeaders);
export const columnHeaders = derived(matrix, ($matrix) => $matrix.columnHeaders);
export const isMatrixGenerated = derived(matrix, ($matrix) => $matrix.isGenerated);
export const showRiskHeatmap = derived(matrix, ($matrix) => $matrix.showRiskHeatmap);
export const documentTabs = derived(matrix, ($matrix) => $matrix.documentTabs);
export const activeTab = derived(matrix, ($matrix) =>
	$matrix.documentTabs.find((t) => t.id === $matrix.activeTabId) || null
);
export const isLoadingOptions = derived(matrix, ($matrix) => $matrix.isLoadingOptions);

// Computed metrics
export const coherence = derived(matrix, ($matrix) => {
	if ($matrix.matrixData.length === 0) return 0;
	const cells = $matrix.matrixData.flat();
	return Math.round(cells.reduce((sum, cell) => sum + cell.confidence, 0) / cells.length * 100);
});

export const population = derived(matrix, ($matrix) => {
	if ($matrix.matrixData.length === 0) return 0;
	const cells = $matrix.matrixData.flat();
	return Math.round(cells.filter((c) => c.value > 0).length / cells.length * 100);
});

export const avgScore = derived(matrix, ($matrix) => {
	if ($matrix.matrixData.length === 0) return 0;
	const cells = $matrix.matrixData.flat();
	return Math.round(cells.reduce((sum, cell) => sum + cell.value, 0) / cells.length);
});

export const powerSpots = derived(matrix, ($matrix) => {
	if ($matrix.matrixData.length === 0) return 0;
	return $matrix.matrixData.flat().filter((c) => c.isLeveragePoint).length;
});
