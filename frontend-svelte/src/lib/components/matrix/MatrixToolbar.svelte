<script lang="ts">
	/**
	 * MatrixToolbar - Row of 5 popup trigger buttons
	 *
	 * Buttons: Power Spots, Plays, Scenarios, Sensitivity, Risk
	 * Each opens its own popup modal.
	 */

	import { createEventDispatcher } from 'svelte';

	export let showRiskHeatmap = false;

	const dispatch = createEventDispatcher<{
		openPopup: { type: 'powerSpots' | 'plays' | 'scenarios' | 'sensitivity' | 'risk' };
		toggleRisk: { enabled: boolean };
	}>();

	function handleOpenPopup(type: 'powerSpots' | 'plays' | 'scenarios' | 'sensitivity' | 'risk') {
		dispatch('openPopup', { type });
	}

	function handleToggleRisk() {
		dispatch('toggleRisk', { enabled: !showRiskHeatmap });
	}
</script>

<div class="matrix-toolbar">
	<button class="toolbar-btn" on:click={() => handleOpenPopup('powerSpots')} title="Power Spots">
		<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>
		</svg>
		<span>Power Spots</span>
	</button>

	<button class="toolbar-btn" on:click={() => handleOpenPopup('plays')} title="Plays">
		<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<rect width="18" height="18" x="3" y="3" rx="2"/>
			<path d="M7 7h10"/>
			<path d="M7 12h10"/>
			<path d="M7 17h10"/>
		</svg>
		<span>Plays</span>
	</button>

	<button class="toolbar-btn" on:click={() => handleOpenPopup('scenarios')} title="Scenarios">
		<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M16 3h5v5"/>
			<path d="M8 3H3v5"/>
			<path d="M21 3l-7 7"/>
			<path d="M3 3l7 7"/>
			<path d="M16 21h5v-5"/>
			<path d="M8 21H3v-5"/>
			<path d="M21 21l-7-7"/>
			<path d="M3 21l7-7"/>
		</svg>
		<span>Scenarios</span>
	</button>

	<button class="toolbar-btn" on:click={() => handleOpenPopup('sensitivity')} title="Sensitivity">
		<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M12 20v-6"/>
			<path d="M12 10V4"/>
			<path d="M4 20v-4"/>
			<path d="M4 12V4"/>
			<path d="M20 20v-8"/>
			<path d="M20 8V4"/>
			<circle cx="12" cy="14" r="2"/>
			<circle cx="4" cy="16" r="2"/>
			<circle cx="20" cy="12" r="2"/>
		</svg>
		<span>Sensitivity</span>
	</button>

	<button
		class="toolbar-btn"
		class:active={showRiskHeatmap}
		on:click={handleToggleRisk}
		title="Risk View"
	>
		<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>
			<path d="M12 9v4"/>
			<path d="M12 17h.01"/>
		</svg>
		<span>Risk</span>
	</button>
</div>

<style>
	.matrix-toolbar {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.25rem;
		padding: 0.5rem;
	}

	.toolbar-btn {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.5rem;
		background: transparent;
		border: none;
		border-radius: 0.25rem;
		font-size: 12px;
		font-weight: 400;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: all 0.1s ease;
		white-space: nowrap;
	}

	.toolbar-btn:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.toolbar-btn.active {
		background: var(--color-text-source);
		color: var(--color-field-void);
	}

	.toolbar-btn svg {
		flex-shrink: 0;
		width: 14px;
		height: 14px;
	}

	@media (max-width: 900px) {
		.toolbar-btn span {
			display: none;
		}

		.toolbar-btn {
			padding: 0.375rem;
		}
	}
</style>
