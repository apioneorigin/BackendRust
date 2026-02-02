<script lang="ts">
	/**
	 * LivePreviewBox - Real-time coherence and transformation preview
	 *
	 * Shows:
	 * - Coherence score
	 * - Balance indicator
	 * - Population level
	 * - Pending changes count
	 * - Estimated impact
	 * - Top insights
	 */

	export let coherence = 0;
	export let balance = 0;
	export let population = 0;
	export let avgScore = 0;
	export let powerSpots = 0;
	export let pendingChanges = 0;

	$: coherenceColor = coherence >= 75 ? 'text-success' : coherence >= 50 ? 'text-warning' : 'text-error';
	$: balanceColor = balance >= 75 ? 'text-success' : balance >= 50 ? 'text-warning' : 'text-error';
</script>

<div class="live-preview">
	<div class="preview-header">
		<div class="header-icon">
			<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
				<circle cx="12" cy="12" r="3"/>
			</svg>
		</div>
		<h3>Live Preview</h3>
		{#if pendingChanges > 0}
			<span class="pending-badge">{pendingChanges} pending</span>
		{/if}
	</div>

	<div class="preview-content">
		<!-- Primary metrics -->
		<div class="metrics-row">
			<div class="metric-box">
				<div class="metric-value {coherenceColor}">{coherence}%</div>
				<div class="metric-label">Coherence</div>
				<div class="metric-bar">
					<div class="bar-fill {coherenceColor}" style="width: {coherence}%"></div>
				</div>
			</div>
			<div class="metric-box">
				<div class="metric-value {balanceColor}">{balance}%</div>
				<div class="metric-label">Balance</div>
				<div class="metric-bar">
					<div class="bar-fill {balanceColor}" style="width: {balance}%"></div>
				</div>
			</div>
		</div>

		<!-- Secondary metrics -->
		<div class="stats-grid">
			<div class="stat-item">
				<span class="stat-value">{population}%</span>
				<span class="stat-label">Population</span>
			</div>
			<div class="stat-item">
				<span class="stat-value">{avgScore}</span>
				<span class="stat-label">Avg Score</span>
			</div>
			<div class="stat-item">
				<span class="stat-value">{powerSpots}</span>
				<span class="stat-label">Power Spots</span>
			</div>
		</div>

		<!-- Insights summary -->
		<div class="insights-section">
			<div class="insight-item">
				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
				</svg>
				<span>Focus on Power Spots for maximum impact</span>
			</div>
			{#if coherence < 50}
				<div class="insight-item warning">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>
						<path d="M12 9v4"/>
						<path d="M12 17h.01"/>
					</svg>
					<span>Low coherence - review alignment</span>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.live-preview {
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.preview-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 0.75rem;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.header-icon {
		color: var(--color-text-whisper);
	}

	.preview-header h3 {
		font-size: 15px;
		font-weight: 500;
		color: var(--color-text-source);
		flex: 1;
	}

	.pending-badge {
		font-size: 11px;
		font-weight: 500;
		padding: 0.125rem 0.375rem;
		background: var(--color-primary-500);
		color: #ffffff;
		border-radius: 9999px;
	}

	.preview-content {
		flex: 1;
		padding: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.625rem;
		overflow-y: auto;
		overflow-x: hidden;
		min-height: 0;
	}

	.metrics-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
	}

	.metric-box {
		padding: 0.625rem;
		background: var(--color-field-depth);
		border-radius: 0.375rem;
		text-align: center;
	}

	.metric-value {
		font-size: 1rem;
		font-weight: 600;
	}

	.metric-value.text-success {
		color: #16a34a;
	}

	.metric-value.text-warning {
		color: #d97706;
	}

	.metric-value.text-error {
		color: #dc2626;
	}

	.metric-label {
		font-size: 12px;
		color: var(--color-text-whisper);
		margin-bottom: 0.375rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.metric-bar {
		height: 3px;
		background: var(--color-veil-thin);
		border-radius: 2px;
		overflow: hidden;
	}

	.bar-fill {
		height: 100%;
		border-radius: 2px;
		transition: width 0.2s ease;
	}

	.bar-fill.text-success {
		background: #16a34a;
	}

	.bar-fill.text-warning {
		background: #d97706;
	}

	.bar-fill.text-error {
		background: #dc2626;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.375rem;
	}

	.stat-item {
		text-align: center;
		padding: 0.5rem 0.25rem;
		background: var(--color-field-depth);
		border-radius: 0.25rem;
	}

	.stat-value {
		display: block;
		font-size: 15px;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.stat-label {
		font-size: 11px;
		color: var(--color-text-whisper);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.insights-section {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		margin-top: auto;
	}

	.insight-item {
		display: flex;
		align-items: flex-start;
		gap: 0.375rem;
		font-size: 13px;
		color: var(--color-text-manifest);
		padding: 0.5rem;
		background: var(--color-field-depth);
		border-radius: 0.25rem;
	}

	.insight-item svg {
		flex-shrink: 0;
		color: var(--color-text-whisper);
		margin-top: 1px;
	}

	.insight-item.warning {
		background: rgba(217, 119, 6, 0.05);
	}

	.insight-item.warning svg {
		color: #d97706;
	}
</style>
