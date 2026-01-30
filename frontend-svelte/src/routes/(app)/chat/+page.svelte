<script lang="ts">
	import { onMount, tick } from 'svelte';
	import {
		chat,
		messages,
		currentConversation,
		conversations,
		isStreaming,
		streamingContent,
		addToast
	} from '$lib/stores';
	import { Button, Spinner, TypingIndicator } from '$lib/components/ui';

	let messageInput = '';
	let messagesContainer: HTMLElement;
	let inputElement: HTMLTextAreaElement;
	let selectedModel = 'gpt-4.1';

	const models = [
		{ id: 'gpt-4.1', name: 'GPT-4.1' },
		{ id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini' },
		{ id: 'gpt-4.5-preview', name: 'GPT-4.5 Preview' },
		{ id: 'claude-sonnet-4-20250514', name: 'Claude Sonnet 4' },
		{ id: 'claude-opus-4-20250514', name: 'Claude Opus 4' },
		{ id: 'o3', name: 'o3' },
		{ id: 'o4-mini', name: 'o4 Mini' }
	];

	onMount(async () => {
		await chat.loadConversations();
	});

	// Auto-scroll when new messages or streaming
	$: if (($messages.length > 0 || $streamingContent) && messagesContainer) {
		tick().then(() => {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		});
	}

	async function handleSendMessage() {
		if (!messageInput.trim() || $isStreaming) return;

		const content = messageInput.trim();
		messageInput = '';

		// Reset textarea height
		if (inputElement) {
			inputElement.style.height = 'auto';
		}

		try {
			await chat.sendMessage(content, selectedModel);
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
					<div class="welcome-icon">
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
							<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
						</svg>
					</div>
					<h2>Welcome to Reality Transformer</h2>
					<p>Start a conversation to transform your goals into reality</p>

					<div class="starter-prompts">
						<button
							class="starter-prompt"
							on:click={() => {
								messageInput = 'Help me define and clarify my goals';
								handleSendMessage();
							}}
						>
							Help me define my goals
						</button>
						<button
							class="starter-prompt"
							on:click={() => {
								messageInput = 'I want to create a transformation plan';
								handleSendMessage();
							}}
						>
							Create a transformation plan
						</button>
						<button
							class="starter-prompt"
							on:click={() => {
								messageInput = 'Guide me through the discovery process';
								handleSendMessage();
							}}
						>
							Start discovery process
						</button>
					</div>
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
		<div class="input-area">
			<div class="input-controls">
				<select bind:value={selectedModel} class="model-select">
					{#each models as model}
						<option value={model.id}>{model.name}</option>
					{/each}
				</select>
			</div>

			<div class="input-container input-premium">
				<textarea
					bind:this={inputElement}
					bind:value={messageInput}
					on:keydown={handleKeyDown}
					on:input={handleInput}
					placeholder="Type your message..."
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
							disabled={!messageInput.trim()}
						>
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
								<path d="m22 2-7 20-4-9-9-4Z" />
								<path d="M22 2 11 13" />
							</svg>
							Send
						</Button>
					{/if}
				</div>
			</div>
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

	/* Welcome screen */
	.welcome-screen {
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		padding: 2rem;
		gap: 1rem;
	}

	.welcome-icon {
		width: 80px;
		height: 80px;
		background: var(--color-field-depth);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-primary-500);
		margin-bottom: 0.5rem;
	}

	.welcome-screen h2 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
	}

	.welcome-screen p {
		color: var(--color-text-whisper);
		max-width: 400px;
	}

	.starter-prompts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
		justify-content: center;
		max-width: 600px;
		margin-top: 1rem;
	}

	.starter-prompt {
		padding: 0.75rem 1rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.75rem;
		color: var(--color-text-manifest);
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.starter-prompt:hover {
		border-color: var(--color-primary-400);
		background: var(--color-field-depth);
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
