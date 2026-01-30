<script lang="ts">
	import { onMount } from 'svelte';
	import { Button, Spinner } from '$lib/components/ui';
	import { addToast } from '$lib/stores';

	// Matrix state
	let isLoading = true;
	let matrixData: CellData[][] = [];
	let rowHeaders = ['Dimension 1', 'Dimension 2', 'Dimension 3', 'Dimension 4', 'Dimension 5'];
	let columnHeaders = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5'];

	// UI state
	let selectedCell: { row: number; col: number } | null = null;
	let showRiskHeatmap = false;
	let showCellPopup = false;
	let activeTab: 'overview' | 'leverage' | 'templates' = 'overview';

	interface CellData {
		value: number;
		dimensions: number[];
		confidence: number;
		description: string;
		isLeveragePoint: boolean;
		riskLevel?: 'low' | 'medium' | 'high';
	}

	// Sample leverage points
	const leveragePoints = [
		{
			id: 'lp1',
			cell: { row: 1, col: 2 },
			title: 'Critical Foundation',
			description: 'Strengthening this area creates cascading positive effects',
			impact: 85
		},
		{
			id: 'lp2',
			cell: { row: 2, col: 3 },
			title: 'Growth Catalyst',
			description: 'Key enabler for sustainable transformation',
			impact: 72
		},
		{
			id: 'lp3',
			cell: { row: 3, col: 1 },
			title: 'Balance Point',
			description: 'Harmonizes multiple dimensions effectively',
			impact: 68
		}
	];

	// Sample templates
	const templates = [
		{
			id: 't1',
			name: 'Rapid Progress',
			description: 'Focused approach for quick wins',
			risk: 'medium' as const,
			timeline: '2-4 weeks'
		},
		{
			id: 't2',
			name: 'Balanced Growth',
			description: 'Steady improvement across all areas',
			risk: 'low' as const,
			timeline: '4-8 weeks'
		},
		{
			id: 't3',
			name: 'Deep Transformation',
			description: 'Comprehensive change strategy',
			risk: 'high' as const,
			timeline: '8-12 weeks'
		}
	];

	onMount(() => {
		// Initialize matrix with sample data
		matrixData = Array.from({ length: 5 }, (_, rowIdx) =>
			Array.from({ length: 5 }, (_, colIdx) => ({
				value: Math.floor(Math.random() * 50) + 25,
				dimensions: Array.from({ length: 5 }, () => Math.floor(Math.random() * 50) + 25),
				confidence: Math.random() * 0.5 + 0.5,
				description: `Cell R${rowIdx}C${colIdx}`,
				isLeveragePoint: leveragePoints.some(
					(lp) => lp.cell.row === rowIdx && lp.cell.col === colIdx
				),
				riskLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as
					| 'low'
					| 'medium'
					| 'high'
			}))
		);

		isLoading = false;
	});

	function handleCellClick(row: number, col: number) {
		selectedCell = { row, col };
		showCellPopup = true;
	}

	function handleCellValueChange(row: number, col: number, value: number) {
		matrixData[row][col].value = Math.max(0, Math.min(100, value));
		matrixData = [...matrixData];
	}

	function getCellColor(cell: CellData) {
		if (showRiskHeatmap && cell.riskLevel) {
			const colors = {
				low: 'bg-success-100 dark:bg-success-900/30',
				medium: 'bg-warning-100 dark:bg-warning-900/30',
				high: 'bg-error-100 dark:bg-error-900/30'
			};
			return colors[cell.riskLevel];
		}
		return 'bg-field-depth dark:bg-field-elevated';
	}

	function getRiskBadgeColor(risk: 'low' | 'medium' | 'high') {
		const colors = {
			low: 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300',
			medium: 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-300',
			high: 'bg-error-100 text-error-700 dark:bg-error-900/30 dark:text-error-300'
		};
		return colors[risk];
	}

	// Computed metrics
	$: coherence = matrixData.length
		? Math.round(
				matrixData.flat().reduce((sum, cell) => sum + cell.confidence, 0) /
					(matrixData.flat().length || 1) *
					100
			)
		: 0;

	$: population = matrixData.length
		? Math.round(
				(matrixData.flat().filter((c) => c.value > 0).length / matrixData.flat().length) * 100
			)
		: 0;

	$: avgValue = matrixData.length
		? Math.round(
				matrixData.flat().reduce((sum, cell) => sum + cell.value, 0) /
					(matrixData.flat().length || 1)
			)
		: 0;
</script>

<svelte:head>
	<title>Matrix | Reality Transformer</title>
</svelte:head>

<div class="matrix-page">
	{#if isLoading}
		<div class="loading-state">
			<Spinner size="lg" />
			<p>Loading matrix...</p>
		</div>
	{:else}
		<!-- Header -->
		<header class="page-header">
			<div class="header-content">
				<div class="header-icon">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<rect x="3" y="3" width="7" height="7" />
						<rect x="14" y="3" width="7" height="7" />
						<rect x="14" y="14" width="7" height="7" />
						<rect x="3" y="14" width="7" height="7" />
					</svg>
				</div>
				<div>
					<h1>Transformation Map</h1>
					<p>Visualize and optimize your transformation journey</p>
				</div>
			</div>

			<div class="header-actions">
				<label class="risk-toggle">
					<input type="checkbox" bind:checked={showRiskHeatmap} />
					<span class="toggle-label">Risk Heatmap</span>
				</label>
				<Button variant="primary" size="sm">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="16"
						height="16"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="M12 5v14" />
						<path d="M5 12h14" />
					</svg>
					Generate Map
				</Button>
			</div>
		</header>

		<!-- Metrics bar -->
		<div class="metrics-bar">
			<div class="metric">
				<span class="metric-value">{coherence}%</span>
				<span class="metric-label">Coherence</span>
			</div>
			<div class="metric">
				<span class="metric-value">{population}%</span>
				<span class="metric-label">Population</span>
			</div>
			<div class="metric">
				<span class="metric-value">{avgValue}</span>
				<span class="metric-label">Average Score</span>
			</div>
			<div class="metric">
				<span class="metric-value">{leveragePoints.length}</span>
				<span class="metric-label">Power Spots</span>
			</div>
		</div>

		<!-- Risk legend -->
		{#if showRiskHeatmap}
			<div class="risk-legend">
				<span class="legend-title">Risk Level:</span>
				<span class="legend-item low">
					<span class="legend-dot"></span>
					Low
				</span>
				<span class="legend-item medium">
					<span class="legend-dot"></span>
					Medium
				</span>
				<span class="legend-item high">
					<span class="legend-dot"></span>
					High
				</span>
			</div>
		{/if}

		<!-- Main content -->
		<div class="matrix-content">
			<!-- Matrix Grid -->
			<div class="matrix-container card-elevated">
				<div class="matrix-grid">
					<!-- Top-left corner (empty) -->
					<div class="grid-corner"></div>

					<!-- Column headers -->
					{#each columnHeaders as header, idx}
						<div class="col-header">
							<span class="header-text">{header}</span>
						</div>
					{/each}

					<!-- Matrix body -->
					{#each matrixData as row, rowIdx}
						<!-- Row header -->
						<div class="row-header">
							<span class="header-text">{rowHeaders[rowIdx]}</span>
						</div>

						<!-- Data cells -->
						{#each row as cell, colIdx}
							<button
								class="matrix-cell {getCellColor(cell)}"
								class:leverage-point={cell.isLeveragePoint}
								class:selected={selectedCell?.row === rowIdx && selectedCell?.col === colIdx}
								on:click={() => handleCellClick(rowIdx, colIdx)}
							>
								{#if cell.isLeveragePoint}
									<span class="power-indicator" title="Power Spot">⚡</span>
								{/if}
								<span class="cell-value">{cell.value}</span>
								<div class="confidence-bar" style="width: {cell.confidence * 100}%"></div>
							</button>
						{/each}
					{/each}
				</div>
			</div>

			<!-- Side panel -->
			<div class="side-panel">
				<!-- Tabs -->
				<div class="panel-tabs">
					<button
						class="tab-btn"
						class:active={activeTab === 'overview'}
						on:click={() => (activeTab = 'overview')}
					>
						Overview
					</button>
					<button
						class="tab-btn"
						class:active={activeTab === 'leverage'}
						on:click={() => (activeTab = 'leverage')}
					>
						Power Spots
					</button>
					<button
						class="tab-btn"
						class:active={activeTab === 'templates'}
						on:click={() => (activeTab = 'templates')}
					>
						Plays
					</button>
				</div>

				<!-- Tab content -->
				<div class="panel-content">
					{#if activeTab === 'overview'}
						<div class="overview-content">
							<h3>Map Insights</h3>
							<p class="insight-text">
								Your transformation map shows strong foundations with opportunities for targeted
								improvements. Focus on Power Spots for maximum impact.
							</p>

							<div class="quick-stats">
								<div class="stat-card">
									<span class="stat-value positive">+12%</span>
									<span class="stat-label">Progress this week</span>
								</div>
								<div class="stat-card">
									<span class="stat-value">3</span>
									<span class="stat-label">Areas need attention</span>
								</div>
							</div>
						</div>
					{:else if activeTab === 'leverage'}
						<div class="leverage-content">
							<h3>Power Spots</h3>
							<p class="panel-description">
								Strategic points that create cascading positive effects
							</p>

							<div class="leverage-list">
								{#each leveragePoints as point}
									<button
										class="leverage-card"
										on:click={() => handleCellClick(point.cell.row, point.cell.col)}
									>
										<div class="leverage-header">
											<span class="leverage-title">{point.title}</span>
											<span class="impact-badge">{point.impact}% impact</span>
										</div>
										<p class="leverage-desc">{point.description}</p>
										<span class="cell-ref"
											>Cell: {rowHeaders[point.cell.row]} × {columnHeaders[point.cell.col]}</span
										>
									</button>
								{/each}
							</div>
						</div>
					{:else if activeTab === 'templates'}
						<div class="templates-content">
							<h3>Available Plays</h3>
							<p class="panel-description">Pre-designed transformation strategies</p>

							<div class="templates-list">
								{#each templates as template}
									<button class="template-card">
										<div class="template-header">
											<span class="template-name">{template.name}</span>
											<span class="risk-badge {getRiskBadgeColor(template.risk)}"
												>{template.risk}</span
											>
										</div>
										<p class="template-desc">{template.description}</p>
										<span class="timeline">{template.timeline}</span>
									</button>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Cell detail popup -->
		{#if showCellPopup && selectedCell}
			<div class="popup-overlay" on:click={() => (showCellPopup = false)} role="presentation">
				<div class="cell-popup card-elevated" on:click|stopPropagation role="dialog">
					<div class="popup-header">
						<h3>
							{rowHeaders[selectedCell.row]} × {columnHeaders[selectedCell.col]}
						</h3>
						<button class="close-btn" on:click={() => (showCellPopup = false)}>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="20"
								height="20"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="M18 6 6 18" />
								<path d="m6 6 12 12" />
							</svg>
						</button>
					</div>

					<div class="popup-body">
						<div class="value-control">
							<label for="cell-value">Score</label>
							<div class="value-input-group">
								<button
									class="value-btn"
									on:click={() =>
										handleCellValueChange(
											selectedCell.row,
											selectedCell.col,
											matrixData[selectedCell.row][selectedCell.col].value - 5
										)}
								>
									-
								</button>
								<input
									id="cell-value"
									type="number"
									min="0"
									max="100"
									value={matrixData[selectedCell.row][selectedCell.col].value}
									on:input={(e) =>
										handleCellValueChange(
											selectedCell.row,
											selectedCell.col,
											parseInt(e.currentTarget.value) || 0
										)}
								/>
								<button
									class="value-btn"
									on:click={() =>
										handleCellValueChange(
											selectedCell.row,
											selectedCell.col,
											matrixData[selectedCell.row][selectedCell.col].value + 5
										)}
								>
									+
								</button>
							</div>
						</div>

						<div class="dimensions-section">
							<h4>Dials</h4>
							<div class="dimensions-grid">
								{#each matrixData[selectedCell.row][selectedCell.col].dimensions as dim, idx}
									<div class="dimension-item">
										<span class="dim-label">Dial {idx + 1}</span>
										<div class="dim-bar-container">
											<div class="dim-bar" style="width: {dim}%"></div>
										</div>
										<span class="dim-value">{dim}</span>
									</div>
								{/each}
							</div>
						</div>

						{#if matrixData[selectedCell.row][selectedCell.col].isLeveragePoint}
							<div class="power-spot-badge">
								<span>⚡</span>
								<span>Power Spot - High Impact Cell</span>
							</div>
						{/if}
					</div>

					<div class="popup-footer">
						<Button variant="ghost" on:click={() => (showCellPopup = false)}>Cancel</Button>
						<Button
							variant="primary"
							on:click={() => {
								addToast('success', 'Cell updated');
								showCellPopup = false;
							}}>Save Changes</Button
						>
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.matrix-page {
		padding: 1.5rem;
		max-width: 1400px;
		margin: 0 auto;
		animation: fadeIn 0.2s ease;
	}

	/* Loading state */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		gap: 1rem;
	}

	.loading-state p {
		color: var(--color-text-whisper);
		font-size: 0.875rem;
	}

	/* Header */
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.header-content {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.header-icon {
		width: 48px;
		height: 48px;
		background: var(--gradient-primary);
		border-radius: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}

	.page-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.25rem;
	}

	.page-header p {
		color: var(--color-text-whisper);
		font-size: 0.875rem;
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.risk-toggle {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
	}

	.risk-toggle input {
		width: 1.125rem;
		height: 1.125rem;
		accent-color: var(--color-primary-500);
	}

	.toggle-label {
		font-size: 0.875rem;
		color: var(--color-text-manifest);
	}

	/* Metrics bar */
	.metrics-bar {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
		padding: 1rem;
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		overflow-x: auto;
	}

	.metric {
		flex: 1;
		min-width: 100px;
		text-align: center;
	}

	.metric-value {
		display: block;
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-primary-500);
	}

	.metric-label {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Risk legend */
	.risk-legend {
		display: flex;
		align-items: center;
		gap: 1.5rem;
		padding: 0.75rem 1rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
		margin-bottom: 1rem;
		font-size: 0.8125rem;
	}

	.legend-title {
		color: var(--color-text-whisper);
		font-weight: 500;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		color: var(--color-text-manifest);
	}

	.legend-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
	}

	.legend-item.low .legend-dot {
		background: var(--color-success-500);
	}
	.legend-item.medium .legend-dot {
		background: var(--color-warning-500);
	}
	.legend-item.high .legend-dot {
		background: var(--color-error-500);
	}

	/* Main content */
	.matrix-content {
		display: grid;
		grid-template-columns: 1fr 320px;
		gap: 1.5rem;
	}

	/* Matrix container */
	.matrix-container {
		padding: 1.25rem;
	}

	.matrix-grid {
		display: grid;
		grid-template-columns: 100px repeat(5, 1fr);
		grid-template-rows: 40px repeat(5, 1fr);
		gap: 4px;
		min-height: 400px;
	}

	.grid-corner {
		/* Empty corner cell */
	}

	.col-header,
	.row-header {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.5rem;
		background: var(--color-primary-50);
		border-radius: 0.375rem;
	}

	[data-theme='dark'] .col-header,
	[data-theme='dark'] .row-header {
		background: var(--color-primary-900);
	}

	.header-text {
		font-size: 0.6875rem;
		font-weight: 600;
		color: var(--color-primary-700);
		text-align: center;
		line-height: 1.2;
	}

	[data-theme='dark'] .header-text {
		color: var(--color-primary-300);
	}

	.matrix-cell {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0.75rem;
		border-radius: 0.5rem;
		border: 1px solid var(--color-veil-thin);
		cursor: pointer;
		transition: all 0.15s ease;
		min-height: 70px;
	}

	.matrix-cell:hover {
		border-color: var(--color-primary-400);
		transform: translateY(-1px);
	}

	.matrix-cell.selected {
		border-color: var(--color-primary-500);
		box-shadow: 0 0 0 3px var(--color-primary-100);
	}

	.matrix-cell.leverage-point {
		border-color: var(--color-accent);
		border-width: 2px;
	}

	.power-indicator {
		position: absolute;
		top: 2px;
		right: 2px;
		font-size: 0.625rem;
		background: var(--color-accent);
		color: white;
		width: 16px;
		height: 16px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.cell-value {
		font-size: 1.125rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.confidence-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		height: 3px;
		background: var(--color-primary-400);
		border-radius: 0 0 0.375rem 0.375rem;
		transition: width 0.3s ease;
	}

	/* Side panel */
	.side-panel {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		overflow: hidden;
	}

	.panel-tabs {
		display: flex;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.tab-btn {
		flex: 1;
		padding: 0.875rem 0.5rem;
		background: none;
		border: none;
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: all 0.15s ease;
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
	}

	.tab-btn:hover {
		color: var(--color-text-manifest);
	}

	.tab-btn.active {
		color: var(--color-primary-500);
		border-bottom-color: var(--color-primary-500);
	}

	.panel-content {
		padding: 1.25rem;
	}

	.panel-content h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.panel-description {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
		margin-bottom: 1rem;
	}

	/* Overview content */
	.insight-text {
		font-size: 0.875rem;
		color: var(--color-text-manifest);
		line-height: 1.6;
		margin-bottom: 1.5rem;
	}

	.quick-stats {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.stat-card {
		padding: 1rem;
		background: var(--color-field-depth);
		border-radius: 0.625rem;
	}

	.stat-card .stat-value {
		display: block;
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.stat-card .stat-value.positive {
		color: var(--color-success-500);
	}

	.stat-card .stat-label {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Leverage points */
	.leverage-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.leverage-card {
		padding: 1rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.625rem;
		text-align: left;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.leverage-card:hover {
		border-color: var(--color-accent);
	}

	.leverage-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.leverage-title {
		font-weight: 600;
		font-size: 0.875rem;
		color: var(--color-text-source);
	}

	.impact-badge {
		font-size: 0.6875rem;
		font-weight: 600;
		padding: 0.25rem 0.5rem;
		background: var(--color-accent);
		color: white;
		border-radius: 9999px;
	}

	.leverage-desc {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
		margin-bottom: 0.5rem;
	}

	.cell-ref {
		font-size: 0.6875rem;
		color: var(--color-text-hint);
	}

	/* Templates */
	.templates-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.template-card {
		padding: 1rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.625rem;
		text-align: left;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.template-card:hover {
		border-color: var(--color-primary-400);
	}

	.template-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.template-name {
		font-weight: 600;
		font-size: 0.875rem;
		color: var(--color-text-source);
	}

	.risk-badge {
		font-size: 0.6875rem;
		font-weight: 600;
		padding: 0.25rem 0.5rem;
		border-radius: 9999px;
		text-transform: capitalize;
	}

	.template-desc {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
		margin-bottom: 0.5rem;
	}

	.timeline {
		font-size: 0.6875rem;
		color: var(--color-text-hint);
	}

	/* Cell popup */
	.popup-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 50;
		padding: 1rem;
	}

	.cell-popup {
		width: 100%;
		max-width: 400px;
		max-height: 90vh;
		overflow-y: auto;
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.popup-header h3 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.close-btn {
		padding: 0.5rem;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.375rem;
		transition: all 0.15s ease;
	}

	.close-btn:hover {
		background: var(--color-field-depth);
		color: var(--color-text-source);
	}

	.popup-body {
		padding: 1.25rem;
	}

	.value-control {
		margin-bottom: 1.5rem;
	}

	.value-control label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.5rem;
	}

	.value-input-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.value-btn {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-source);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.value-btn:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	.value-input-group input {
		flex: 1;
		text-align: center;
		padding: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text-source);
		background: var(--color-field-void);
	}

	.value-input-group input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.dimensions-section h4 {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.75rem;
	}

	.dimensions-grid {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.dimension-item {
		display: grid;
		grid-template-columns: 60px 1fr 40px;
		align-items: center;
		gap: 0.75rem;
	}

	.dim-label {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	.dim-bar-container {
		height: 6px;
		background: var(--color-field-depth);
		border-radius: 3px;
		overflow: hidden;
	}

	.dim-bar {
		height: 100%;
		background: var(--color-primary-400);
		border-radius: 3px;
		transition: width 0.3s ease;
	}

	.dim-value {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-source);
		text-align: right;
	}

	.power-spot-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem;
		margin-top: 1rem;
		background: var(--color-accent);
		color: white;
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 500;
	}

	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1.25rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	/* Mobile responsive */
	@media (max-width: 1024px) {
		.matrix-content {
			grid-template-columns: 1fr;
		}

		.side-panel {
			order: -1;
		}
	}

	@media (max-width: 767px) {
		.matrix-page {
			padding: 1rem;
		}

		.page-header {
			flex-direction: column;
		}

		.header-actions {
			width: 100%;
			justify-content: space-between;
		}

		.metrics-bar {
			flex-wrap: wrap;
		}

		.metric {
			min-width: calc(50% - 0.5rem);
		}

		.matrix-grid {
			grid-template-columns: 60px repeat(5, 1fr);
		}

		.row-header {
			padding: 0.25rem;
		}

		.header-text {
			font-size: 0.5rem;
		}

		.matrix-cell {
			min-height: 50px;
			padding: 0.375rem;
		}

		.cell-value {
			font-size: 0.875rem;
		}
	}
</style>
