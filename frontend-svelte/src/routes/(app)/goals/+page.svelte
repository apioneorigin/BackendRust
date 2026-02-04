<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { addToast, auth, chat } from '$lib/stores';
	import { Button, Spinner } from '$lib/components/ui';
	import { api } from '$lib/utils/api';

	interface DiscoveredGoal {
		id: string;
		type: string;
		identity: string;
		firstMove: string;
		confidence: number;
		sourceFiles: string[];
		createdAt: string;
		addedToInventory: boolean;
	}

	interface SavedGoal extends DiscoveredGoal {
		savedAt: string;
	}

	interface UploadedFile {
		name: string;
		content: string;
		type: string;
	}

	let uploadedFiles: UploadedFile[] = [];
	let discoveredGoals: DiscoveredGoal[] = [];
	let savedGoals: SavedGoal[] = [];
	let isDiscovering = false;
	let isLoadingInventory = true;
	let activeTab: 'discover' | 'saved' = 'discover';
	let dragOver = false;

	const goalTypeColors: Record<string, string> = {
		OPTIMIZE: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
		TRANSFORM: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
		DISCOVER: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
		QUANTUM: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
		HIDDEN: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
		INTEGRATION: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900 dark:text-cyan-300',
		DIFFERENTIATION: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
		ANTI_SILOING: 'bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300',
		SYNTHESIS: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300',
		RECONCILIATION: 'bg-teal-100 text-teal-700 dark:bg-teal-900 dark:text-teal-300',
		ARBITRAGE: 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300'
	};

	onMount(async () => {
		await loadSavedGoals();
	});

	async function loadSavedGoals() {
		try {
			const data = await api.get<{ goals: SavedGoal[] }>('/api/goal-inventory/list');
			savedGoals = data.goals || [];
		} catch (error) {
			console.error('Failed to load saved goals:', error);
		} finally {
			isLoadingInventory = false;
		}
	}

	async function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files) {
			await processFiles(Array.from(input.files));
		}
	}

	async function handleDrop(event: DragEvent) {
		event.preventDefault();
		dragOver = false;
		if (event.dataTransfer?.files) {
			await processFiles(Array.from(event.dataTransfer.files));
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		dragOver = true;
	}

	function handleDragLeave() {
		dragOver = false;
	}

	async function processFiles(files: File[]) {
		for (const file of files) {
			// Skip if already uploaded
			if (uploadedFiles.some((f) => f.name === file.name)) continue;

			try {
				const content = await readFileContent(file);
				uploadedFiles = [
					...uploadedFiles,
					{
						name: file.name,
						content,
						type: file.type || 'text/plain'
					}
				];
			} catch (error) {
				addToast('error', `Failed to read ${file.name}`);
			}
		}
	}

	async function readFileContent(file: File): Promise<string> {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = () => resolve(reader.result as string);
			reader.onerror = reject;
			reader.readAsText(file);
		});
	}

	function removeFile(fileName: string) {
		uploadedFiles = uploadedFiles.filter((f) => f.name !== fileName);
	}

	async function discoverGoals() {
		if (uploadedFiles.length === 0) {
			addToast('error', 'Please upload at least one file');
			return;
		}

		isDiscovering = true;
		try {
			const data = await api.post<{ goals: DiscoveredGoal[] }>('/api/goal-inventory/generate', {
				files: uploadedFiles,
				existing_goals: discoveredGoals
			});
			discoveredGoals = [...discoveredGoals, ...data.goals];
			addToast('success', `Discovered ${data.goals.length} goals`);
		} catch (error: any) {
			addToast('error', error.message || 'Failed to discover goals');
		} finally {
			isDiscovering = false;
		}
	}

	async function saveGoalToInventory(goal: DiscoveredGoal) {
		const savedGoal: SavedGoal = {
			...goal,
			savedAt: new Date().toISOString(),
			addedToInventory: true
		};

		savedGoals = [...savedGoals, savedGoal];

		// Update local state
		discoveredGoals = discoveredGoals.map((g) =>
			g.id === goal.id ? { ...g, addedToInventory: true } : g
		);

		// Persist to backend
		try {
			await api.post('/api/goal-inventory/save', { goals: savedGoals });
			addToast('success', 'Goal saved to library');
		} catch (error) {
			addToast('error', 'Failed to save goal');
		}
	}

	async function removeFromInventory(goalId: string) {
		try {
			await api.post('/api/goal-inventory/remove', { goal_id: goalId });
			savedGoals = savedGoals.filter((g) => g.id !== goalId);
			addToast('success', 'Goal removed from library');
		} catch (error) {
			addToast('error', 'Failed to remove goal');
		}
	}

	async function startChatWithGoal(goal: DiscoveredGoal | SavedGoal) {
		// Create a new conversation with this goal as context
		try {
			const conversation = await api.post<{ id: string }>('/api/chat/conversations', {
				title: goal.identity,
				context: `Goal: ${goal.identity}\n\nFirst Move: ${goal.firstMove}\n\nType: ${goal.type}\nConfidence: ${goal.confidence}%`
			});
			await chat.loadConversations();
			goto(`/chat`);
			await chat.selectConversation(conversation.id);
		} catch (error) {
			addToast('error', 'Failed to create chat');
		}
	}

	function getConfidenceColor(confidence: number): string {
		if (confidence >= 90) return 'text-green-600 dark:text-green-400';
		if (confidence >= 70) return 'text-blue-600 dark:text-blue-400';
		if (confidence >= 50) return 'text-yellow-600 dark:text-yellow-400';
		return 'text-red-600 dark:text-red-400';
	}

	function clearDiscoveredGoals() {
		discoveredGoals = [];
	}
</script>

<svelte:head>
	<title>Goal Discovery | Reality Transformer</title>
</svelte:head>

<div class="goals-page">
	<!-- Page header -->
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
					<circle cx="12" cy="12" r="10" />
					<circle cx="12" cy="12" r="6" />
					<circle cx="12" cy="12" r="2" />
				</svg>
			</div>
			<div>
				<h1>Goal Discovery</h1>
				<p>Upload files to discover actionable goals</p>
			</div>
		</div>
		<div class="header-stats">
			<div class="stat-item">
				<span class="stat-value">{uploadedFiles.length}</span>
				<span class="stat-label">Files</span>
			</div>
			<div class="stat-item">
				<span class="stat-value">{discoveredGoals.length}</span>
				<span class="stat-label">Discovered</span>
			</div>
			<div class="stat-item">
				<span class="stat-value">{savedGoals.length}</span>
				<span class="stat-label">Saved</span>
			</div>
		</div>
	</header>

	<!-- Tabs -->
	<div class="tabs">
		<button class="tab" class:active={activeTab === 'discover'} on:click={() => (activeTab = 'discover')}>
			<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
				<polyline points="17 8 12 3 7 8" />
				<line x1="12" x2="12" y1="3" y2="15" />
			</svg>
			Upload Files
		</button>
		<button class="tab" class:active={activeTab === 'saved'} on:click={() => (activeTab = 'saved')}>
			<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
			</svg>
			My Library ({savedGoals.length})
		</button>
	</div>

	{#if activeTab === 'discover'}
		<!-- File upload section -->
		<section class="upload-section">
			<div
				class="drop-zone"
				class:drag-over={dragOver}
				on:drop={handleDrop}
				on:dragover={handleDragOver}
				on:dragleave={handleDragLeave}
				role="button"
				tabindex="0"
			>
				<input
					type="file"
					id="file-input"
					multiple
					accept=".txt,.pdf,.csv,.json,.md,.doc,.docx,.xls,.xlsx"
					on:change={handleFileSelect}
					class="hidden"
				/>
				<label for="file-input" class="drop-zone-content">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="48"
						height="48"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
						<polyline points="17 8 12 3 7 8" />
						<line x1="12" x2="12" y1="3" y2="15" />
					</svg>
					<p class="drop-text">Drag & drop files here, or click to browse</p>
					<p class="drop-hint">Supports TXT, PDF, CSV, JSON, MD, DOC, XLS files</p>
				</label>
			</div>

			{#if uploadedFiles.length > 0}
				<div class="uploaded-files">
					<div class="files-header">
						<h3>Uploaded Files ({uploadedFiles.length})</h3>
						{#if uploadedFiles.length >= 2}
							<span class="multi-file-badge">Multi-file analysis enabled</span>
						{/if}
					</div>
					<div class="files-grid">
						{#each uploadedFiles as file (file.name)}
							<div class="file-chip">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
									<polyline points="14 2 14 8 20 8" />
								</svg>
								<span class="file-name">{file.name}</span>
								<button class="remove-file" on:click={() => removeFile(file.name)} title="Remove file">
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M18 6 6 18" />
										<path d="m6 6 12 12" />
									</svg>
								</button>
							</div>
						{/each}
					</div>
					<div class="discover-actions">
						<Button variant="primary" on:click={discoverGoals} disabled={isDiscovering}>
							{#if isDiscovering}
								<Spinner size="sm" />
								<span>Analyzing...</span>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<circle cx="12" cy="12" r="10" />
									<circle cx="12" cy="12" r="6" />
									<circle cx="12" cy="12" r="2" />
								</svg>
								Discover Goals
							{/if}
						</Button>
					</div>
				</div>
			{/if}
		</section>

		<!-- Discovered goals section -->
		{#if discoveredGoals.length > 0}
			<section class="goals-section">
				<div class="section-header">
					<h2>Discovered Goals ({discoveredGoals.length})</h2>
					<button class="clear-btn" on:click={clearDiscoveredGoals}>Clear all</button>
				</div>
				<div class="goals-grid">
					{#each discoveredGoals as goal (goal.id)}
						<div class="goal-card card-elevated">
							<div class="goal-header">
								<span class="goal-type {goalTypeColors[goal.type] || 'bg-gray-100 text-gray-700'}">
									{goal.type.replace('_', ' ')}
								</span>
								<span class="goal-confidence {getConfidenceColor(goal.confidence)}">
									{goal.confidence}%
								</span>
							</div>
							<h3 class="goal-identity">{goal.identity}</h3>
							<p class="goal-first-move">{goal.firstMove}</p>
							<div class="goal-sources">
								{#each goal.sourceFiles as source}
									<span class="source-badge">{source}</span>
								{/each}
							</div>
							<div class="goal-actions">
								<button
									class="action-btn save-btn"
									on:click={() => saveGoalToInventory(goal)}
									disabled={goal.addedToInventory}
								>
									{#if goal.addedToInventory}
										<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M20 6 9 17l-5-5" />
										</svg>
										Saved
									{:else}
										<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
										</svg>
										Save to Library
									{/if}
								</button>
								<button class="action-btn chat-btn" on:click={() => startChatWithGoal(goal)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
									</svg>
									Start Chat
								</button>
							</div>
						</div>
					{/each}
				</div>
			</section>
		{/if}
	{:else}
		<!-- Saved goals (library) -->
		<section class="goals-section">
			{#if isLoadingInventory}
				<div class="loading-state">
					<Spinner size="lg" />
					<p>Loading your library...</p>
				</div>
			{:else if savedGoals.length === 0}
				<div class="empty-state">
					<div class="empty-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
							<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
						</svg>
					</div>
					<h3>No saved goals</h3>
					<p>Discover goals from your files and save them here</p>
					<Button variant="primary" on:click={() => (activeTab = 'discover')}>
						Start Discovering
					</Button>
				</div>
			{:else}
				<div class="goals-grid">
					{#each savedGoals as goal (goal.id)}
						<div class="goal-card card-elevated">
							<div class="goal-header">
								<span class="goal-type {goalTypeColors[goal.type] || 'bg-gray-100 text-gray-700'}">
									{goal.type.replace('_', ' ')}
								</span>
								<span class="goal-confidence {getConfidenceColor(goal.confidence)}">
									{goal.confidence}%
								</span>
							</div>
							<h3 class="goal-identity">{goal.identity}</h3>
							<p class="goal-first-move">{goal.firstMove}</p>
							<div class="goal-sources">
								{#each goal.sourceFiles as source}
									<span class="source-badge">{source}</span>
								{/each}
							</div>
							<div class="goal-actions">
								<button class="action-btn chat-btn" on:click={() => startChatWithGoal(goal)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
									</svg>
									Start Chat
								</button>
								<button class="action-btn remove-btn" on:click={() => removeFromInventory(goal.id)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M3 6h18" />
										<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
										<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
									</svg>
									Remove
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>

<style>
	.goals-page {
		padding: 2rem 3rem;
		width: 100%;
		height: 100%;
		overflow-y: auto;
		overflow-x: hidden;
		box-sizing: border-box;
		animation: fadeIn 0.2s ease;
	}

	.goals-page > * {
		max-width: 1400px;
	}

	/* Page header */
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1.5rem;
		padding-bottom: 1.5rem;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.header-content {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.header-icon {
		width: 48px;
		height: 48px;
		background: var(--color-primary-500);
		border-radius: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #ffffff;
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

	.header-stats {
		display: flex;
		gap: 1.5rem;
	}

	.stat-item {
		text-align: center;
	}

	.stat-value {
		display: block;
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-primary-500);
	}

	.stat-label {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Tabs */
	.tabs {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.tab {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.25rem;
		background: transparent;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		color: var(--color-text-manifest);
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.tab:hover {
		background: var(--color-field-depth);
	}

	.tab.active {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: white;
	}

	/* Upload section */
	.upload-section {
		margin-bottom: 2rem;
		min-height: 200px;
	}

	.drop-zone {
		border: 2px dashed var(--color-veil-soft);
		border-radius: 1rem;
		padding: 3rem 2rem;
		text-align: center;
		transition: all 0.2s ease;
		cursor: pointer;
		min-height: 180px;
	}

	.drop-zone:hover,
	.drop-zone.drag-over {
		border-color: var(--color-primary-400);
		background: var(--color-primary-50);
	}

	[data-theme='dark'] .drop-zone:hover,
	[data-theme='dark'] .drop-zone.drag-over {
		background: rgba(15, 23, 42, 0.1);
	}

	.drop-zone-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		cursor: pointer;
	}

	.drop-zone svg {
		color: var(--color-text-hint);
	}

	.drop-text {
		font-size: 1rem;
		font-weight: 500;
		color: var(--color-text-manifest);
	}

	.drop-hint {
		font-size: 0.8125rem;
		color: var(--color-text-hint);
	}

	.hidden {
		display: none;
	}

	/* Uploaded files */
	.uploaded-files {
		margin-top: 1.5rem;
		padding: 1.25rem;
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
	}

	.files-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.files-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.multi-file-badge {
		font-size: 0.6875rem;
		padding: 0.25rem 0.625rem;
		background: var(--color-success-100);
		color: var(--color-success-700);
		border-radius: 9999px;
		font-weight: 600;
	}

	[data-theme='dark'] .multi-file-badge {
		background: rgba(34, 197, 94, 0.15);
		color: var(--color-success-400);
	}

	.files-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.file-chip {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
		font-size: 0.8125rem;
	}

	.file-chip svg {
		color: var(--color-primary-500);
	}

	.file-name {
		color: var(--color-text-manifest);
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.remove-file {
		background: none;
		border: none;
		padding: 0.125rem;
		cursor: pointer;
		color: var(--color-text-hint);
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 0.25rem;
	}

	.remove-file:hover {
		color: var(--color-error-500);
		background: var(--color-error-50);
	}

	.discover-actions {
		margin-top: 1rem;
		display: flex;
		justify-content: flex-end;
	}

	/* Goals section */
	.goals-section {
		margin-top: 2rem;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.section-header h2 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.clear-btn {
		background: none;
		border: none;
		color: var(--color-text-hint);
		font-size: 0.8125rem;
		cursor: pointer;
		padding: 0.375rem 0.75rem;
		border-radius: 0.375rem;
	}

	.clear-btn:hover {
		color: var(--color-error-500);
		background: var(--color-error-50);
	}

	.goals-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.25rem;
	}

	.goal-card {
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		min-height: 220px;
	}

	.goal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.goal-type {
		font-size: 0.6875rem;
		font-weight: 600;
		padding: 0.25rem 0.625rem;
		border-radius: 9999px;
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}

	.goal-confidence {
		font-size: 0.8125rem;
		font-weight: 600;
	}

	.goal-identity {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		line-height: 1.4;
	}

	.goal-first-move {
		font-size: 0.875rem;
		color: var(--color-text-manifest);
		line-height: 1.5;
	}

	.goal-sources {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.source-badge {
		font-size: 0.6875rem;
		padding: 0.125rem 0.5rem;
		background: var(--color-field-depth);
		color: var(--color-text-whisper);
		border-radius: 0.25rem;
	}

	.goal-actions {
		display: flex;
		gap: 0.5rem;
		margin-top: 0.5rem;
		padding-top: 0.75rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	.action-btn {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.375rem;
		padding: 0.5rem 0.75rem;
		border-radius: 0.5rem;
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.save-btn {
		background: var(--color-success-50);
		border: 1px solid var(--color-success-200);
		color: var(--color-success-700);
	}

	.save-btn:hover:not(:disabled) {
		background: var(--color-success-100);
	}

	.save-btn:disabled {
		opacity: 0.7;
		cursor: default;
	}

	.chat-btn {
		background: var(--color-primary-500);
		border: none;
		color: white;
	}

	.chat-btn:hover {
		background: var(--color-primary-600);
	}

	.remove-btn {
		background: transparent;
		border: 1px solid var(--color-veil-soft);
		color: var(--color-text-whisper);
	}

	.remove-btn:hover {
		border-color: var(--color-error-400);
		color: var(--color-error-500);
		background: var(--color-error-50);
	}

	/* Loading and empty states */
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

	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
		background: var(--color-field-surface);
		border-radius: 1rem;
		border: 1px dashed var(--color-veil-soft);
	}

	.empty-icon {
		margin: 0 auto 1.5rem;
		width: 80px;
		height: 80px;
		background: var(--color-field-depth);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-text-hint);
	}

	.empty-state h3 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.empty-state p {
		color: var(--color-text-whisper);
		font-size: 0.875rem;
		margin-bottom: 1.5rem;
	}

	/* Tablet responsive */
	@media (max-width: 1200px) {
		.goals-page {
			padding: 1.5rem 2rem;
		}

		.goals-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	/* Mobile responsive */
	@media (max-width: 900px) {
		.goals-page {
			padding: 1rem;
		}

		.page-header {
			flex-direction: column;
			gap: 1rem;
		}

		.header-stats {
			width: 100%;
			justify-content: flex-start;
		}

		.tabs {
			flex-direction: column;
		}

		.goals-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
