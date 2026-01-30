<script lang="ts">
	/**
	 * EffectPopup - Select column dimensions for the transformation matrix
	 *
	 * Features:
	 * - Document tabs (3 initial + ability to add more)
	 * - Max 10 column options to choose from per tab
	 * - Must select exactly 5 dimensions
	 * - Generate more options button (LLM call, max 5 new per call)
	 * - Submit button wired per tab
	 */

	import { createEventDispatcher } from 'svelte';
	import { matrix, documentTabs, activeTab, isLoadingOptions } from '$lib/stores';
	import { Button, Spinner } from '$lib/components/ui';

	export let open = false;

	const dispatch = createEventDispatcher<{
		close: void;
		submit: { tabId: string };
	}>();

	let newTabName = '';
	let showAddTab = false;

	$: currentTab = $activeTab;
	$: canSubmit = currentTab && currentTab.selectedEffects.length === 5;
	$: canGenerateMore = currentTab && currentTab.effectOptions.length < 10;
	$: selectedCount = currentTab?.selectedEffects.length || 0;

	function handleClose() {
		open = false;
		showAddTab = false;
		newTabName = '';
		dispatch('close');
	}

	function handleTabClick(tabId: string) {
		matrix.setActiveTab(tabId);
	}

	function handleToggleOption(optionId: string) {
		if (currentTab) {
			matrix.toggleEffectSelection(currentTab.id, optionId);
		}
	}

	async function handleGenerateMore() {
		if (currentTab && canGenerateMore) {
			await matrix.generateMoreEffectOptions(currentTab.id);
		}
	}

	function handleSubmit() {
		if (currentTab && canSubmit) {
			const success = matrix.submitEffectSelection(currentTab.id);
			if (success) {
				dispatch('submit', { tabId: currentTab.id });
				handleClose();
			}
		}
	}

	function handleAddTab() {
		if (newTabName.trim()) {
			matrix.addDocumentTab(newTabName.trim());
			newTabName = '';
			showAddTab = false;
		}
	}

	function handleRemoveTab(tabId: string) {
		matrix.removeDocumentTab(tabId);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleClose();
		}
	}
</script>

{#if open}
	<div
		class="popup-overlay"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="presentation"
		tabindex="-1"
	>
		<div
			class="effect-popup"
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			aria-modal="true"
			aria-labelledby="effect-title"
		>
			<div class="popup-header">
				<h3 id="effect-title">Select Effect Dimensions</h3>
				<button class="close-btn" on:click={handleClose} aria-label="Close">
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

			<!-- Document Tabs -->
			<div class="tabs-container">
				<div class="tabs-row">
					{#each $documentTabs as tab (tab.id)}
						<button
							class="tab-btn"
							class:active={currentTab?.id === tab.id}
							on:click={() => handleTabClick(tab.id)}
						>
							<span class="tab-name">{tab.name}</span>
							{#if tab.type === 'custom'}
								<button
									class="tab-remove"
									on:click|stopPropagation={() => handleRemoveTab(tab.id)}
									aria-label="Remove tab"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										width="12"
										height="12"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
									>
										<path d="M18 6 6 18" />
										<path d="m6 6 12 12" />
									</svg>
								</button>
							{/if}
						</button>
					{/each}

					<button class="tab-add-btn" on:click={() => (showAddTab = !showAddTab)} aria-label="Add document tab">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="14"
							height="14"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M12 5v14" />
							<path d="M5 12h14" />
						</svg>
					</button>
				</div>

				{#if showAddTab}
					<div class="add-tab-form">
						<input
							type="text"
							bind:value={newTabName}
							placeholder="Document name..."
							on:keydown={(e) => e.key === 'Enter' && handleAddTab()}
						/>
						<Button variant="primary" size="sm" on:click={handleAddTab} disabled={!newTabName.trim()}>
							Add
						</Button>
						<Button variant="ghost" size="sm" on:click={() => (showAddTab = false)}>
							Cancel
						</Button>
					</div>
				{/if}
			</div>

			<div class="popup-body">
				<div class="selection-info">
					<span class="selection-count" class:complete={selectedCount === 5} class:error={selectedCount > 5}>
						{selectedCount}/5 selected
					</span>
					<span class="selection-hint">Select exactly 5 effect dimensions</span>
				</div>

				{#if currentTab}
					<div class="options-list">
						{#each currentTab.effectOptions as option (option.id)}
							{@const isSelected = currentTab.selectedEffects.includes(option.id)}
							{@const isDisabled = !isSelected && selectedCount >= 5}
							<button
								class="option-item"
								class:selected={isSelected}
								class:disabled={isDisabled}
								on:click={() => !isDisabled && handleToggleOption(option.id)}
								disabled={isDisabled}
							>
								<div class="option-checkbox" class:checked={isSelected}>
									{#if isSelected}
										<svg
											xmlns="http://www.w3.org/2000/svg"
											width="14"
											height="14"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="3"
										>
											<polyline points="20 6 9 17 4 12" />
										</svg>
									{/if}
								</div>
								<div class="option-content">
									<span class="option-label">{option.label}</span>
									{#if option.description}
										<span class="option-description">{option.description}</span>
									{/if}
								</div>
							</button>
						{/each}
					</div>

					{#if canGenerateMore}
						<button
							class="generate-more-btn"
							on:click={handleGenerateMore}
							disabled={$isLoadingOptions}
						>
							{#if $isLoadingOptions}
								<Spinner size="sm" />
								<span>Generating...</span>
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="16"
									height="16"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path d="M12 5v14" />
									<path d="M5 12h14" />
								</svg>
								<span>Generate More Options ({currentTab.effectOptions.length}/10)</span>
							{/if}
						</button>
					{:else}
						<div class="options-limit-notice">
							Maximum options reached (10/10)
						</div>
					{/if}
				{/if}
			</div>

			<div class="popup-footer">
				<Button variant="ghost" on:click={handleClose}>Cancel</Button>
				<Button variant="primary" on:click={handleSubmit} disabled={!canSubmit}>
					Confirm Selection
				</Button>
			</div>
		</div>
	</div>
{/if}

<style>
	.popup-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: 1rem;
	}

	.effect-popup {
		width: 100%;
		max-width: 550px;
		max-height: 85vh;
		display: flex;
		flex-direction: column;
		background: var(--color-field-surface);
		border-radius: 1rem;
		border: 1px solid var(--color-veil-thin);
		box-shadow: var(--shadow-elevated);
		overflow: hidden;
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
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

	/* Tabs */
	.tabs-container {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
		background: var(--color-field-depth);
		flex-shrink: 0;
	}

	.tabs-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		overflow-x: auto;
		padding-bottom: 0.25rem;
	}

	.tab-btn {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.75rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.15s ease;
		white-space: nowrap;
	}

	.tab-btn:hover {
		border-color: var(--color-primary-400);
	}

	.tab-btn.active {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: white;
	}

	.tab-name {
		max-width: 120px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.tab-remove {
		padding: 0.125rem;
		background: none;
		border: none;
		color: inherit;
		opacity: 0.7;
		cursor: pointer;
		border-radius: 0.25rem;
	}

	.tab-remove:hover {
		opacity: 1;
		background: rgba(255, 255, 255, 0.2);
	}

	.tab-add-btn {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		border: 1px dashed var(--color-veil-thin);
		border-radius: 0.5rem;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.tab-add-btn:hover {
		border-color: var(--color-primary-400);
		color: var(--color-primary-500);
	}

	.add-tab-form {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.75rem;
	}

	.add-tab-form input {
		flex: 1;
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
		font-size: 0.875rem;
	}

	.add-tab-form input:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	/* Body */
	.popup-body {
		flex: 1;
		padding: 1rem 1.25rem;
		overflow-y: auto;
	}

	.selection-info {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.selection-count {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-manifest);
	}

	.selection-count.complete {
		color: #059669;
	}

	[data-theme='dark'] .selection-count.complete {
		color: #34d399;
	}

	.selection-count.error {
		color: #dc2626;
	}

	[data-theme='dark'] .selection-count.error {
		color: #f87171;
	}

	.selection-hint {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	.options-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.option-item {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid transparent;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
		width: 100%;
	}

	.option-item:hover:not(.disabled) {
		border-color: var(--color-primary-400);
	}

	.option-item.selected {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	[data-theme='dark'] .option-item.selected {
		background: rgba(15, 76, 117, 0.2);
	}

	.option-item.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.option-checkbox {
		width: 20px;
		height: 20px;
		border: 2px solid var(--color-veil-thin);
		border-radius: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		transition: all 0.15s ease;
	}

	.option-checkbox.checked {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: white;
	}

	.option-content {
		flex: 1;
		min-width: 0;
	}

	.option-label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.option-description {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		margin-top: 0.125rem;
	}

	.generate-more-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem;
		margin-top: 1rem;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		color: var(--color-primary-600);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.generate-more-btn:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	.generate-more-btn:disabled {
		opacity: 0.7;
		cursor: wait;
	}

	[data-theme='dark'] .generate-more-btn {
		color: var(--color-primary-400);
	}

	[data-theme='dark'] .generate-more-btn:hover:not(:disabled) {
		background: rgba(15, 76, 117, 0.2);
	}

	.options-limit-notice {
		text-align: center;
		padding: 0.75rem;
		margin-top: 1rem;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		background: var(--color-field-depth);
		border-radius: 0.5rem;
	}

	/* Footer */
	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1rem 1.25rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}
</style>
