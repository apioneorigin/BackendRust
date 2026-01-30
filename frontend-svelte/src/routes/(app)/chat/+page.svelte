<script lang="ts">
	/**
	 * Unified Chat Page - 4-Box Desktop Layout
	 *
	 * Layout:
	 * ┌─────────┬────────────────────────────────────────────┐
	 * │         │  Response Container (80%)  │  Matrix 5x5   │
	 * │ Sidebar │                            │    (50%)      │
	 * │ (conv)  │                            │               │
	 * │         ├────────────────────────────┼───────────────┤
	 * │         │  Input Panel (20%)         │  Live Preview │
	 * │         │  [📎][Causation][Effect]→  │    (50%)      │
	 * └─────────┴────────────────────────────┴───────────────┘
	 */

	import { onMount, onDestroy, tick } from 'svelte';
	import {
		chat,
		messages,
		currentConversation,
		conversations,
		isStreaming,
		streamingContent,
		addToast,
		user,
		matrix,
		matrixData as matrixDataStore,
		rowHeaders as rowHeadersStore,
		columnHeaders as columnHeadersStore,
		isMatrixGenerated,
		showRiskHeatmap as showRiskHeatmapStore,
		coherence as coherenceStore,
		population as populationStore,
		avgScore as avgScoreStore,
		powerSpots as powerSpotsStore
	} from '$lib/stores';
	import { Button, Spinner, TypingIndicator } from '$lib/components/ui';
	import MatrixPanel from '$lib/components/matrix/MatrixPanel.svelte';
	import LivePreviewBox from '$lib/components/matrix/LivePreviewBox.svelte';
	import MatrixToolbar from '$lib/components/matrix/MatrixToolbar.svelte';
	import CausationPopup from '$lib/components/matrix/CausationPopup.svelte';
	import EffectPopup from '$lib/components/matrix/EffectPopup.svelte';

	// Chat state
	let messageInput = '';
	let messagesContainer: HTMLElement;
	let inputElement: HTMLTextAreaElement;
	let fileInputElement: HTMLInputElement;
	let selectedModel = 'gpt-4.1';
	let attachedFiles: File[] = [];
	let isDragging = false;
	let placeholderIndex = 0;
	let placeholderInterval: ReturnType<typeof setInterval>;

	// Popup state
	let showCausationPopup = false;
	let showEffectPopup = false;
	let activeToolbarPopup: 'powerSpots' | 'plays' | 'scenarios' | 'sensitivity' | 'risk' | null = null;

	// Rotating placeholder prompts
	const PLACEHOLDERS = [
		"What's on your mind?",
		"I'll help you understand the why, not just the what...",
		"Share your thoughts, upload a file, or both...",
		"I'll surface what you're really after...",
		"Let's map what connects everything..."
	];

	const models = [
		{ id: 'gpt-4.1', name: 'GPT-4.1' },
		{ id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini' },
		{ id: 'gpt-4.5-preview', name: 'GPT-4.5 Preview' },
		{ id: 'claude-sonnet-4-20250514', name: 'Claude Sonnet 4' },
		{ id: 'claude-opus-4-20250514', name: 'Claude Opus 4' },
		{ id: 'o3', name: 'o3' },
		{ id: 'o4-mini', name: 'o4 Mini' }
	];

	// Get time-based greeting
	function getGreeting(): string {
		const hour = new Date().getHours();
		const firstName = $user?.name?.trim().split(/\s+/)[0] || '';
		const nameStr = firstName ? `, ${firstName}` : '';

		if (hour >= 5 && hour < 12) {
			return `Good morning${nameStr}`;
		} else if (hour >= 12 && hour < 17) {
			return `Good afternoon${nameStr}`;
		} else {
			return `Good evening${nameStr}`;
		}
	}

	$: greeting = getGreeting();

	onMount(async () => {
		await chat.loadConversations();

		// Rotate placeholder every 3 seconds
		placeholderInterval = setInterval(() => {
			placeholderIndex = (placeholderIndex + 1) % PLACEHOLDERS.length;
		}, 3000);

		// Initialize matrix with sample data (will be replaced by auto-generation)
		matrix.initializeMatrix();
	});

	onDestroy(() => {
		if (placeholderInterval) {
			clearInterval(placeholderInterval);
		}
	});

	// Auto-scroll when new messages or streaming
	$: if (($messages.length > 0 || $streamingContent) && messagesContainer) {
		tick().then(() => {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		});
	}

	async function handleSendMessage() {
		if ((!messageInput.trim() && attachedFiles.length === 0) || $isStreaming) return;

		const content = messageInput.trim();
		const files = [...attachedFiles];
		messageInput = '';
		attachedFiles = [];

		if (inputElement) {
			inputElement.style.height = 'auto';
		}

		try {
			await chat.sendMessage(content, selectedModel, files);
		} catch (error: any) {
			addToast('error', error.message || 'Failed to send message');
		}
	}

	async function handleNewChat() {
		await chat.createConversation();
	}

	async function handleSelectConversation(conversationId: string) {
		await chat.selectConversation(conversationId);
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSendMessage();
		}
	}

	function handleInput(e: Event) {
		const target = e.target as HTMLTextAreaElement;
		target.style.height = 'auto';
		target.style.height = Math.min(target.scrollHeight, 150) + 'px';
	}

	function stopGeneration() {
		chat.stopStreaming();
	}

	// File upload handlers
	function handleFileSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files) {
			addFiles(Array.from(target.files));
		}
		target.value = '';
	}

	function addFiles(files: File[]) {
		const validFiles = files.filter((file) => {
			if (file.size > 10 * 1024 * 1024) {
				addToast('error', `${file.name} exceeds 10MB limit`);
				return false;
			}
			if (attachedFiles.some((f) => f.name === file.name && f.size === file.size)) {
				return false;
			}
			return true;
		});
		attachedFiles = [...attachedFiles, ...validFiles];
	}

	function removeFile(index: number) {
		attachedFiles = attachedFiles.filter((_, i) => i !== index);
	}

	function triggerFileInput() {
		fileInputElement?.click();
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		if (e.dataTransfer?.files) {
			addFiles(Array.from(e.dataTransfer.files));
		}
	}

	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return bytes + ' B';
		if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
		return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
	}

	function getFileIcon(file: File): string {
		const type = file.type;
		if (type.startsWith('image/')) return '🖼️';
		if (type.startsWith('video/')) return '🎬';
		if (type.startsWith('audio/')) return '🎵';
		if (type.includes('pdf')) return '📄';
		if (type.includes('word') || type.includes('document')) return '📝';
		if (type.includes('sheet') || type.includes('excel')) return '📊';
		if (type.includes('presentation') || type.includes('powerpoint')) return '📽️';
		if (type.includes('zip') || type.includes('rar') || type.includes('7z')) return '📦';
		if (type.includes('text') || type.includes('json') || type.includes('xml')) return '📃';
		return '📎';
	}

	function formatTimestamp(date: Date | string) {
		const d = typeof date === 'string' ? new Date(date) : date;
		return new Intl.DateTimeFormat('en-US', {
			hour: 'numeric',
			minute: '2-digit',
			hour12: true
		}).format(d);
	}

	// Matrix handlers
	function handleCellClick(e: CustomEvent<{ row: number; col: number }>) {
		// Cell click handled by MatrixPanel internally
	}

	function handleCellChange(e: CustomEvent<{ row: number; col: number; value: number }>) {
		const { row, col, value } = e.detail;
		matrix.updateCellValue(row, col, value);
	}

	function handleToolbarPopup(e: CustomEvent<{ type: 'powerSpots' | 'plays' | 'scenarios' | 'sensitivity' | 'risk' }>) {
		activeToolbarPopup = e.detail.type;
	}

	function handleToggleRisk(e: CustomEvent<{ enabled: boolean }>) {
		matrix.toggleRiskHeatmap(e.detail.enabled);
	}

	function closeToolbarPopup() {
		activeToolbarPopup = null;
	}

	function handleCausationSubmit() {
		showCausationPopup = false;
	}

	function handleEffectSubmit() {
		showEffectPopup = false;
	}
</script>

<svelte:head>
	<title>Chat | Reality Transformer</title>
</svelte:head>

<div class="unified-layout">
	<!-- Conversation sidebar -->
	<aside class="sidebar">
		<div class="sidebar-header">
			<h3>Conversations</h3>
			<Button variant="primary" size="sm" on:click={handleNewChat}>
				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M12 5v14" />
					<path d="M5 12h14" />
				</svg>
				New
			</Button>
		</div>

		<div class="conversations-list">
			{#each $conversations as conversation (conversation.id)}
				<button
					class="conversation-item"
					class:active={$currentConversation?.id === conversation.id}
					on:click={() => handleSelectConversation(conversation.id)}
				>
					<span class="conversation-title">{conversation.title || 'New Conversation'}</span>
					<span class="conversation-time">{formatTimestamp(conversation.createdAt)}</span>
				</button>
			{/each}

			{#if $conversations.length === 0}
				<div class="empty-conversations">
					<p>No conversations yet</p>
					<p class="hint">Start a new chat to begin</p>
				</div>
			{/if}
		</div>
	</aside>

	<!-- Main content area (4 boxes) -->
	<main class="main-content">
		<!-- Left column: Chat (Response + Input) -->
		<div class="chat-column">
			<!-- Response container (80%) -->
			<div class="response-container" bind:this={messagesContainer}>
				{#if $messages.length === 0}
					<!-- Welcome screen -->
					<div class="welcome-screen">
						<div class="welcome-spacer"></div>
						<div class="welcome-greeting">
							<svg class="welcome-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
								<circle cx="50" cy="50" r="45" fill="#0f4c75" stroke="#3d93ce" stroke-width="4"/>
								<text x="50" y="72" font-family="'Product Sans', 'Roboto', sans-serif" font-size="55" font-weight="500" font-style="italic" fill="#FFFFFF" text-anchor="middle">G</text>
							</svg>
							<h1>{greeting}</h1>
						</div>
						<p class="welcome-subtitle">Your transformation map awaits on the right</p>
						<div class="welcome-spacer"></div>
					</div>
				{:else}
					<!-- Messages -->
					{#each $messages as message (message.id)}
						<div class="message" class:user={message.role === 'user'}>
							<div class="message-avatar" class:user-avatar={message.role === 'user'}>
								{#if message.role === 'user'}
									<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
										<circle cx="12" cy="7" r="4" />
									</svg>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M12 8V4H8" />
										<rect width="16" height="12" x="4" y="8" rx="2" />
										<path d="M2 14h2" />
										<path d="M20 14h2" />
										<path d="M15 13v2" />
										<path d="M9 13v2" />
									</svg>
								{/if}
							</div>
							<div class="message-content">
								<div class="message-header">
									<span class="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
									<span class="message-time">{formatTimestamp(message.createdAt)}</span>
								</div>
								<div class="message-bubble" class:bubble-user={message.role === 'user'} class:bubble-assistant={message.role === 'assistant'}>
									<div class="message-text">
										{@html message.content.replace(/\n/g, '<br>')}
									</div>
								</div>
							</div>
						</div>
					{/each}

					<!-- Streaming message -->
					{#if $isStreaming}
						<div class="message">
							<div class="message-avatar">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M12 8V4H8" />
									<rect width="16" height="12" x="4" y="8" rx="2" />
									<path d="M2 14h2" />
									<path d="M20 14h2" />
									<path d="M15 13v2" />
									<path d="M9 13v2" />
								</svg>
							</div>
							<div class="message-content">
								<div class="message-header">
									<span class="message-role">Assistant</span>
								</div>
								<div class="message-bubble bubble-assistant">
									{#if $streamingContent}
										<div class="message-text">
											{@html $streamingContent.replace(/\n/g, '<br>')}
										</div>
									{:else}
										<TypingIndicator />
									{/if}
								</div>
							</div>
						</div>
					{/if}
				{/if}
			</div>

			<!-- Input panel (20%) -->
			<div
				class="input-panel"
				on:dragover={handleDragOver}
				on:dragleave={handleDragLeave}
				on:drop={handleDrop}
				class:drag-over={isDragging}
				role="region"
			>
				<!-- Hidden file input -->
				<input
					type="file"
					bind:this={fileInputElement}
					on:change={handleFileSelect}
					multiple
					accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.json,.xml,.zip,.rar"
					class="hidden-input"
				/>

				<!-- Attached files -->
				{#if attachedFiles.length > 0}
					<div class="attached-files">
						{#each attachedFiles as file, index}
							<div class="file-chip">
								<span class="file-icon">{getFileIcon(file)}</span>
								<span class="file-name">{file.name}</span>
								<span class="file-size">{formatFileSize(file.size)}</span>
								<button class="remove-file" on:click={() => removeFile(index)} title="Remove file">
									<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M18 6 6 18" />
										<path d="m6 6 12 12" />
									</svg>
								</button>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Input row -->
				<div class="input-row">
					<textarea
						bind:this={inputElement}
						bind:value={messageInput}
						on:keydown={handleKeyDown}
						on:input={handleInput}
						placeholder={PLACEHOLDERS[placeholderIndex]}
						rows="1"
						disabled={$isStreaming}
					></textarea>
				</div>

				<!-- Controls row -->
				<div class="controls-row">
					<div class="controls-left">
						<button class="control-btn" on:click={triggerFileInput} disabled={$isStreaming} title="Attach files">
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
							</svg>
						</button>

						{#if $isMatrixGenerated}
							<button class="control-btn causation-btn" on:click={() => (showCausationPopup = true)} title="Select row dimensions">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M12 3v18"/>
									<path d="M5 9h14"/>
									<path d="M5 15h14"/>
								</svg>
								<span>Causation</span>
							</button>

							<button class="control-btn effect-btn" on:click={() => (showEffectPopup = true)} title="Select column dimensions">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M3 12h18"/>
									<path d="M9 5v14"/>
									<path d="M15 5v14"/>
								</svg>
								<span>Effect</span>
							</button>
						{/if}
					</div>

					<div class="controls-right">
						<select bind:value={selectedModel} class="model-select">
							{#each models as model}
								<option value={model.id}>{model.name}</option>
							{/each}
						</select>

						{#if $isStreaming}
							<button class="send-btn stop-btn" on:click={stopGeneration}>
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
									<rect x="6" y="6" width="12" height="12" rx="2" />
								</svg>
							</button>
						{:else}
							<button
								class="send-btn"
								on:click={handleSendMessage}
								disabled={(!messageInput.trim() && attachedFiles.length === 0)}
							>
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
									<path d="M22 2L11 13" />
									<path d="M22 2L15 22L11 13L2 9L22 2Z" />
								</svg>
							</button>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Right column: Matrix + Preview -->
		<div class="matrix-column">
			<!-- Matrix (50%) -->
			<div class="matrix-box">
				<MatrixPanel
					matrixData={$matrixDataStore}
					rowHeaders={$rowHeadersStore}
					columnHeaders={$columnHeadersStore}
					showRiskHeatmap={$showRiskHeatmapStore}
					compact={true}
					on:cellClick={handleCellClick}
					on:cellChange={handleCellChange}
				/>
			</div>

			<!-- Toolbar between matrix and preview -->
			<MatrixToolbar
				showRiskHeatmap={$showRiskHeatmapStore}
				on:openPopup={handleToolbarPopup}
				on:toggleRisk={handleToggleRisk}
			/>

			<!-- Live Preview (50%) -->
			<div class="preview-box">
				<LivePreviewBox
					coherence={$coherenceStore}
					balance={Math.round(($coherenceStore + $populationStore) / 2)}
					population={$populationStore}
					avgScore={$avgScoreStore}
					powerSpots={$powerSpotsStore}
					pendingChanges={0}
				/>
			</div>
		</div>
	</main>
</div>

<!-- Toolbar Popups -->
{#if activeToolbarPopup}
	<div class="popup-overlay" on:click={closeToolbarPopup} on:keydown={(e) => e.key === 'Escape' && closeToolbarPopup()} role="presentation" tabindex="-1">
		<div class="toolbar-popup" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true">
			<div class="popup-header">
				<h3>
					{#if activeToolbarPopup === 'powerSpots'}Power Spots
					{:else if activeToolbarPopup === 'plays'}Plays
					{:else if activeToolbarPopup === 'scenarios'}Scenarios Comparison
					{:else if activeToolbarPopup === 'sensitivity'}Sensitivity Analysis
					{:else if activeToolbarPopup === 'risk'}Risk View
					{/if}
				</h3>
				<button class="close-btn" on:click={closeToolbarPopup}>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M18 6 6 18" />
						<path d="m6 6 12 12" />
					</svg>
				</button>
			</div>
			<div class="popup-body">
				{#if activeToolbarPopup === 'powerSpots'}
					<p class="popup-description">Strategic points that create cascading positive effects</p>
					<div class="power-spots-list">
						{#each $matrixDataStore.flat().filter(c => c.isLeveragePoint) as _, idx}
							<div class="power-spot-item">
								<span class="spot-icon">⚡</span>
								<div class="spot-info">
									<span class="spot-title">Power Spot {idx + 1}</span>
									<span class="spot-desc">High impact cell for transformation</span>
								</div>
							</div>
						{/each}
					</div>
				{:else if activeToolbarPopup === 'plays'}
					<p class="popup-description">Pre-designed transformation strategies</p>
					<div class="plays-list">
						<div class="play-item">
							<span class="play-name">Rapid Progress</span>
							<span class="play-risk low">Low Risk</span>
						</div>
						<div class="play-item">
							<span class="play-name">Balanced Growth</span>
							<span class="play-risk medium">Medium Risk</span>
						</div>
						<div class="play-item">
							<span class="play-name">Deep Transformation</span>
							<span class="play-risk high">High Risk</span>
						</div>
					</div>
				{:else if activeToolbarPopup === 'scenarios'}
					<p class="popup-description">Compare different transformation scenarios</p>
					<div class="scenarios-placeholder">Scenarios comparison coming soon</div>
				{:else if activeToolbarPopup === 'sensitivity'}
					<p class="popup-description">Analyze factor sensitivity and variations</p>
					<div class="scenarios-placeholder">Sensitivity analysis coming soon</div>
				{:else if activeToolbarPopup === 'risk'}
					<p class="popup-description">Risk heatmap is {$showRiskHeatmapStore ? 'enabled' : 'disabled'}</p>
					<button class="toggle-risk-btn" on:click={() => matrix.toggleRiskHeatmap()}>
						{$showRiskHeatmapStore ? 'Disable' : 'Enable'} Risk Heatmap
					</button>
				{/if}
			</div>
		</div>
	</div>
{/if}

<!-- Causation Popup -->
<CausationPopup
	bind:open={showCausationPopup}
	on:close={() => (showCausationPopup = false)}
	on:submit={handleCausationSubmit}
/>

<!-- Effect Popup -->
<EffectPopup
	bind:open={showEffectPopup}
	on:close={() => (showEffectPopup = false)}
	on:submit={handleEffectSubmit}
/>

<style>
	/* Main unified layout */
	.unified-layout {
		display: flex;
		height: 100%;
		overflow: hidden;
	}

	/* Sidebar */
	.sidebar {
		width: 260px;
		min-width: 260px;
		background: var(--color-field-surface);
		border-right: 1px solid var(--color-veil-thin);
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem;
		border-bottom: 1px solid var(--color-veil-thin);
	}

	.sidebar-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.conversations-list {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.conversation-item {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 0.25rem;
		padding: 0.75rem;
		background: none;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background-color 0.15s ease;
		text-align: left;
	}

	.conversation-item:hover {
		background: var(--color-field-depth);
	}

	.conversation-item.active {
		background: var(--color-primary-100);
	}

	[data-theme='dark'] .conversation-item.active {
		background: rgba(15, 76, 117, 0.3);
	}

	.conversation-title {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-source);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		max-width: 100%;
	}

	.conversation-time {
		font-size: 0.6875rem;
		color: var(--color-text-whisper);
	}

	.empty-conversations {
		text-align: center;
		padding: 2rem 1rem;
	}

	.empty-conversations p {
		font-size: 0.875rem;
		color: var(--color-text-whisper);
	}

	.empty-conversations .hint {
		font-size: 0.75rem;
		color: var(--color-text-hint);
		margin-top: 0.25rem;
	}

	/* Main content */
	.main-content {
		flex: 1;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		padding: 1rem;
		overflow: hidden;
		min-width: 0;
	}

	/* Chat column */
	.chat-column {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		min-width: 0;
		overflow: hidden;
	}

	.response-container {
		flex: 1;
		overflow-y: auto;
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		padding: 1rem;
	}

	/* Welcome screen */
	.welcome-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
	}

	.welcome-spacer {
		flex: 1;
	}

	.welcome-greeting {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.welcome-logo {
		width: 64px;
		height: 64px;
	}

	.welcome-greeting h1 {
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.welcome-subtitle {
		font-size: 0.875rem;
		color: var(--color-text-whisper);
		margin-top: 0.5rem;
	}

	/* Messages */
	.message {
		display: flex;
		gap: 0.75rem;
		padding: 0.75rem 0;
	}

	.message.user {
		flex-direction: row-reverse;
	}

	.message-avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: var(--color-primary-100);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-primary-600);
		flex-shrink: 0;
	}

	[data-theme='dark'] .message-avatar {
		background: rgba(15, 76, 117, 0.3);
		color: var(--color-primary-400);
	}

	.message-avatar.user-avatar {
		background: var(--color-field-depth);
		color: var(--color-text-manifest);
	}

	.message-content {
		flex: 1;
		min-width: 0;
		max-width: 80%;
	}

	.message.user .message-content {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.25rem;
	}

	.message.user .message-header {
		flex-direction: row-reverse;
	}

	.message-role {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.message-time {
		font-size: 0.625rem;
		color: var(--color-text-hint);
	}

	.message-bubble {
		padding: 0.75rem 1rem;
		border-radius: 1rem;
		max-width: 100%;
	}

	.bubble-user {
		background: var(--color-primary-500);
		color: white;
		border-bottom-right-radius: 0.25rem;
	}

	.bubble-assistant {
		background: var(--color-field-depth);
		color: var(--color-text-source);
		border-bottom-left-radius: 0.25rem;
	}

	.message-text {
		font-size: 0.875rem;
		line-height: 1.5;
		word-break: break-word;
	}

	/* Input panel */
	.input-panel {
		background: var(--color-field-surface);
		border-radius: 0.75rem;
		border: 1px solid var(--color-veil-thin);
		padding: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.input-panel.drag-over {
		border-color: var(--color-primary-400);
		background: var(--color-primary-50);
	}

	[data-theme='dark'] .input-panel.drag-over {
		background: rgba(15, 76, 117, 0.1);
	}

	.hidden-input {
		display: none;
	}

	.attached-files {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.file-chip {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.25rem 0.5rem;
		background: var(--color-field-depth);
		border-radius: 0.375rem;
		font-size: 0.75rem;
	}

	.file-icon {
		font-size: 0.875rem;
	}

	.file-name {
		max-width: 100px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--color-text-source);
	}

	.file-size {
		color: var(--color-text-whisper);
	}

	.remove-file {
		padding: 0.125rem;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.25rem;
	}

	.remove-file:hover {
		background: var(--color-veil-thin);
		color: var(--color-error-500);
	}

	.input-row textarea {
		width: 100%;
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
		font-size: 0.875rem;
		resize: none;
		font-family: inherit;
		line-height: 1.5;
	}

	.input-row textarea:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.input-row textarea::placeholder {
		color: var(--color-text-hint);
	}

	.controls-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.controls-left,
	.controls-right {
		display: flex;
		align-items: center;
		gap: 0.375rem;
	}

	.control-btn {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.5rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		color: var(--color-text-manifest);
		cursor: pointer;
		font-size: 0.6875rem;
		font-weight: 500;
		transition: all 0.15s ease;
	}

	.control-btn:hover:not(:disabled) {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	[data-theme='dark'] .control-btn:hover:not(:disabled) {
		background: rgba(15, 76, 117, 0.3);
	}

	.control-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.causation-btn,
	.effect-btn {
		color: var(--color-primary-600);
	}

	[data-theme='dark'] .causation-btn,
	[data-theme='dark'] .effect-btn {
		color: var(--color-primary-400);
	}

	.model-select {
		padding: 0.375rem 0.5rem;
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.375rem;
		background: var(--color-field-void);
		color: var(--color-text-source);
		font-size: 0.75rem;
		cursor: pointer;
	}

	.model-select:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.send-btn {
		width: 36px;
		height: 36px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary-500);
		border: none;
		border-radius: 0.5rem;
		color: white;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.send-btn:hover:not(:disabled) {
		background: var(--color-primary-600);
	}

	.send-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.send-btn.stop-btn {
		background: var(--color-error-500);
	}

	.send-btn.stop-btn:hover {
		background: var(--color-error-600);
	}

	/* Matrix column */
	.matrix-column {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		min-width: 0;
		overflow: hidden;
	}

	.matrix-box {
		flex: 1;
		min-height: 0;
	}

	.preview-box {
		flex: 1;
		min-height: 0;
	}

	/* Popup styles */
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

	.toolbar-popup,
	.causation-popup,
	.effect-popup {
		width: 100%;
		max-width: 450px;
		max-height: 80vh;
		overflow-y: auto;
		background: var(--color-field-surface);
		border-radius: 1rem;
		border: 1px solid var(--color-veil-thin);
		box-shadow: var(--shadow-elevated);
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
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
		padding: 1rem;
	}

	.popup-description {
		font-size: 0.875rem;
		color: var(--color-text-whisper);
		margin-bottom: 1rem;
	}

	.popup-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	/* Power spots list */
	.power-spots-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.power-spot-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
	}

	.spot-icon {
		font-size: 1.25rem;
	}

	.spot-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.spot-title {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.spot-desc {
		font-size: 0.75rem;
		color: var(--color-text-whisper);
	}

	/* Plays list */
	.plays-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.play-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
	}

	.play-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.play-risk {
		font-size: 0.6875rem;
		font-weight: 500;
		padding: 0.25rem 0.5rem;
		border-radius: 9999px;
	}

	.play-risk.low {
		background: rgba(5, 150, 105, 0.1);
		color: #059669;
	}

	.play-risk.medium {
		background: rgba(217, 119, 6, 0.1);
		color: #d97706;
	}

	.play-risk.high {
		background: rgba(220, 38, 38, 0.1);
		color: #dc2626;
	}

	[data-theme='dark'] .play-risk.low {
		background: rgba(52, 211, 153, 0.15);
		color: #34d399;
	}

	[data-theme='dark'] .play-risk.medium {
		background: rgba(251, 191, 36, 0.15);
		color: #fbbf24;
	}

	[data-theme='dark'] .play-risk.high {
		background: rgba(248, 113, 113, 0.15);
		color: #f87171;
	}

	.scenarios-placeholder {
		padding: 2rem;
		text-align: center;
		color: var(--color-text-whisper);
		font-size: 0.875rem;
	}

	.toggle-risk-btn {
		width: 100%;
		padding: 0.75rem;
		background: var(--color-primary-500);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.15s ease;
	}

	.toggle-risk-btn:hover {
		background: var(--color-primary-600);
	}

	/* Dimension options */
	.dimension-options {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

	.dimension-option {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background-color 0.15s ease;
	}

	.dimension-option:hover {
		background: var(--color-field-elevated);
	}

	.dimension-option.selected {
		background: var(--color-primary-50);
		border: 1px solid var(--color-primary-400);
	}

	[data-theme='dark'] .dimension-option.selected {
		background: rgba(15, 76, 117, 0.2);
	}

	.dimension-option input {
		accent-color: var(--color-primary-500);
	}

	.dimension-option span {
		font-size: 0.875rem;
		color: var(--color-text-source);
	}

	.generate-more-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border: 1px dashed var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		color: var(--color-primary-600);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.generate-more-btn:hover {
		background: var(--color-primary-50);
		border-color: var(--color-primary-400);
	}

	[data-theme='dark'] .generate-more-btn {
		color: var(--color-primary-400);
	}

	[data-theme='dark'] .generate-more-btn:hover {
		background: rgba(15, 76, 117, 0.2);
	}
</style>
