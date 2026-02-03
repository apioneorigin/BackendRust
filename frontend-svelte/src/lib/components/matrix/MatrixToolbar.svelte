<script lang="ts">
	/**
	 * MatrixToolbar - Row of popup trigger buttons
	 *
	 * Buttons: Power Spots (view), Plays, Scenarios, Risk (view), Save
	 * Power Spots and Risk are filtered views that dim non-relevant cells.
	 */

	import { createEventDispatcher } from 'svelte';

	export let showPowerSpotsView = false;
	export let showRiskView = false;
	export let disabled = false;

	const dispatch = createEventDispatcher<{
		openPopup: { type: 'plays' | 'scenarios' };
		togglePowerSpots: { enabled: boolean };
		toggleRisk: { enabled: boolean };
		saveScenario: void;
	}>();

	function handleOpenPopup(type: 'plays' | 'scenarios') {
		if (disabled) return;
		dispatch('openPopup', { type });
	}

	function handleTogglePowerSpots() {
		if (disabled) return;
		// Turn off risk view when enabling power spots
		if (!showPowerSpotsView && showRiskView) {
			dispatch('toggleRisk', { enabled: false });
		}
		dispatch('togglePowerSpots', { enabled: !showPowerSpotsView });
	}

	function handleToggleRisk() {
		if (disabled) return;
		// Turn off power spots view when enabling risk
		if (!showRiskView && showPowerSpotsView) {
			dispatch('togglePowerSpots', { enabled: false });
		}
		dispatch('toggleRisk', { enabled: !showRiskView });
	}

	function handleSave() {
		if (disabled) return;
		dispatch('saveScenario');
	}
</script>

<div class="matrix-toolbar" class:disabled>
	<button
		class="toolbar-btn"
		class:active={showPowerSpotsView}
		on:click={handleTogglePowerSpots}
		title="Power Spots View"
	>
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

	<button
		class="toolbar-btn"
		class:active={showRiskView}
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

	<button class="toolbar-btn save-btn" on:click={handleSave} title="Save Scenario">
		<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
			<polyline points="17 21 17 13 7 13 7 21"/>
			<polyline points="7 3 7 8 15 8"/>
		</svg>
		<span>Save</span>
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
		justify-content: center;
		gap: 0.25rem;
		padding: 0.375rem 0.5rem;
		min-width: 100px;
		background: transparent;
		border: 1px solid var(--color-accent);
		border-radius: 0.5rem;
		font-size: var(--font-size-base);
		font-weight: 400;
		color: var(--color-accent);
		cursor: pointer;
		transition: all 0.1s ease;
		white-space: nowrap;
	}

	.toolbar-btn:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.toolbar-btn.active {
		background: var(--color-primary-500);
		color: #ffffff;
	}

	.toolbar-btn svg {
		flex-shrink: 0;
		width: 14px;
		height: 14px;
	}

	/* Disabled state - non-interactive on welcome page */
	.disabled .toolbar-btn {
		opacity: 0.4;
		cursor: default;
		pointer-events: none;
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
