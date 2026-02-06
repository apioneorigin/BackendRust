<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { addToast, chat, llmManualBusy } from '$lib/stores';
	import { Button, Spinner, ConfirmDialog } from '$lib/components/ui';
	import { api } from '$lib/utils/api';

	interface DiscoveredGoal {
		id: string;
		type: string;
		identity: string;
		firstMove: string;
		first_move?: string;
		confidence: number;
		sourceFiles?: string[];
		source_files?: string[];
		createdAt?: string;
		created_at?: string;
		addedToInventory?: boolean;
	}

	interface SavedGoal extends DiscoveredGoal {
		savedAt: string;
	}

	interface FileGoalDiscovery {
		id: string;
		fileNames: string[];
		fileCount: number;
		fileSummary: string;
		goals: DiscoveredGoal[];
		goalCount: number;
		createdAt: string;
	}

	interface UploadedFile {
		name: string;
		content: string;
		type: string;
		encoding: 'text' | 'base64';
	}

	const TEXT_EXTENSIONS = new Set(['.txt', '.md', '.json', '.csv']);
	const BINARY_EXTENSIONS = new Set(['.docx', '.pptx', '.xlsx', '.jpg', '.jpeg', '.png', '.zip']);

	function getFileExtension(filename: string): string {
		const dot = filename.lastIndexOf('.');
		return dot >= 0 ? filename.slice(dot).toLowerCase() : '';
	}

	let uploadedFiles: UploadedFile[] = [];
	let discoveries: FileGoalDiscovery[] = [];
	let savedGoals: SavedGoal[] = [];
	let isDiscovering = false;
	let isLoading = true;
	let activeTab: 'discover' | 'saved' = 'discover';
	let dragOver = false;
	let webSearchEnabled = true; // Web search enriches signals with real-world data

	// Modal state
	let showGoalsModal = false;
	let modalDiscovery: FileGoalDiscovery | null = null;
	let goalsSavedDuringModal = false;
	let flashLibraryTab = false;
	let modalPage = 0;
	const GOALS_PER_PAGE = 6;

	$: modalGoals = modalDiscovery?.goals ?? [];
	$: totalModalPages = Math.ceil(modalGoals.length / GOALS_PER_PAGE);
	$: visibleGoals = modalGoals.slice(modalPage * GOALS_PER_PAGE, (modalPage + 1) * GOALS_PER_PAGE);

	// Discovery row dropdown state
	let activeDiscoveryMenu: string | null = null;

	// Delete confirmation state
	let showDeleteDiscoveryConfirm = false;
	let deleteDiscoveryId: string | null = null;
	let showRemoveGoalConfirm = false;
	let removeGoalId: string | null = null;
	let showDeleteGoalFromDiscoveryConfirm = false;
	let deleteGoalFromDiscoveryInfo: { discoveryId: string; goalId: string } | null = null;

	const goalTypeColors: Record<string, string> = {
		OPTIMIZE: 'type-action',
		BUILD: 'type-action',
		LEVERAGE: 'type-action',
		DISCOVER: 'type-insight',
		HIDDEN: 'type-insight',
		QUANTUM: 'type-insight',
		TRANSFORM: 'type-change',
		RESOLVE: 'type-change',
		RELEASE: 'type-change',
		PROTECT: 'type-shield',
		ALIGN: 'type-shield',
		INTEGRATION: 'type-systems',
		DIFFERENTIATION: 'type-systems',
		ANTI_SILOING: 'type-systems',
		SYNTHESIS: 'type-systems',
		RECONCILIATION: 'type-systems',
		ARBITRAGE: 'type-systems'
	};

	onMount(async () => {
		await Promise.all([loadDiscoveries(), loadSavedGoals()]);
	});

	function toggleDiscoveryMenu(e: Event, discoveryId: string) {
		e.stopPropagation();
		activeDiscoveryMenu = activeDiscoveryMenu === discoveryId ? null : discoveryId;
	}

	function closeDiscoveryMenus() {
		activeDiscoveryMenu = null;
	}

	async function shareDiscovery(e: Event, discoveryId: string) {
		e.stopPropagation();
		activeDiscoveryMenu = null;
		try {
			const url = `${window.location.origin}/goals?discovery=${discoveryId}`;
			await navigator.clipboard.writeText(url);
			addToast('success', 'Link copied to clipboard');
		} catch {
			addToast('error', 'Failed to copy link');
		}
	}

	async function loadDiscoveries() {
		try {
			const data = await api.get<{ discoveries: FileGoalDiscovery[] }>('/api/goal-discoveries');
			discoveries = data.discoveries || [];
		} catch (error) {
			console.error('Failed to load discoveries:', error);
		} finally {
			isLoading = false;
		}
	}

	async function loadSavedGoals() {
		try {
			const data = await api.get<{ goals: SavedGoal[] }>('/api/goal-inventory/list');
			savedGoals = data.goals || [];
		} catch (error) {
			console.error('Failed to load saved goals:', error);
		}
	}

	async function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files) {
			await processFiles(Array.from(input.files));
		}
		// Reset input so same file can be re-selected
		input.value = '';
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
			if (uploadedFiles.some((f) => f.name === file.name)) continue;
			try {
				const ext = getFileExtension(file.name);
				const isBinary = BINARY_EXTENSIONS.has(ext);
				const content = isBinary ? await readFileAsBase64(file) : await readFileAsText(file);
				uploadedFiles = [
					...uploadedFiles,
					{
						name: file.name,
						content,
						type: file.type || 'text/plain',
						encoding: isBinary ? 'base64' : 'text'
					}
				];
			} catch (error) {
				addToast('error', `Failed to read ${file.name}`);
			}
		}
	}

	async function readFileAsText(file: File): Promise<string> {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = () => resolve(reader.result as string);
			reader.onerror = reject;
			reader.readAsText(file);
		});
	}

	async function readFileAsBase64(file: File): Promise<string> {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = () => {
				const result = reader.result as string;
				// Strip "data:...;base64," prefix — backend expects raw base64
				const base64 = result.includes(',') ? result.split(',')[1] : result;
				resolve(base64);
			};
			reader.onerror = reject;
			reader.readAsDataURL(file);
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
		llmManualBusy.set(true);
		try {
			await api.post('/api/goals/discover-from-files', {
				files: uploadedFiles,
				existing_goals: [],
				web_search: webSearchEnabled
			}, { timeout: 300000 });
			addToast('success', 'Goals discovered and saved');
			uploadedFiles = [];
			// Reload the persisted discoveries
			await loadDiscoveries();
			// Auto-show the goals modal for the newest discovery
			if (discoveries.length > 0) {
				openGoalsModal(discoveries[0]);
			}
		} catch (error: any) {
			addToast('error', error.message || 'Failed to discover goals');
		} finally {
			isDiscovering = false;
			llmManualBusy.set(false);
		}
	}

	function openGoalsModal(discovery: FileGoalDiscovery) {
		modalDiscovery = discovery;
		modalPage = 0;
		showGoalsModal = true;
		goalsSavedDuringModal = false;
	}

	function closeGoalsModal() {
		showGoalsModal = false;
		modalDiscovery = null;
		if (goalsSavedDuringModal) {
			flashLibraryTab = true;
			setTimeout(() => { flashLibraryTab = false; }, 5000);
		}
	}

	function deleteDiscovery(discoveryId: string) {
		deleteDiscoveryId = discoveryId;
		showDeleteDiscoveryConfirm = true;
	}

	async function confirmDeleteDiscovery() {
		if (!deleteDiscoveryId) return;
		try {
			await api.delete(`/api/goal-discoveries/${deleteDiscoveryId}`);
			discoveries = discoveries.filter((d) => d.id !== deleteDiscoveryId);
			addToast('success', 'Discovery removed');
		} catch (error) {
			addToast('error', 'Failed to remove discovery');
		} finally {
			deleteDiscoveryId = null;
		}
	}

	function cancelDeleteDiscovery() {
		deleteDiscoveryId = null;
	}

	function normalizeGoal(goal: DiscoveredGoal): DiscoveredGoal {
		return {
			...goal,
			firstMove: goal.firstMove || goal.first_move || '',
			sourceFiles: goal.sourceFiles || goal.source_files || [],
			createdAt: goal.createdAt || goal.created_at || ''
		};
	}

	async function saveGoalToInventory(goal: DiscoveredGoal) {
		const g = normalizeGoal(goal);
		const savedGoal: SavedGoal = {
			...g,
			savedAt: new Date().toISOString(),
			addedToInventory: true
		};

		savedGoals = [...savedGoals, savedGoal];
		try {
			await api.post('/api/goal-inventory/save', { goals: savedGoals });
			goalsSavedDuringModal = true;
			addToast('success', 'Goal saved to library');
		} catch (error) {
			addToast('error', 'Failed to save goal');
		}
	}

	function removeFromInventory(goalId: string) {
		removeGoalId = goalId;
		showRemoveGoalConfirm = true;
	}

	async function confirmRemoveFromInventory() {
		if (!removeGoalId) return;
		const updatedGoals = savedGoals.filter((g) => g.id !== removeGoalId);
		try {
			await api.post('/api/goal-inventory/save', { goals: updatedGoals });
			savedGoals = updatedGoals;
			addToast('success', 'Goal removed from library');
		} catch (error) {
			addToast('error', 'Failed to remove goal');
		} finally {
			removeGoalId = null;
		}
	}

	function cancelRemoveFromInventory() {
		removeGoalId = null;
	}

	function deleteGoalFromDiscovery(goalId: string) {
		if (!modalDiscovery) return;
		deleteGoalFromDiscoveryInfo = { discoveryId: modalDiscovery.id, goalId };
		showDeleteGoalFromDiscoveryConfirm = true;
	}

	async function confirmDeleteGoalFromDiscovery() {
		if (!deleteGoalFromDiscoveryInfo) return;
		const { discoveryId, goalId } = deleteGoalFromDiscoveryInfo;
		try {
			await api.delete(`/api/goal-discoveries/${discoveryId}/goals/${goalId}`);
			// Update local state
			const disc = discoveries.find((d) => d.id === discoveryId);
			if (disc) {
				disc.goals = disc.goals.filter((g) => g.id !== goalId);
				disc.goalCount = disc.goals.length;
				if (disc.goals.length === 0) {
					discoveries = discoveries.filter((d) => d.id !== discoveryId);
					closeGoalsModal();
				} else {
					discoveries = [...discoveries];
					if (modalDiscovery && modalDiscovery.id === discoveryId) {
						modalDiscovery = { ...disc };
					}
				}
			}
			addToast('success', 'Goal removed');
		} catch (error) {
			addToast('error', 'Failed to remove goal');
		} finally {
			deleteGoalFromDiscoveryInfo = null;
		}
	}

	function cancelDeleteGoalFromDiscovery() {
		deleteGoalFromDiscoveryInfo = null;
	}

	async function startChatWithGoal(goal: DiscoveredGoal | SavedGoal) {
		const g = normalizeGoal(goal);
		try {
			const conversation = await api.post<{ id: string }>('/api/chat/conversations', {
				title: g.identity,
				context: `Goal: ${g.identity}\n\nFirst Move: ${g.firstMove}\n\nType: ${g.type}\nConfidence: ${g.confidence}%`
			});
			await chat.loadConversations();
			goto(`/chat`);
			await chat.selectConversation(conversation.id);
		} catch (error) {
			addToast('error', 'Failed to create chat');
		}
	}

	function isGoalSaved(goalId: string): boolean {
		return savedGoals.some((g) => g.id === goalId);
	}

	function getConfidenceColor(confidence: number): string {
		if (confidence >= 90) return 'confidence-high';
		if (confidence >= 70) return 'confidence-good';
		if (confidence >= 50) return 'confidence-medium';
		return 'confidence-low';
	}

	function formatDate(dateStr: string): string {
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Goal Discovery | Reality Transformer</title>
</svelte:head>

<div class="goals-page">
	<!-- Page header -->
	<header class="page-header">
		<div class="header-left">
			<div class="header-icon">
				<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="10" />
					<circle cx="12" cy="12" r="6" />
					<circle cx="12" cy="12" r="2" />
				</svg>
			</div>
			<div>
				<h1>Goal Discovery</h1>
				<p class="subtitle">Upload files to discover actionable goals</p>
			</div>
		</div>
		<div class="header-stats">
			<div class="stat-item">
				<span class="stat-value">{discoveries.length}</span>
				<span class="stat-label">Discoveries</span>
			</div>
			<div class="stat-item">
				<span class="stat-value">{discoveries.reduce((sum, d) => sum + d.goalCount, 0)}</span>
				<span class="stat-label">Goals Found</span>
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
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
			</svg>
			Discoveries
		</button>
		<button class="tab" class:active={activeTab === 'saved'} class:flash={flashLibraryTab} on:click={() => (activeTab = 'saved')}>
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
			</svg>
			My Library ({savedGoals.length})
		</button>
	</div>

	{#if activeTab === 'discover'}
		<!-- Upload bar -->
		<div
			class="upload-bar"
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
				accept=".txt,.md,.json,.csv,.docx,.pptx,.xlsx,.jpg,.jpeg,.png,.zip"
				on:change={handleFileSelect}
				class="hidden"
			/>
			<div class="upload-bar-left">
				{#if uploadedFiles.length > 0}
					<div class="staged-files">
						{#each uploadedFiles as file (file.name)}
							<span class="file-tag">
								<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
									<polyline points="14 2 14 8 20 8" />
								</svg>
								{file.name}
								<button class="file-tag-remove" on:click|stopPropagation={() => removeFile(file.name)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
										<path d="M18 6 6 18" /><path d="m6 6 12 12" />
									</svg>
								</button>
							</span>
						{/each}
					</div>
				{:else}
					<span class="upload-hint">
						{dragOver ? 'Drop files here' : 'Drag files here or click browse'}
					</span>
				{/if}
			</div>
			<div class="upload-bar-actions">
				<label for="file-input" class="browse-btn">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
						<polyline points="17 8 12 3 7 8" />
						<line x1="12" x2="12" y1="3" y2="15" />
					</svg>
					Browse
				</label>
				<label class="web-search-toggle" title="Enrich with real-world data: benchmarks, trends, comparables">
					<input type="checkbox" bind:checked={webSearchEnabled} />
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="12" cy="12" r="10" />
						<path d="M2 12h20" />
						<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
					</svg>
					<span>Web Search</span>
				</label>
				<button
					class="discover-btn"
					on:click={discoverGoals}
					disabled={isDiscovering || uploadedFiles.length === 0}
				>
					{#if isDiscovering}
						<Spinner size="sm" />
						{webSearchEnabled ? 'Researching...' : 'Analyzing...'}
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
						</svg>
						Discover Goals
					{/if}
				</button>
			</div>
		</div>

		<!-- Discoveries list -->
		<section class="discoveries-section">
			{#if isLoading}
				<div class="loading-state">
					<Spinner size="lg" />
					<p>Loading discoveries...</p>
				</div>
			{:else if discoveries.length === 0 && uploadedFiles.length === 0}
				<div class="empty-state">
					<div class="empty-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
							<circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
						</svg>
					</div>
					<h3>No discoveries yet</h3>
					<p>Upload files above to discover goals from your data</p>
				</div>
			{:else}
				<!-- svelte-ignore a11y-click-events-have-key-events -->
				<div class="discoveries-list" on:click={closeDiscoveryMenus}>
					{#each discoveries as discovery (discovery.id)}
						<div class="discovery-row" on:click={() => openGoalsModal(discovery)} role="button" tabindex="0" on:keydown={(e) => e.key === 'Enter' && openGoalsModal(discovery)}>
							<span class="discovery-title">
								<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
									<polyline points="14 2 14 8 20 8" />
								</svg>
								{discovery.fileNames.join(', ')}
								<span class="discovery-goal-count">{discovery.goalCount} goals</span>
								{#if discovery.fileSummary}
									<span class="discovery-summary">{discovery.fileSummary}</span>
								{/if}
							</span>
							<button class="discovery-options-btn" on:click|stopPropagation={(e) => toggleDiscoveryMenu(e, discovery.id)} title="Options">
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="m6 9 6 6 6-6"/>
								</svg>
							</button>
							{#if activeDiscoveryMenu === discovery.id}
								<!-- svelte-ignore a11y-click-events-have-key-events -->
								<div class="discovery-dropdown" on:click|stopPropagation role="menu">
									<button class="dropdown-item" on:click={(e) => shareDiscovery(e, discovery.id)}>
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
											<polyline points="16 6 12 2 8 6"/>
											<line x1="12" x2="12" y1="2" y2="15"/>
										</svg>
										<span>Share link</span>
									</button>
									<button class="dropdown-item delete" on:click|stopPropagation={() => { activeDiscoveryMenu = null; deleteDiscovery(discovery.id); }}>
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M3 6h18"/>
											<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
											<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
										</svg>
										<span>Delete</span>
									</button>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</section>
	{:else}
		<!-- Saved goals (library) -->
		<section class="discoveries-section">
			{#if savedGoals.length === 0}
				<div class="empty-state">
					<div class="empty-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
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
						{@const g = normalizeGoal(goal)}
						<div class="goal-card">
							<div class="goal-header">
								<span class="goal-type {goalTypeColors[g.type] || 'type-default'}">
									{g.type.replace('_', ' ')}
								</span>
								<span class="goal-confidence {getConfidenceColor(g.confidence)}">
									{g.confidence}%<span class="confidence-label">confidence</span>
								</span>
							</div>
							<h3 class="goal-identity">{g.identity}</h3>
							<p class="goal-first-move">{g.firstMove}</p>
							<div class="goal-sources">
								{#each g.sourceFiles || [] as source}
									<span class="source-badge">{source}</span>
								{/each}
							</div>
							<div class="goal-actions">
								<button class="action-btn chat-btn" on:click={() => startChatWithGoal(g)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
									</svg>
									Start Chat
								</button>
								<button class="action-btn remove-btn" on:click={() => removeFromInventory(g.id)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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

<!-- Goals Modal -->
{#if showGoalsModal && modalDiscovery}
	<div class="modal-overlay" on:click={closeGoalsModal} on:keydown={(e) => e.key === 'Escape' && closeGoalsModal()} role="dialog" tabindex="-1">
		<div class="modal-content" on:click|stopPropagation role="document">
			<div class="modal-header">
				<div class="modal-header-row">
					<h2>Discovered Goals</h2>
					<span class="modal-header-sep">|</span>
					{#each modalDiscovery.fileNames as fileName}
						<span class="file-badge">{fileName}</span>
					{/each}
					<span class="modal-header-sep">|</span>
					<span class="modal-date">{formatDate(modalDiscovery.createdAt)}</span>
				</div>
				<button class="modal-close" on:click={closeGoalsModal}>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M18 6 6 18" /><path d="m6 6 12 12" />
					</svg>
				</button>
			</div>
			<div class="modal-body">
				<div class="modal-goals-grid">
					{#each visibleGoals as goal (goal.id)}
						{@const g = normalizeGoal(goal)}
						<div class="goal-card">
							<div class="goal-header">
								<span class="goal-type {goalTypeColors[g.type] || 'type-default'}">
									{g.type.replace('_', ' ')}
								</span>
								<span class="goal-confidence {getConfidenceColor(g.confidence)}">
									{g.confidence}%<span class="confidence-label">confidence</span>
								</span>
							</div>
							<h3 class="goal-identity">{g.identity}</h3>
							<p class="goal-first-move">{g.firstMove}</p>
							<div class="goal-actions">
								<button
									class="action-btn save-btn"
									on:click={() => saveGoalToInventory(g)}
									disabled={isGoalSaved(g.id)}
								>
									{#if isGoalSaved(g.id)}
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M20 6 9 17l-5-5" />
										</svg>
										Saved
									{:else}
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
										</svg>
										Save
									{/if}
								</button>
								<button class="action-btn chat-btn" on:click={() => startChatWithGoal(g)}>
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
									</svg>
									Chat
								</button>
								<button class="action-btn remove-btn" on:click={() => deleteGoalFromDiscovery(g.id)} title="Delete goal">
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M3 6h18" />
										<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
										<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
									</svg>
									Delete
								</button>
							</div>
						</div>
					{/each}
				</div>
			</div>
			{#if totalModalPages > 1}
				<div class="modal-footer">
					<button class="page-btn" disabled={modalPage === 0} on:click={() => modalPage--}>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
						Prev
					</button>
					<span class="page-info">{modalPage + 1} / {totalModalPages}</span>
					<button class="page-btn" disabled={modalPage >= totalModalPages - 1} on:click={() => modalPage++}>
						Next
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
					</button>
				</div>
			{/if}
		</div>
	</div>
{/if}

<ConfirmDialog
	bind:open={showDeleteDiscoveryConfirm}
	title="Delete Discovery"
	message="Are you sure you want to delete this discovery? All discovered goals from this batch will be removed."
	confirmText="Delete"
	variant="danger"
	on:confirm={confirmDeleteDiscovery}
	on:cancel={cancelDeleteDiscovery}
/>

<ConfirmDialog
	bind:open={showRemoveGoalConfirm}
	title="Remove from Library"
	message="Are you sure you want to remove this goal from your library?"
	confirmText="Remove"
	variant="danger"
	on:confirm={confirmRemoveFromInventory}
	on:cancel={cancelRemoveFromInventory}
/>

<ConfirmDialog
	bind:open={showDeleteGoalFromDiscoveryConfirm}
	title="Delete Goal"
	message="Are you sure you want to delete this goal from the discovery?"
	confirmText="Delete"
	variant="danger"
	on:confirm={confirmDeleteGoalFromDiscovery}
	on:cancel={cancelDeleteGoalFromDiscovery}
/>

<style>
	.goals-page {
		padding: 1.5rem 2rem;
		width: 100%;
		height: 100%;
		overflow-y: auto;
		overflow-x: hidden;
		box-sizing: border-box;
		animation: fadeIn 0.2s ease;
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	/* Page header */
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.25rem;
		padding-bottom: 1.25rem;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.header-left {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.header-icon {
		width: 40px;
		height: 40px;
		background: var(--color-primary-500);
		border-radius: 0.625rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #ffffff;
		flex-shrink: 0;
	}

	.page-header h1 {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.125rem;
	}

	.subtitle {
		color: var(--color-text-whisper);
		font-size: 0.8125rem;
	}

	.header-stats {
		display: flex;
		gap: 1.25rem;
	}

	.stat-item {
		text-align: center;
	}

	.stat-value {
		display: block;
		font-size: 1.125rem;
		font-weight: 700;
		color: var(--color-primary-500);
	}

	.stat-label {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}

	/* Tabs */
	.tabs {
		display: flex;
		gap: 0.375rem;
		margin-bottom: 1rem;
	}

	.tab {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 1rem;
		background: transparent;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		color: var(--color-text-manifest);
		font-size: 0.8125rem;
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

	@keyframes flashPulse {
		0%, 100% {
			background: var(--color-primary-100);
			box-shadow: 0 0 0 2px var(--color-primary-300);
			transform: scale(1);
		}
		50% {
			background: var(--color-primary-300);
			box-shadow: 0 0 12px 4px var(--color-primary-400);
			transform: scale(1.07);
		}
	}

	.tab.flash {
		animation: flashPulse 0.8s ease 5;
		border-color: var(--color-primary-500);
		color: var(--color-primary-700);
		background: var(--color-primary-100);
		font-weight: 700;
	}

	/* Upload bar */
	.upload-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.625rem 0.75rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		margin-bottom: 1.25rem;
		gap: 0.75rem;
		transition: border-color 0.15s ease, background 0.15s ease;
		min-height: 44px;
	}

	.upload-bar.drag-over {
		border-color: var(--color-primary-400);
		background: var(--color-primary-50);
	}

	.upload-bar-left {
		flex: 1;
		min-width: 0;
		overflow: hidden;
	}

	.upload-hint {
		font-size: 0.8125rem;
		color: var(--color-text-hint);
	}

	.staged-files {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.file-tag {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.5rem;
		background: var(--color-field-depth);
		border-radius: 0.25rem;
		font-size: 0.75rem;
		color: var(--color-text-manifest);
	}

	.file-tag svg {
		color: var(--color-primary-500);
		flex-shrink: 0;
	}

	.file-tag-remove {
		background: none;
		border: none;
		padding: 0.125rem;
		cursor: pointer;
		color: var(--color-text-hint);
		display: flex;
		align-items: center;
		border-radius: 2px;
		margin-left: 0.125rem;
	}

	.file-tag-remove:hover {
		color: var(--color-error-500);
		background: var(--color-error-50);
	}

	.upload-bar-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	.browse-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-soft);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.browse-btn:hover {
		background: var(--color-veil-thin);
	}

	.discover-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.875rem;
		background: var(--color-primary-500);
		border: none;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 600;
		color: white;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.discover-btn:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.discover-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Web search toggle - visible checkbox */
	.web-search-toggle {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.625rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-soft);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.15s ease;
		user-select: none;
	}

	.web-search-toggle:hover {
		background: var(--color-veil-thin);
	}

	.web-search-toggle input[type="checkbox"] {
		width: 14px;
		height: 14px;
		margin: 0;
		cursor: pointer;
		accent-color: var(--color-primary-500);
		flex-shrink: 0;
	}

	.web-search-toggle:has(input:checked) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
		color: var(--color-primary-600);
	}

	.web-search-toggle:has(input:checked) svg {
		color: var(--color-primary-500);
	}

	.web-search-toggle svg {
		color: var(--color-text-whisper);
		transition: color 0.15s ease;
	}

	.hidden {
		display: none;
	}

	/* Discoveries section */
	.discoveries-section {
		flex: 1;
	}

	.discoveries-list {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.discovery-row {
		position: relative;
		display: flex;
		align-items: center;
		padding: 0.5rem 0.625rem;
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.discovery-row:hover {
		background: var(--color-accent-subtle, var(--color-field-depth));
	}

	.discovery-title {
		flex: 1;
		min-width: 0;
		display: flex;
		align-items: center;
		gap: 0.375rem;
		font-size: 13px;
		font-weight: 400;
		color: var(--color-text-manifest);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.discovery-row:hover .discovery-title {
		color: var(--color-text-source);
	}

	.discovery-title svg {
		color: var(--color-primary-500);
		flex-shrink: 0;
	}

	.discovery-goal-count {
		color: var(--color-text-whisper);
		font-size: 12px;
		flex-shrink: 0;
	}

	.discovery-summary {
		color: var(--color-text-hint);
		font-size: 12px;
		font-style: italic;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		min-width: 0;
	}

	.discovery-options-btn {
		position: absolute;
		right: 0.625rem;
		opacity: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		padding: 0;
		background: var(--color-field-surface);
		border: none;
		border-radius: 0.25rem;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: opacity 0.1s ease;
	}

	.discovery-row:hover .discovery-options-btn {
		opacity: 1;
	}

	.discovery-options-btn:hover {
		background: var(--color-veil-present, var(--color-field-depth));
		color: var(--color-text-source);
	}

	.discovery-dropdown {
		position: absolute;
		top: 100%;
		right: 0;
		z-index: 50;
		min-width: 140px;
		padding: 0.25rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		box-shadow: var(--shadow-elevated);
	}

	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.5rem 0.625rem;
		background: transparent;
		border: none;
		border-radius: 0.25rem;
		font-size: 13px;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.1s ease;
		text-align: left;
	}

	.dropdown-item:hover {
		background: var(--color-accent-subtle, var(--color-field-depth));
		color: var(--color-text-source);
	}

	.dropdown-item.delete:hover {
		background: var(--color-error-50);
		color: var(--color-error-500);
	}

	.dropdown-item svg {
		flex-shrink: 0;
	}

	/* Goals grid (used in library) */
	.goals-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 1rem;
	}

	/* Modal goals grid - exactly 6 goals visible (2 rows x 3 cols), no scroll */
	.modal-goals-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		grid-template-rows: 1fr 1fr;
		gap: 0.75rem;
		height: 100%;
		overflow: hidden;
	}

	.modal-goals-grid .goal-card {
		padding: 1rem;
		gap: 0.5rem;
		overflow: hidden;
	}

	.modal-goals-grid .goal-actions {
		padding-top: 0.5rem;
	}

	.goal-card {
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.625rem;
		background: var(--color-field-surface);
		box-shadow: var(--shadow-elevated);
		border-radius: 0.625rem;
		border: 1px solid var(--color-veil-thin);
	}

	.goal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.goal-type {
		font-size: 0.625rem;
		font-weight: 500;
		padding: 0.1875rem 0.5rem;
		border-radius: 9999px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.goal-confidence {
		font-size: 0.75rem;
		font-weight: 600;
		display: flex;
		align-items: baseline;
		gap: 0.25rem;
	}

	.confidence-label {
		font-size: 0.625rem;
		font-weight: 400;
		opacity: 0.6;
		text-transform: lowercase;
	}

	/* Confidence colors */
	.confidence-high { color: #16a34a; }
	.confidence-good { color: #2563eb; }
	.confidence-medium { color: #ca8a04; }
	.confidence-low { color: #dc2626; }

	/* Goal type colors — 5 semantic groups */
	.type-action { background: #f1f5f9; color: #475569; }
	.type-insight { background: #eef2ff; color: #3730a3; }
	.type-change { background: #fefce8; color: #854d0e; }
	.type-shield { background: #ecfdf5; color: #065f46; }
	.type-systems { background: #f0fdfa; color: #115e59; }
	.type-default { background: #f9fafb; color: #6b7280; }

	.goal-identity {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text-source);
		line-height: 1.4;
	}

	.goal-first-move {
		font-size: 0.8125rem;
		color: var(--color-text-manifest);
		line-height: 1.5;
		flex: 1;
	}

	.goal-sources {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}

	.source-badge {
		font-size: 0.625rem;
		padding: 0.125rem 0.375rem;
		background: var(--color-field-depth);
		color: var(--color-text-whisper);
		border-radius: 0.1875rem;
	}

	.goal-actions {
		display: flex;
		gap: 0.375rem;
		margin-top: auto;
		padding-top: 0.625rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	.action-btn {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.25rem;
		padding: 0.4375rem 0.625rem;
		border-radius: 0.375rem;
		font-size: 0.75rem;
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
		padding: 3rem 2rem;
		gap: 0.75rem;
	}

	.loading-state p {
		color: var(--color-text-whisper);
		font-size: 0.8125rem;
	}

	.empty-state {
		text-align: center;
		padding: 3rem 2rem;
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px dashed var(--color-veil-soft);
	}

	.empty-icon {
		margin: 0 auto 1rem;
		width: 64px;
		height: 64px;
		background: var(--color-field-depth);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-text-hint);
	}

	.empty-state h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.375rem;
	}

	.empty-state p {
		color: var(--color-text-whisper);
		font-size: 0.8125rem;
		margin-bottom: 1.25rem;
	}

	/* Modal */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 0.75rem;
		animation: fadeIn 0.15s ease;
	}

	.modal-content {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		width: 100%;
		max-width: 1200px;
		height: 96vh;
		display: flex;
		flex-direction: column;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		border: 1px solid var(--color-veil-thin);
	}

	.modal-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.modal-header-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex: 1;
		min-width: 0;
	}

	.modal-header-row h2 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-source);
		white-space: nowrap;
		margin: 0;
	}

	.modal-header-sep {
		color: var(--color-veil-soft);
		font-size: 0.875rem;
		flex-shrink: 0;
	}

	.file-badge {
		font-size: 0.75rem;
		padding: 0.125rem 0.5rem;
		background: var(--color-field-depth);
		color: var(--color-text-manifest);
		border-radius: 0.25rem;
		white-space: nowrap;
	}

	.modal-date {
		color: var(--color-text-hint);
		font-size: 0.75rem;
		white-space: nowrap;
	}

	.modal-close {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-text-hint);
		padding: 0.25rem;
		border-radius: 0.25rem;
		display: flex;
		align-items: center;
		transition: all 0.15s ease;
	}

	.modal-close:hover {
		color: var(--color-text-source);
		background: var(--color-field-depth);
	}

	.modal-body {
		padding: 0.75rem 1rem;
		overflow: hidden;
		flex: 1;
		min-height: 0;
	}

	.modal-footer {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		padding: 0.5rem 1rem;
		border-top: 1px solid var(--color-veil-thin);
		flex-shrink: 0;
	}

	.page-btn {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.75rem;
		background: transparent;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.page-btn:hover:not(:disabled) {
		background: var(--color-field-depth);
		border-color: var(--color-veil-soft);
	}

	.page-btn:disabled {
		opacity: 0.3;
		cursor: default;
	}

	.page-info {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Responsive */
	@media (max-width: 1200px) {
		.goals-grid {
			grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		}

		.modal-goals-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (max-width: 768px) {
		.goals-page {
			padding: 1rem;
		}

		.page-header {
			flex-direction: column;
			gap: 0.75rem;
			align-items: flex-start;
		}

		.header-stats {
			width: 100%;
			justify-content: flex-start;
		}

		.upload-bar {
			flex-direction: column;
			align-items: stretch;
			gap: 0.5rem;
		}

		.upload-bar-actions {
			justify-content: flex-end;
		}

		.goals-grid {
			grid-template-columns: 1fr;
		}

		.modal-goals-grid {
			grid-template-columns: 1fr;
		}

		.modal-content {
			max-width: 100%;
			max-height: 90vh;
		}

		.modal-overlay {
			padding: 1rem;
		}
	}
</style>
