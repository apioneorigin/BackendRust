<script lang="ts">
	import { onMount, onDestroy, tick } from 'svelte';
	import {
		chat,
		messages,
		currentConversation,
		conversations,
		isStreaming,
		streamingContent,
		addToast,
		user
	} from '$lib/stores';
	import { Button, Spinner, TypingIndicator } from '$lib/components/ui';

	let messageInput = '';
	let messagesContainer: HTMLElement;
	let inputElement: HTMLTextAreaElement;
	let fileInputElement: HTMLInputElement;
	let selectedModel = 'gpt-4.1';
	let attachedFiles: File[] = [];
	let isDragging = false;
	let placeholderIndex = 0;
	let placeholderInterval: ReturnType<typeof setInterval>;

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

	// Reactive greeting
	$: greeting = getGreeting();

	onMount(async () => {
		await chat.loadConversations();

		// Rotate placeholder every 3 seconds
		placeholderInterval = setInterval(() => {
			placeholderIndex = (placeholderIndex + 1) % PLACEHOLDERS.length;
		}, 3000);
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

		// Reset textarea height
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
		target.style.height = Math.min(target.scrollHeight, 200) + 'px';
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
		// Reset input so same file can be selected again
		target.value = '';
	}

	function addFiles(files: File[]) {
		const validFiles = files.filter((file) => {
			// Check file size (max 10MB)
			if (file.size > 10 * 1024 * 1024) {
				addToast('error', 'File too large', `${file.name} exceeds 10MB limit`);
				return false;
			}
			// Check for duplicates
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

	// Drag and drop handlers
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
</script>

<svelte:head>
	<title>Chat | Reality Transformer</title>
</svelte:head>

<div class="chat-layout">
	<!-- Conversation sidebar -->
	<aside class="conversations-panel">
		<div class="panel-header">
			<h3>Conversations</h3>
			<Button variant="primary" size="sm" on:click={handleNewChat}>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="14"
					height="14"
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

	<!-- Main chat area -->
	<div class="chat-main">
		<!-- Messages -->
		<div class="messages-container chat-scroll" bind:this={messagesContainer}>
			{#if $messages.length === 0}
				<div class="welcome-screen">
					<!-- Spacer to push content down -->
					<div class="welcome-spacer"></div>

					<!-- Greeting with logo -->
					<div class="welcome-greeting">
						<svg class="welcome-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
							<circle cx="50" cy="50" r="45" fill="#0f4c75" stroke="#3d93ce" stroke-width="4"/>
							<text x="50" y="72" font-family="'Product Sans', 'Roboto', 'Arial', sans-serif" font-size="55" font-weight="500" font-style="italic" fill="#FFFFFF" text-anchor="middle">G</text>
						</svg>
						<h1>{greeting}</h1>
					</div>

					<!-- Centered input with rotating placeholder -->
					<div class="welcome-input-container">
						<!-- Hidden file input -->
						<input
							type="file"
							bind:this={fileInputElement}
							on:change={handleFileSelect}
							multiple
							accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.json,.xml,.zip,.rar"
							class="hidden-input"
						/>

						<!-- Attached files preview -->
						{#if attachedFiles.length > 0}
							<div class="welcome-attached-files">
								{#each attachedFiles as file, index}
									<div class="file-chip">
										<span class="file-icon">{getFileIcon(file)}</span>
										<span class="file-name">{file.name}</span>
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

						<div class="welcome-input input-premium">
							<textarea
								bind:this={inputElement}
								bind:value={messageInput}
								on:keydown={handleKeyDown}
								on:input={handleInput}
								placeholder={PLACEHOLDERS[placeholderIndex]}
								rows="2"
								disabled={$isStreaming}
							></textarea>

							<div class="welcome-input-controls">
								<button
									class="attach-btn"
									on:click={triggerFileInput}
									disabled={$isStreaming}
									title="Attach files"
								>
									<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
									</svg>
								</button>

								<div class="flex-spacer"></div>

								<button
									class="welcome-send-btn"
									on:click={handleSendMessage}
									disabled={(!messageInput.trim() && attachedFiles.length === 0) || $isStreaming}
								>
									<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
										<path d="M22 2L11 13" />
										<path d="M22 2L15 22L11 13L2 9L22 2Z" />
									</svg>
								</button>
							</div>
						</div>

						<p class="welcome-hint">
							<span class="mobile-hint">Tap send or Enter to send</span>
							<span class="desktop-hint">Press Enter to send, Shift+Enter for new line</span>
						</p>
					</div>

					<!-- Spacer to push content up -->
					<div class="welcome-spacer"></div>
				</div>
			{:else}
				{#each $messages as message (message.id)}
					<div class="message" class:user={message.role === 'user'}>
						<div class="message-avatar" class:user-avatar={message.role === 'user'}>
							{#if message.role === 'user'}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
									<circle cx="12" cy="7" r="4" />
								</svg>
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
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
							<div
								class="message-bubble"
								class:bubble-user={message.role === 'user'}
								class:bubble-assistant={message.role === 'assistant'}
							>
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
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="18"
								height="18"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
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

		<!-- Input area -->
		<div class="input-area"
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

			<div class="input-controls">
				<select bind:value={selectedModel} class="model-select">
					{#each models as model}
						<option value={model.id}>{model.name}</option>
					{/each}
				</select>
			</div>

			<!-- Attached files preview -->
			{#if attachedFiles.length > 0}
				<div class="attached-files">
					{#each attachedFiles as file, index}
						<div class="file-chip">
							<span class="file-icon">{getFileIcon(file)}</span>
							<span class="file-name">{file.name}</span>
							<span class="file-size">{formatFileSize(file.size)}</span>
							<button class="remove-file" on:click={() => removeFile(index)} title="Remove file">
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M18 6 6 18" />
									<path d="m6 6 12 12" />
								</svg>
							</button>
						</div>
					{/each}
				</div>
			{/if}

			<div class="input-container input-premium">
				<!-- File upload button -->
				<button
					class="attach-btn"
					on:click={triggerFileInput}
					disabled={$isStreaming}
					title="Attach files"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
					</svg>
				</button>

				<textarea
					bind:this={inputElement}
					bind:value={messageInput}
					on:keydown={handleKeyDown}
					on:input={handleInput}
					placeholder={attachedFiles.length > 0 ? "Add a message or send files..." : "Type your message..."}
					rows="1"
					disabled={$isStreaming}
				></textarea>
				<div class="input-actions">
					{#if $isStreaming}
						<Button variant="outline" size="sm" on:click={stopGeneration}>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="14"
								height="14"
								viewBox="0 0 24 24"
								fill="currentColor"
							>
								<rect x="6" y="6" width="12" height="12" rx="2" />
							</svg>
							Stop
						</Button>
					{:else}
						<Button
							variant="primary"
							size="sm"
							on:click={handleSendMessage}
							disabled={!messageInput.trim() && attachedFiles.length === 0}
						>
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
								<path d="m22 2-7 20-4-9-9-4Z" />
								<path d="M22 2 11 13" />
							</svg>
						</Button>
					{/if}
				</div>
			</div>

			<!-- Drag overlay -->
			{#if isDragging}
				<div class="drag-overlay">
					<div class="drag-content">
						<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
							<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
							<polyline points="17 8 12 3 7 8" />
							<line x1="12" x2="12" y1="3" y2="15" />
						</svg>
						<p>Drop files here</p>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.chat-layout {
		display: flex;
		height: 100%;
		overflow: hidden;
	}

	/* Conversations panel */
	.conversations-panel {
		width: 280px;
		background: var(--color-field-surface);
		border-right: 1px solid var(--color-veil-thin);
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
	}

	.panel-header {
		padding: 1rem;
		border-bottom: 1px solid var(--color-veil-thin);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.panel-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-whisper);
	}

	.conversations-list {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.conversation-item {
		width: 100%;
		padding: 0.75rem 1rem;
		background: none;
		border: none;
		border-radius: 0.625rem;
		text-align: left;
		cursor: pointer;
		transition: background-color 0.15s ease;
	}

	.conversation-item:hover {
		background: var(--color-field-depth);
	}

	.conversation-item.active {
		background: var(--color-primary-50);
	}

	[data-theme='dark'] .conversation-item.active {
		background: var(--color-primary-900);
	}

	.conversation-title {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-source);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.conversation-time {
		display: block;
		font-size: 0.75rem;
		color: var(--color-text-whisper);
		margin-top: 0.25rem;
	}

	.empty-conversations {
		padding: 2rem 1rem;
		text-align: center;
	}

	.empty-conversations p {
		font-size: 0.875rem;
		color: var(--color-text-whisper);
	}

	.empty-conversations .hint {
		font-size: 0.75rem;
		margin-top: 0.5rem;
	}

	/* Main chat area */
	.chat-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.messages-container {
		flex: 1;
		overflow-y: auto;
		padding: 1.5rem;
	}

	/* Welcome screen - centered input like Claude.ai */
	.welcome-screen {
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 1rem;
	}

	.welcome-spacer {
		flex: 1;
	}

	.welcome-greeting {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		margin-bottom: 2rem;
	}

	.welcome-logo {
		width: 40px;
		height: 40px;
		flex-shrink: 0;
	}

	@media (min-width: 768px) {
		.welcome-logo {
			width: 48px;
			height: 48px;
		}
	}

	.welcome-greeting h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-primary-700);
	}

	[data-theme='dark'] .welcome-greeting h1 {
		color: var(--color-primary-300);
	}

	@media (min-width: 768px) {
		.welcome-greeting h1 {
			font-size: 2rem;
		}
	}

	.welcome-input-container {
		width: 100%;
		max-width: 48rem;
	}

	.welcome-attached-files {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
		padding: 0 0.25rem;
	}

	.welcome-input {
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.welcome-input textarea {
		width: 100%;
		min-height: 72px;
		max-height: 200px;
		padding: 0.875rem 1rem;
		border: none;
		background: transparent;
		color: var(--color-text-source);
		font-size: 0.9375rem;
		line-height: 1.5;
		resize: none;
		font-family: inherit;
	}

	.welcome-input textarea:focus {
		outline: none;
	}

	.welcome-input textarea::placeholder {
		color: var(--color-text-hint);
		transition: opacity 0.3s ease;
	}

	.welcome-input textarea:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.welcome-input-controls {
		display: flex;
		align-items: center;
		padding: 0.5rem 0.75rem;
		border-top: 1px solid var(--color-veil-thin);
		background: var(--color-field-depth);
	}

	.flex-spacer {
		flex: 1;
	}

	.welcome-send-btn {
		width: 36px;
		height: 36px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.welcome-send-btn:not(:disabled) {
		background: var(--color-primary-500);
		color: white;
	}

	.welcome-send-btn:not(:disabled):hover {
		background: var(--color-primary-600);
	}

	.welcome-send-btn:disabled {
		background: var(--color-primary-200);
		color: var(--color-primary-400);
		cursor: not-allowed;
	}

	[data-theme='dark'] .welcome-send-btn:disabled {
		background: var(--color-primary-800);
		color: var(--color-primary-600);
	}

	.welcome-hint {
		margin-top: 0.75rem;
		text-align: center;
		font-size: 0.6875rem;
		color: var(--color-text-hint);
	}

	.welcome-hint .mobile-hint {
		display: block;
	}

	.welcome-hint .desktop-hint {
		display: none;
	}

	@media (min-width: 768px) {
		.welcome-hint .mobile-hint {
			display: none;
		}

		.welcome-hint .desktop-hint {
			display: block;
		}
	}

	/* Messages */
	.message {
		display: flex;
		gap: 0.875rem;
		margin-bottom: 1.5rem;
	}

	.message.user {
		flex-direction: row-reverse;
	}

	.message-avatar {
		width: 36px;
		height: 36px;
		border-radius: 0.625rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		background: var(--gradient-primary);
		color: white;
	}

	.message-avatar.user-avatar {
		background: var(--color-primary-100);
		color: var(--color-primary-700);
	}

	[data-theme='dark'] .message-avatar.user-avatar {
		background: var(--color-primary-800);
		color: var(--color-primary-200);
	}

	.message-content {
		flex: 1;
		min-width: 0;
		max-width: 70%;
	}

	.message.user .message-content {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
	}

	.message-header {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		margin-bottom: 0.375rem;
	}

	.message.user .message-header {
		flex-direction: row-reverse;
	}

	.message-role {
		font-weight: 600;
		font-size: 0.8125rem;
		color: var(--color-text-source);
	}

	.message-time {
		font-size: 0.75rem;
		color: var(--color-text-hint);
	}

	.message-bubble {
		padding: 0.875rem 1rem;
	}

	.message-text {
		font-size: 0.9375rem;
		line-height: 1.6;
		color: var(--color-text-manifest);
	}

	/* Input area */
	.input-area {
		padding: 0.75rem 1.5rem 1.5rem;
		background: var(--color-field-void);
		position: relative;
	}

	.input-area.drag-over {
		background: var(--color-primary-50);
	}

	[data-theme='dark'] .input-area.drag-over {
		background: rgba(15, 76, 117, 0.1);
	}

	.hidden-input {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		border: 0;
	}

	/* Attached files */
	.attached-files {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
	}

	.file-chip {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.5rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		font-size: 0.75rem;
		animation: fadeIn 0.15s ease;
	}

	.file-icon {
		font-size: 0.875rem;
	}

	.file-name {
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--color-text-source);
	}

	.file-size {
		color: var(--color-text-hint);
	}

	.remove-file {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 18px;
		height: 18px;
		padding: 0;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 50%;
		transition: all 0.15s ease;
	}

	.remove-file:hover {
		background: var(--color-error-100);
		color: var(--color-error-500);
	}

	/* Attach button */
	.attach-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		padding: 0;
		background: none;
		border: none;
		color: var(--color-text-whisper);
		cursor: pointer;
		border-radius: 0.5rem;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.attach-btn:hover:not(:disabled) {
		background: var(--color-field-depth);
		color: var(--color-primary-500);
	}

	.attach-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Drag overlay */
	.drag-overlay {
		position: absolute;
		inset: 0;
		background: rgba(15, 76, 117, 0.95);
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 0.75rem;
		z-index: 10;
	}

	.drag-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
		color: white;
	}

	.drag-content p {
		font-size: 1rem;
		font-weight: 500;
	}

	.input-controls {
		margin-bottom: 0.75rem;
	}

	.model-select {
		padding: 0.5rem 0.75rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.5rem;
		color: var(--color-text-manifest);
		font-size: 0.75rem;
		cursor: pointer;
	}

	.model-select:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.input-container {
		display: flex;
		align-items: flex-end;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
	}

	.input-container textarea {
		flex: 1;
		border: none;
		background: transparent;
		resize: none;
		font-size: 0.9375rem;
		line-height: 1.5;
		color: var(--color-text-source);
		min-height: 24px;
		max-height: 200px;
		font-family: inherit;
	}

	.input-container textarea:focus {
		outline: none;
	}

	.input-container textarea::placeholder {
		color: var(--color-text-hint);
	}

	.input-container textarea:disabled {
		opacity: 0.6;
	}

	.input-actions {
		display: flex;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.conversations-panel {
			display: none;
		}

		.messages-container {
			padding: 1rem;
		}

		.message-content {
			max-width: 85%;
		}

		.input-area {
			padding: 0.75rem 1rem 1rem;
		}

		.starter-prompts {
			flex-direction: column;
		}

		.starter-prompt {
			width: 100%;
		}
	}
</style>
