<script lang="ts">
	/**
	 * Unified Chat Page - 4-Box Desktop Layout
	 *
	 * Layout (within the app layout's main content area):
	 * ┌────────────────────────────────────────────┐
	 * │  Response Container (80%)  │  Matrix 5x5   │
	 * │                            │    (50%)      │
	 * │                            │               │
	 * ├────────────────────────────┼───────────────┤
	 * │  Input Panel (20%)         │  Live Preview │
	 * │  [📎][Causation][Effect]→  │    (50%)      │
	 * └────────────────────────────┴───────────────┘
	 */

	import { onMount, onDestroy, tick } from 'svelte';
	import {
		chat,
		messages,
		currentConversation,
		conversations,
		isStreaming,
		streamingContent,
		questions,
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
		powerSpots as powerSpotsStore,
		activeDocumentId,
		activeDocument,
		plays as playsStore,
		selectedPlayId as selectedPlayIdStore,
		isLoadingPlays as isLoadingPlaysStore,
		autoRefresh as autoRefreshStore
	} from '$lib/stores';
	import { Button, Spinner, TypingIndicator } from '$lib/components/ui';
	import MatrixPanel from '$lib/components/matrix/MatrixPanel.svelte';
	import LivePreviewBox from '$lib/components/matrix/LivePreviewBox.svelte';
	import MatrixToolbar from '$lib/components/matrix/MatrixToolbar.svelte';
	import ContextControlPopup from '$lib/components/matrix/ContextControlPopup.svelte';

	// Chat state
	let messageInput = '';
	let messagesContainer: HTMLElement;
	let inputElement: HTMLTextAreaElement;
	let fileInputElement: HTMLInputElement;
	let selectedModel = 'claude-opus-4-5-20251101';
	let webSearchEnabled = false;
	let attachedFiles: File[] = [];
	let isDragging = false;
	let placeholderIndex = 0;
	let placeholderInterval: ReturnType<typeof setInterval>;

	// Welcome state - shows strategic overview until user starts chatting
	$: isWelcomeState = $messages.length === 0 && !$isStreaming;

	// Popup state
	let showContextPopup = false;
	let activeToolbarPopup: 'plays' | 'scenarios' | null = null;

	// Filtered view states (Power Spots and Risk are now filtered views, not popups)
	let showPowerSpotsView = false;
	let showRiskView = false;

	// Explanation popup state
	let explanationPopup: {
		type: 'powerSpot' | 'risk';
		row: number;
		col: number;
		cell: any;
	} | null = null;

	// Rotating placeholder prompts
	const PLACEHOLDERS = [
		"What's on your mind?",
		"I'll help you understand the why, not just the what...",
		"Share your thoughts, upload a file, or both...",
		"I'll surface what you're really after...",
		"Let's map what connects everything..."
	];

	const models = [
		{ id: 'claude-opus-4-5-20251101', name: 'Claude Opus 4.5' },
		{ id: 'gpt-5.2', name: 'GPT-5.2' },
		{ id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini' }
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

	// Copy message content to clipboard
	async function copyToClipboard(text: string) {
		try {
			await navigator.clipboard.writeText(text);
			addToast('success', 'Copied to clipboard');
		} catch (err) {
			addToast('error', 'Failed to copy');
		}
	}

	// Handle feedback toggle - clicking same feedback clears it
	function handleFeedback(messageId: string, feedback: 'up' | 'down', currentFeedback?: 'up' | 'down' | null) {
		if (currentFeedback === feedback) {
			chat.rateMessage(messageId, null);
		} else {
			chat.rateMessage(messageId, feedback);
		}
	}

	onMount(async () => {
		// Note: loadConversations is already called in the app layout, no need to call again here
		// This prevents duplicate API calls and reactive update loops

		// Rotate placeholder every 3 seconds
		placeholderInterval = setInterval(() => {
			placeholderIndex = (placeholderIndex + 1) % PLACEHOLDERS.length;
		}, 3000);

		// Matrix initialization is handled by chat.selectConversation() when loading documents
		// Do NOT call matrix.initializeMatrix() here as it causes race conditions
	});

	onDestroy(() => {
		if (placeholderInterval) {
			clearInterval(placeholderInterval);
		}
	});

	// Auto-scroll when new messages arrive - only if user hasn't scrolled up
	let lastMessageCount = 0;
	let userScrolledUp = false;
	let wasStreamingBefore = false;
	let lastScrollTop = 0; // Track last scroll position to detect user scroll direction
	const SCROLL_THRESHOLD = 150; // pixels from bottom to consider "at bottom"

	function isNearBottom(): boolean {
		if (!messagesContainer) return true;
		const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
		return scrollHeight - scrollTop - clientHeight < SCROLL_THRESHOLD;
	}

	function handleScroll() {
		if (!messagesContainer) return;

		const currentScrollTop = messagesContainer.scrollTop;

		// During streaming: detect if user is actively scrolling UP (away from bottom)
		// Once they scroll up, lock the scroll position until streaming ends or they scroll back to bottom
		if ($isStreaming) {
			// User scrolled up (intentional scroll away from new content)
			if (currentScrollTop < lastScrollTop) {
				userScrolledUp = true;
			}
			// User scrolled back to bottom - allow auto-scroll again
			else if (isNearBottom()) {
				userScrolledUp = false;
			}
			// If user scrolled down but not to bottom, keep userScrolledUp state
		} else {
			// Not streaming - simple check if at bottom
			userScrolledUp = !isNearBottom();
		}

		lastScrollTop = currentScrollTop;
	}

	// Only auto-scroll on message count changes, NOT on every streaming token
	$: {
		const currentCount = $messages.length;
		const isCurrentlyStreaming = $isStreaming;

		// Auto-scroll when: new message added OR streaming just started
		const streamingJustStarted = isCurrentlyStreaming && !wasStreamingBefore;
		const messageAdded = currentCount > lastMessageCount;

		// Reset userScrolledUp when streaming ends
		const streamingJustEnded = !isCurrentlyStreaming && wasStreamingBefore;
		if (streamingJustEnded) {
			userScrolledUp = false;
		}

		if ((messageAdded || streamingJustStarted) && messagesContainer) {
			lastMessageCount = currentCount;
			// Reset userScrolledUp when a NEW message is added (user sent message)
			if (messageAdded) {
				userScrolledUp = false;
				lastScrollTop = messagesContainer.scrollHeight; // Reset scroll tracking
			}
			setTimeout(() => {
				if (messagesContainer && !userScrolledUp) {
					messagesContainer.scrollTop = messagesContainer.scrollHeight;
				}
			}, 0);
		}

		wasStreamingBefore = isCurrentlyStreaming;
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
			await chat.sendMessage(content, selectedModel, files, webSearchEnabled);
		} catch (error: any) {
			addToast('error', error.message || 'Failed to send message');
		}
	}

	function handleNewChat() {
		// Clear current conversation - new one will be created on first message
		chat.clearCurrentConversation();
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

	// Matrix handlers
	function handleCellClick(e: CustomEvent<{ row: number; col: number }>) {
		// Cell click handled by MatrixPanel internally
	}

	function handleCellChange(e: CustomEvent<{ row: number; col: number; value: number }>) {
		// Cell value changes are handled via dimension updates in MatrixPanel
		// This handler is kept for backward compatibility with events
	}

	async function handleToolbarPopup(e: CustomEvent<{ type: 'plays' | 'scenarios' }>) {
		activeToolbarPopup = e.detail.type;
		// Fetch plays when opening plays popup
		if (e.detail.type === 'plays') {
			await matrix.fetchPlays();
		}
	}

	function handleTogglePowerSpots(e: CustomEvent<{ enabled: boolean }>) {
		showPowerSpotsView = e.detail.enabled;
		// Turn off risk view when enabling power spots
		if (e.detail.enabled) {
			showRiskView = false;
		}
	}

	function handleToggleRisk(e: CustomEvent<{ enabled: boolean }>) {
		showRiskView = e.detail.enabled;
		// Turn off power spots view when enabling risk
		if (e.detail.enabled) {
			showPowerSpotsView = false;
		}
	}

	function handleSaveScenario() {
		// TODO: Implement backend persistence
		addToast('info', 'Scenario save will be implemented with backend integration');
	}

	// Explanation loading state
	let explanationLoading = false;
	let explanationData: any = null;

	async function handleShowPowerSpotExplanation(e: CustomEvent<{ row: number; col: number; cell: any }>) {
		explanationPopup = {
			type: 'powerSpot',
			row: e.detail.row,
			col: e.detail.col,
			cell: e.detail.cell
		};
		explanationData = null;
		explanationLoading = true;

		try {
			const conversationId = $currentConversation?.id;
			const docId = $activeDocumentId;
			if (conversationId && docId) {
				const response = await fetch(
					`/api/matrix/${conversationId}/document/${docId}/cell/${e.detail.row}/${e.detail.col}/explain?explanation_type=leverage`,
					{ method: 'GET', credentials: 'include' }
				);
				if (response.ok) {
					const data = await response.json();
					explanationData = data.explanation;
				}
			}
		} catch (err) {
			console.error('Failed to fetch leverage explanation:', err);
		} finally {
			explanationLoading = false;
		}
	}

	async function handleShowRiskExplanation(e: CustomEvent<{ row: number; col: number; cell: any }>) {
		explanationPopup = {
			type: 'risk',
			row: e.detail.row,
			col: e.detail.col,
			cell: e.detail.cell
		};
		explanationData = null;
		explanationLoading = true;

		try {
			const conversationId = $currentConversation?.id;
			const docId = $activeDocumentId;
			if (conversationId && docId) {
				const response = await fetch(
					`/api/matrix/${conversationId}/document/${docId}/cell/${e.detail.row}/${e.detail.col}/explain?explanation_type=risk`,
					{ method: 'GET', credentials: 'include' }
				);
				if (response.ok) {
					const data = await response.json();
					explanationData = data.explanation;
				}
			}
		} catch (err) {
			console.error('Failed to fetch risk explanation:', err);
		} finally {
			explanationLoading = false;
		}
	}

	function closeExplanationPopup() {
		explanationPopup = null;
		explanationData = null;
	}

	function closeToolbarPopup() {
		activeToolbarPopup = null;
	}

	function handleContextSubmit() {
		showContextPopup = false;
	}
</script>

<svelte:head>
	<title>Chat | Reality Transformer</title>
</svelte:head>

<div class="chat-layout">
	<!-- Left column: Chat (Response + Input) -->
	<div class="chat-column">
		<!-- Response container (80%) -->
		<div class="response-container" bind:this={messagesContainer} on:scroll={handleScroll}>
			{#if $messages.length === 0}
				<!-- Welcome screen -->
				<div class="welcome-screen">
					<div class="welcome-spacer"></div>
					<div class="welcome-greeting">
						<div class="welcome-logo-container">
							<svg class="welcome-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
								<circle class="logo-circle" cx="50" cy="50" r="48"/>
								<text class="logo-text" x="50" y="72" font-family="'Product Sans', 'Roboto', sans-serif" font-size="55" font-weight="500" font-style="italic" text-anchor="middle">G</text>
							</svg>
						</div>
						<h1>{greeting}</h1>
						<p class="welcome-tagline">Strategic Intelligence Platform</p>
					</div>
					<div class="welcome-description">
						<p>Turn complexity into clarity through<br/>cross-impact analysis and scenario modeling.</p>
					</div>
					<div class="welcome-spacer"></div>
				</div>
			{:else}
				<!-- Messages -->
				{#each $messages as message (message.id)}
					<div class="message" class:user={message.role === 'user'}>
						<div class="message-content">
							<div class="message-bubble" class:bubble-user={message.role === 'user'} class:bubble-assistant={message.role === 'assistant'}>
								<div class="message-text">
									{@html message.content.replace(/\n/g, '<br>')}
								</div>
								{#if message.role === 'assistant'}
									<div class="message-actions">
										<button
											class="action-btn"
											title="Copy to clipboard"
											on:click={() => copyToClipboard(message.content)}
										>
											<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
												<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
												<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
											</svg>
										</button>
										<button
											class="action-btn"
											class:active={message.feedback === 'up'}
											title="Good response"
											on:click={() => handleFeedback(message.id, 'up', message.feedback)}
										>
											<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill={message.feedback === 'up' ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
												<path d="M7 10v12"/>
												<path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>
											</svg>
										</button>
										<button
											class="action-btn"
											class:active={message.feedback === 'down'}
											title="Poor response"
											on:click={() => handleFeedback(message.id, 'down', message.feedback)}
										>
											<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill={message.feedback === 'down' ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
												<path d="M17 14V2"/>
												<path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>
											</svg>
										</button>
									</div>
								{/if}
							</div>
						</div>
					</div>
				{/each}

				<!-- Streaming message -->
				{#if $isStreaming}
					<div class="message">
						<div class="message-content">
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

				<!-- Questions -->
				{#if $questions.length > 0}
					{#each $questions as q (q.id)}
						<div class="question-card" class:answered={q.selectedOption}>
							<div class="question-text">{q.text}</div>
							<div class="question-options">
								{#each q.options as option}
									<button
										class="question-option"
										class:selected={q.selectedOption === option.id}
										class:not-selected={q.selectedOption && q.selectedOption !== option.id}
										on:click={() => !q.selectedOption && chat.answerQuestion(q.id, option.id)}
										disabled={!!q.selectedOption}
									>
										{option.text}
									</button>
								{/each}
							</div>
						</div>
					{/each}
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
						<button class="control-btn context-btn" on:click={() => (showContextPopup = true)} title="Control matrix context">
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<circle cx="12" cy="12" r="3"/>
								<path d="M12 1v6"/>
								<path d="M12 17v6"/>
								<path d="M4.22 4.22l4.24 4.24"/>
								<path d="M15.54 15.54l4.24 4.24"/>
								<path d="M1 12h6"/>
								<path d="M17 12h6"/>
								<path d="M4.22 19.78l4.24-4.24"/>
								<path d="M15.54 8.46l4.24-4.24"/>
							</svg>
							<span>Context Control</span>
						</button>

						<label class="auto-refresh-toggle" title="Auto-update matrix on next query. LLM may add 1 new document per update.">
							<input type="checkbox" checked={$autoRefreshStore} on:change={() => matrix.toggleAutoRefresh()} />
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
								<path d="M3 3v5h5"/>
								<path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
								<path d="M16 16h5v5"/>
							</svg>
							<span>Auto Refresh</span>
						</label>
					{/if}
				</div>

				<div class="controls-right">
					<select bind:value={selectedModel} class="model-select">
						{#each models as model}
							<option value={model.id}>{model.name}</option>
						{/each}
					</select>

					<label class="web-search-toggle" title={webSearchEnabled ? "Disable web research" : "Enable web research"}>
						<input type="checkbox" bind:checked={webSearchEnabled} />
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<circle cx="12" cy="12" r="10"/>
							<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
							<path d="M2 12h20"/>
						</svg>
						<span>Research</span>
					</label>

					<button
						class="send-btn"
						on:click={handleSendMessage}
						disabled={$isStreaming || (!messageInput.trim() && attachedFiles.length === 0)}
					>
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
							<path d="M22 2L11 13" />
							<path d="M22 2L15 22L11 13L2 9L22 2Z" />
						</svg>
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Right column: Matrix + Preview (shows with welcome overlays in welcome state) -->
	<div class="matrix-column">
		<!-- Matrix Panel - always shown -->
		<div class="matrix-box" class:welcome-overlay-container={isWelcomeState}>
			<MatrixPanel
				matrixData={$matrixDataStore}
				rowHeaders={$rowHeadersStore}
				columnHeaders={$columnHeadersStore}
				showPowerSpotsView={showPowerSpotsView}
				showRiskView={showRiskView}
				compact={true}
				on:cellClick={handleCellClick}
				on:cellChange={handleCellChange}
				on:showPowerSpotExplanation={handleShowPowerSpotExplanation}
				on:showRiskExplanation={handleShowRiskExplanation}
			/>
			{#if isWelcomeState}
				<div class="welcome-overlay matrix-overlay">
					<div class="overlay-content">
						<div class="overlay-icon matrix-icon">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<rect x="3" y="3" width="7" height="7"/>
								<rect x="14" y="3" width="7" height="7"/>
								<rect x="14" y="14" width="7" height="7"/>
								<rect x="3" y="14" width="7" height="7"/>
							</svg>
						</div>
						<h3>Design Your Reality</h3>
						<p>Visualize how factors influence each other.<br/>Click cells to explore relationships.</p>
					</div>
				</div>
			{/if}
		</div>

		<!-- Toolbar - always shown -->
		<MatrixToolbar
			showPowerSpotsView={showPowerSpotsView}
			showRiskView={showRiskView}
			disabled={isWelcomeState}
			on:openPopup={handleToolbarPopup}
			on:togglePowerSpots={handleTogglePowerSpots}
			on:toggleRisk={handleToggleRisk}
			on:saveScenario={handleSaveScenario}
		/>

		<!-- Live Preview - always shown -->
		<div class="preview-box" class:welcome-overlay-container={isWelcomeState}>
			<LivePreviewBox
				coherence={$coherenceStore}
				balance={Math.round(($coherenceStore + $populationStore) / 2)}
				population={$populationStore}
				avgScore={$avgScoreStore}
				powerSpots={$powerSpotsStore}
				pendingChanges={0}
			/>
			{#if isWelcomeState}
				<div class="welcome-overlay preview-overlay">
					<div class="overlay-content">
						<div class="overlay-icon preview-icon">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
								<polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
								<polyline points="7.5 19.79 7.5 14.6 3 12"/>
								<polyline points="21 12 16.5 14.6 16.5 19.79"/>
								<polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
								<line x1="12" y1="22.08" x2="12" y2="12"/>
							</svg>
						</div>
						<h3>Live Preview</h3>
						<p>Watch reality unfold live.<br/>This is your output box.</p>
					</div>
				</div>
			{/if}
		</div>

	</div>
</div>

<!-- Toolbar Popups (Plays and Scenarios only) -->
{#if activeToolbarPopup}
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div class="popup-overlay" on:click={closeToolbarPopup} on:keydown={(e) => e.key === 'Escape' && closeToolbarPopup()} role="presentation" tabindex="-1">
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div class="toolbar-popup" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true">
			<div class="popup-header">
				<h3>
					{#if activeToolbarPopup === 'plays'}Plays
					{:else if activeToolbarPopup === 'scenarios'}Scenarios
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
				{#if activeToolbarPopup === 'plays'}
					{#if $activeDocument?.name}
						<div class="document-name-badge">{$activeDocument.name}</div>
					{/if}
					<p class="popup-description">Transformation strategies for this document</p>
					<div class="plays-list">
						{#if $isLoadingPlaysStore}
							<div class="plays-loading">
								<Spinner size="sm" />
								<span>Loading plays...</span>
							</div>
						{:else if $playsStore.length > 0}
							{#each $playsStore as play (play.id)}
								<button
									class="play-item"
									class:selected={$selectedPlayIdStore === play.id}
									on:click={() => matrix.selectPlay(play.id)}
								>
									<div class="play-info">
										<span class="play-name">{play.name}</span>
										<span class="play-desc">{play.description}</span>
										<div class="play-meta">
											<span class="play-timeline">{play.timeline}</span>
											<span class="play-phases">{play.phases} phases</span>
											<span class="play-improvement">+{play.expectedImprovement}%</span>
										</div>
									</div>
									<div class="play-badges">
										<span class="play-fit">Fit: {play.fitScore}%</span>
										<span class="play-risk {play.risk}">{play.risk}</span>
									</div>
								</button>
							{/each}
						{:else}
							<p class="plays-hint">No plays available. Plays are generated during document population - send a message to generate matrix data first.</p>
						{/if}
					</div>
				{:else if activeToolbarPopup === 'scenarios'}
					<p class="popup-description">Compare different transformation scenarios</p>
					<div class="scenarios-list">
						<p class="scenarios-hint">Save scenarios using the Save button, then compare them here</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<!-- Explanation Popup (Power Spot or Risk) -->
{#if explanationPopup}
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div class="popup-overlay" on:click={closeExplanationPopup} on:keydown={(e) => e.key === 'Escape' && closeExplanationPopup()} role="presentation" tabindex="-1">
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<div class="toolbar-popup explanation-popup" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true">
			<div class="popup-header">
				<h3>
					{#if explanationPopup.type === 'powerSpot'}
						<span class="header-icon">⚡</span> Power Spot
					{:else}
						<span class="header-icon">⚠</span> Risk Analysis
					{/if}
				</h3>
				<button class="close-btn" on:click={closeExplanationPopup}>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M18 6 6 18" />
						<path d="m6 6 12 12" />
					</svg>
				</button>
			</div>
			<div class="popup-body">
				<div class="cell-info">
					<span class="cell-label">{explanationData?.cell_label || `${$rowHeadersStore[explanationPopup.row]} × ${$columnHeadersStore[explanationPopup.col]}`}</span>
					<span class="cell-score">Score: {explanationPopup.cell.value}</span>
				</div>

				{#if explanationLoading}
					<div class="loading-section">
						<div class="loading-spinner"></div>
						<p>Analyzing cell with AI...</p>
					</div>
				{:else if explanationData && !explanationData.message}
					{#if explanationPopup.type === 'powerSpot'}
						<div class="explanation-section">
							<h4>Why is this a Power Spot?</h4>
							<p>{explanationData.why_leverage || explanationData.description}</p>
							<div class="impact-details">
								<div class="impact-item">
									<span class="impact-label">Impact Score</span>
									<span class="impact-value high">{explanationData.impact_score || explanationPopup.cell.value}</span>
								</div>
								<div class="impact-item">
									<span class="impact-label">Effort Score</span>
									<span class="impact-value">{explanationData.effort_score || 'N/A'}</span>
								</div>
								<div class="impact-item">
									<span class="impact-label">ROI Ratio</span>
									<span class="impact-value high">{explanationData.roi_ratio ? explanationData.roi_ratio.toFixed(2) + 'x' : 'N/A'}</span>
								</div>
							</div>
							{#if explanationData.cascade_effects?.length}
								<h4>Cascade Effects</h4>
								<ul class="action-list">
									{#each explanationData.cascade_effects as effect}
										<li>{effect}</li>
									{/each}
								</ul>
							{/if}
							{#if explanationData.recommended_actions?.length}
								<h4>Recommended Actions</h4>
								<ul class="action-list">
									{#each explanationData.recommended_actions as action}
										<li>{action}</li>
									{/each}
								</ul>
							{/if}
						</div>
					{:else}
						<div class="explanation-section">
							<h4>Risk Assessment</h4>
							<p>{explanationData.description}</p>
							<div class="impact-details">
								<div class="impact-item">
									<span class="impact-label">Risk Level</span>
									<span class="impact-value {explanationData.risk_level}">{explanationData.risk_level === 'high' ? 'High' : 'Medium'}</span>
								</div>
								<div class="impact-item">
									<span class="impact-label">Current Score</span>
									<span class="impact-value">{explanationPopup.cell.value}</span>
								</div>
							</div>
							{#if explanationData.risk_factors?.length}
								<h4>Risk Factors</h4>
								<ul class="action-list">
									{#each explanationData.risk_factors as factor}
										<li>{factor}</li>
									{/each}
								</ul>
							{/if}
							{#if explanationData.mitigation_strategies?.length}
								<h4>Mitigation Strategies</h4>
								<ul class="action-list">
									{#each explanationData.mitigation_strategies as strategy}
										<li>{strategy}</li>
									{/each}
								</ul>
							{/if}
							{#if explanationData.impact_if_ignored}
								<h4>Impact if Ignored</h4>
								<p class="warning-text">{explanationData.impact_if_ignored}</p>
							{/if}
						</div>
					{/if}
				{:else}
					<!-- Fallback to static content if no API data -->
					{#if explanationPopup.type === 'powerSpot'}
						<div class="explanation-section">
							<h4>Why is this a Power Spot?</h4>
							<p>{explanationData?.message || 'This cell has a high impact score (≥75), indicating it\'s a strategic leverage point where small changes can create cascading positive effects.'}</p>
							<div class="impact-details">
								<div class="impact-item">
									<span class="impact-label">Impact Score</span>
									<span class="impact-value high">{explanationPopup.cell.value}</span>
								</div>
								<div class="impact-item">
									<span class="impact-label">Cascade Potential</span>
									<span class="impact-value">High</span>
								</div>
							</div>
						</div>
					{:else}
						<div class="explanation-section">
							<h4>Risk Assessment</h4>
							<p>{explanationData?.message || `This cell has been flagged as ${explanationPopup.cell.riskLevel === 'high' ? 'high' : 'medium'} risk based on its current state.`}</p>
							<div class="impact-details">
								<div class="impact-item">
									<span class="impact-label">Risk Level</span>
									<span class="impact-value {explanationPopup.cell.riskLevel}">{explanationPopup.cell.riskLevel === 'high' ? 'High' : 'Medium'}</span>
								</div>
								<div class="impact-item">
									<span class="impact-label">Current Score</span>
									<span class="impact-value">{explanationPopup.cell.value}</span>
								</div>
							</div>
						</div>
					{/if}
				{/if}
			</div>
		</div>
	</div>
{/if}

<!-- Context Control Popup -->
<ContextControlPopup
	bind:open={showContextPopup}
	model={selectedModel}
	on:close={() => (showContextPopup = false)}
	on:submit={handleContextSubmit}
/>

<style>
	/* Chat layout - clean grid */
	.chat-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
		padding: 1.5rem;
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	/* Chat column */
	.chat-column {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		min-width: 0;
		min-height: 0;
		overflow: hidden;
	}

	.response-container {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		padding: 1.5rem calc(0.75rem + 1px);
		min-height: 0;
		/* Override global smooth scroll - prevents conflicts during streaming */
		scroll-behavior: auto;
	}

	/* Welcome screen - ultra minimal */
	.welcome-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		padding: 3rem;
	}

	.welcome-spacer {
		flex: 1;
	}

	.welcome-greeting {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
	}

	.welcome-logo-container {
		margin-bottom: 1rem;
	}

	.welcome-logo {
		width: 48px;
		height: 48px;
	}

	.welcome-logo .logo-circle {
		fill: var(--color-primary-500);
		stroke: none;
	}

	.welcome-logo .logo-text {
		fill: #ffffff;
	}

	.welcome-greeting h1 {
		font-family: var(--font-heading);
		font-size: 2rem;
		font-weight: 600;
		color: var(--color-primary-500);
		letter-spacing: -0.02em;
	}

	.welcome-tagline {
		font-size: var(--font-size-sm);
		font-weight: 500;
		color: var(--color-text-whisper);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.welcome-description {
		margin-top: 2rem;
		max-width: 400px;
	}

	.welcome-description p {
		font-size: var(--font-size-md);
		line-height: 1.6;
		color: var(--color-text-manifest);
	}

	/* Messages - minimal */
	.message {
		display: flex;
		gap: 0.75rem;
		padding: 1rem 0;
	}

	.message.user {
		justify-content: flex-end;
	}

	.message-content {
		max-width: 85%;
	}

	.message:not(.user) .message-content {
		max-width: 100%;
		width: 100%;
	}

	.message.user .message-content {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
	}

	.message-bubble {
		padding: 0.875rem 1rem;
		max-width: 100%;
	}

	.bubble-user {
		background: var(--color-field-depth);
		color: var(--color-text-source);
		border-radius: 1rem 1rem 0.25rem 1rem;
	}

	.bubble-assistant {
		background: transparent;
		color: var(--color-text-source);
		border-radius: 1rem;
		padding-left: 0;
		padding-right: 0;
	}

	.message-text {
		font-size: var(--font-size-md);
		line-height: 1.6;
		word-break: break-word;
	}

	.bubble-assistant .message-text {
		text-align: justify;
	}

	/* Message actions (copy, thumbs up/down) */
	.message-actions {
		display: flex;
		gap: 0.25rem;
		margin-top: 0.75rem;
		opacity: 0;
		transition: opacity 0.15s ease;
	}

	.message:hover .message-actions,
	.message-actions:focus-within {
		opacity: 1;
	}

	/* Keep visible if any feedback is active */
	.message-actions:has(.action-btn.active) {
		opacity: 1;
	}

	.action-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		padding: 0;
		border: none;
		border-radius: 0.375rem;
		background: transparent;
		color: var(--color-text-whisper);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.action-btn:hover {
		background: var(--color-field-depth);
		color: var(--color-text-manifest);
	}

	.action-btn.active {
		color: var(--color-primary-500);
	}

	.action-btn.active:hover {
		background: var(--color-accent-subtle);
	}

	/* Question - inline with response text */
	.question-card {
		padding: 1rem 0;
		background: transparent;
		border: none;
		border-radius: 0;
		box-shadow: none;
	}

	.question-text {
		font-size: var(--font-size-md);
		font-weight: 400;
		color: var(--color-text-source);
		margin-bottom: 1rem;
		line-height: 1.6;
		text-align: justify;
	}

	.question-options {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.question-option {
		padding: 0.75rem 1rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		color: var(--color-text-manifest);
		font-size: var(--font-size-sm);
		text-align: left;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.question-option:hover:not(:disabled) {
		background: var(--color-accent-subtle);
		border-color: var(--color-primary-300);
		color: var(--color-text-source);
	}

	.question-option.selected {
		background: var(--color-primary-500);
		border-color: var(--color-primary-500);
		color: white;
		cursor: default;
	}

	.question-option.not-selected {
		opacity: 0.5;
		cursor: default;
	}

	.question-card.answered {
		opacity: 0.85;
	}

	/* Input panel - minimal */
	.input-panel {
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.75rem;
		padding: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		flex-shrink: 0;
		overflow: hidden;
	}

	.input-panel.drag-over {
		border-color: var(--color-text-source);
		background: var(--color-field-depth);
	}

	.input-panel:focus-within {
		border-color: var(--color-text-whisper);
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
		border-radius: 0.25rem;
		font-size: var(--font-size-xs);
	}

	.file-icon {
		font-size: var(--font-size-base);
	}

	.file-name {
		max-width: 80px;
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
		color: var(--color-error-500);
	}

	.input-row textarea {
		width: 100%;
		padding: 0.5rem 0;
		border: none;
		border-radius: 0;
		background: transparent;
		color: var(--color-text-source);
		font-size: var(--font-size-base);
		resize: none;
		font-family: inherit;
		line-height: 1.6;
	}

	.input-row textarea:focus {
		outline: none;
	}

	.input-row textarea::placeholder {
		color: var(--color-text-hint);
	}

	.controls-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		padding-top: 0.5rem;
		min-height: 44px;
		border-top: 1px solid var(--color-veil-thin);
	}

	.controls-left,
	.controls-right {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.control-btn {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.5rem;
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		color: var(--color-text-whisper);
		cursor: pointer;
		font-size: var(--font-size-base);
		font-weight: 400;
		transition: all 0.1s ease;
	}

	.control-btn:hover:not(:disabled) {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.control-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.context-btn {
		color: var(--color-accent);
		border: 1px solid var(--color-accent);
		border-radius: 1rem;
		min-width: 120px;
		justify-content: center;
	}

	.model-select {
		padding: 0.375rem 0.5rem;
		border: none;
		border-radius: 0.375rem;
		background: transparent;
		color: var(--color-text-whisper);
		font-size: var(--font-size-base);
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.model-select:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.model-select:focus {
		outline: none;
	}

	.web-search-toggle {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.5rem;
		border: none;
		border-radius: 0.375rem;
		background: transparent;
		color: var(--color-text-whisper);
		font-size: var(--font-size-base);
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.web-search-toggle:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.web-search-toggle:has(input:checked) {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.web-search-toggle input {
		display: none;
	}

	.web-search-toggle svg {
		flex-shrink: 0;
	}

	/* Auto refresh toggle - similar to web search but in controls-left */
	.auto-refresh-toggle {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.5rem;
		border: none;
		border-radius: 0.375rem;
		background: transparent;
		color: var(--color-text-whisper);
		font-size: 0.75rem;
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.auto-refresh-toggle:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.auto-refresh-toggle:has(input:checked) {
		background: var(--color-primary-50);
		color: var(--color-primary-600);
	}

	[data-theme='dark'] .auto-refresh-toggle:has(input:checked) {
		background: rgba(59, 130, 246, 0.15);
		color: var(--color-primary-400);
	}

	.auto-refresh-toggle input {
		display: none;
	}

	.auto-refresh-toggle svg {
		flex-shrink: 0;
	}

	.auto-refresh-toggle span {
		white-space: nowrap;
	}

	.send-btn {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-primary-500);
		border: none;
		border-radius: 0.375rem;
		color: #ffffff;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.send-btn:hover:not(:disabled) {
		background: var(--color-primary-800);
	}

	.send-btn:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	/* Matrix column */
	.matrix-column {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		min-width: 0;
		min-height: 0;
		overflow: hidden;
	}

	.matrix-box {
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	.preview-box {
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	/* Welcome Overlay - subtle glass */
	.welcome-overlay-container {
		position: relative;
	}

	.welcome-overlay {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: color-mix(in srgb, var(--color-field-void) 92%, transparent);
		backdrop-filter: blur(4px);
		border-radius: 0.5rem;
		z-index: 10;
		transition: opacity 0.2s ease;
	}

	.welcome-overlay:hover {
		opacity: 0.3;
	}

	.overlay-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: 1.5rem;
		max-width: 400px;
	}

	.overlay-icon {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 0.5rem;
		margin-bottom: 0.75rem;
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.matrix-icon,
	.preview-icon {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.overlay-content h3 {
		font-size: 16px;
		font-weight: 500;
		color: var(--color-text-source);
		margin-bottom: 0.375rem;
	}

	.overlay-content p {
		font-size: 14px;
		line-height: 1.5;
		color: var(--color-text-manifest);
	}

	/* Popup styles - clean */
	.popup-overlay {
		position: fixed;
		inset: 0;
		background: rgba(255, 255, 255, 0.8);
		backdrop-filter: blur(8px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: 1rem;
	}

	.toolbar-popup {
		width: 100%;
		max-width: 400px;
		max-height: 80vh;
		overflow-y: auto;
		background: var(--color-field-surface);
		border-radius: 0.75rem;
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
		font-size: 16px;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.close-btn {
		padding: 0.375rem;
		background: transparent;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.375rem;
		transition: all 0.1s ease;
	}

	.close-btn:hover {
		background: var(--color-accent-subtle);
		color: var(--color-text-source);
	}

	.popup-body {
		padding: 1rem;
	}

	.popup-description {
		font-size: 14px;
		color: var(--color-text-whisper);
		margin-bottom: 1rem;
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
		border-radius: 0.375rem;
	}

	.spot-icon {
		font-size: 1rem;
	}

	.spot-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.spot-title {
		font-size: 15px;
		font-weight: 500;
		color: var(--color-text-source);
	}

	.spot-desc {
		font-size: 13px;
		color: var(--color-text-whisper);
	}

	/* Document name badge */
	.document-name-badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		margin-bottom: 0.75rem;
		background: var(--color-primary-100);
		color: var(--color-primary-700);
		border-radius: 1rem;
		font-size: 0.75rem;
		font-weight: 600;
	}

	/* Plays list */
	.plays-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.plays-loading {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 2rem;
		color: var(--color-text-whisper);
		font-size: 14px;
	}

	.play-item {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border: 1px solid transparent;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
	}

	.play-item:hover {
		border-color: var(--color-primary-400);
	}

	.play-item.selected {
		background: var(--color-primary-50);
		border-color: var(--color-primary-500);
	}

	.play-info {
		flex: 1;
		min-width: 0;
	}

	.play-name {
		display: block;
		font-size: 14px;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.25rem;
	}

	.play-desc {
		display: block;
		font-size: 12px;
		color: var(--color-text-whisper);
		margin-bottom: 0.5rem;
		line-height: 1.4;
	}

	.play-meta {
		display: flex;
		gap: 0.75rem;
		font-size: 11px;
		color: var(--color-text-manifest);
	}

	.play-meta span {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.play-badges {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.25rem;
		flex-shrink: 0;
	}

	.play-fit {
		font-size: 11px;
		font-weight: 600;
		color: var(--color-primary-600);
	}

	.play-risk {
		font-size: 12px;
		font-weight: 500;
		padding: 0.25rem 0.5rem;
		border-radius: 9999px;
	}

	.play-risk.low {
		background: rgba(22, 163, 74, 0.1);
		color: #16a34a;
	}

	.play-risk.medium {
		background: rgba(217, 119, 6, 0.1);
		color: #d97706;
	}

	.play-risk.high {
		background: rgba(220, 38, 38, 0.1);
		color: #dc2626;
	}

	.scenarios-placeholder {
		padding: 2rem;
		text-align: center;
		color: var(--color-text-whisper);
		font-size: 14px;
	}

	/* Generate plays button */
	.generate-plays-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem;
		background: var(--color-primary-500);
		color: #ffffff;
		border: none;
		border-radius: 0.5rem;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.generate-plays-btn:hover {
		background: var(--color-primary-600);
	}

	.plays-hint,
	.scenarios-hint {
		padding: 1rem;
		text-align: center;
		color: var(--color-text-whisper);
		font-size: 13px;
	}

	/* Explanation popup styles */
	.explanation-popup {
		max-width: 480px;
	}

	.header-icon {
		margin-right: 0.25rem;
	}

	.cell-info {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem;
		background: var(--color-field-depth);
		border-radius: 0.5rem;
		margin-bottom: 1rem;
	}

	.cell-label {
		font-size: 14px;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.cell-score {
		font-size: 13px;
		font-weight: 500;
		color: var(--color-text-manifest);
		padding: 0.25rem 0.5rem;
		background: var(--color-accent-subtle);
		border-radius: 0.25rem;
	}

	.explanation-section h4 {
		font-size: 13px;
		font-weight: 600;
		color: var(--color-text-source);
		margin: 0.75rem 0 0.5rem;
		text-transform: uppercase;
		letter-spacing: 0.03em;
	}

	.explanation-section p {
		font-size: 14px;
		color: var(--color-text-manifest);
		line-height: 1.5;
	}

	.impact-details {
		display: flex;
		gap: 1rem;
		margin: 0.75rem 0;
	}

	.impact-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		padding: 0.5rem 0.75rem;
		background: var(--color-field-depth);
		border-radius: 0.375rem;
	}

	.impact-label {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-whisper);
	}

	.impact-value {
		font-size: 16px;
		font-weight: 600;
		color: var(--color-text-source);
	}

	.impact-value.high {
		color: #16a34a;
	}

	.impact-value.medium {
		color: #d97706;
	}

	.action-list {
		margin: 0.5rem 0;
		padding-left: 1.25rem;
	}

	.action-list li {
		font-size: 13px;
		color: var(--color-text-manifest);
		margin-bottom: 0.375rem;
		line-height: 1.4;
	}

	/* Responsive */
	@media (max-width: 1024px) {
		.chat-layout {
			grid-template-columns: 1fr;
			grid-template-rows: 1fr 1fr;
		}
	}

	@media (max-width: 767px) {
		.chat-layout {
			padding: 0.5rem;
			gap: 0.5rem;
		}
	}
</style>
