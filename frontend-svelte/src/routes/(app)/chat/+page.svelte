<script lang="ts">
	import { onMount, tick } from 'svelte';
	import {
		chat,
		messages,
		currentConversation,
		conversations,
		isStreaming,
		addToast
	} from '$lib/stores';

	// Accept SvelteKit props
	export let data: Record<string, unknown> = {};
	let _restProps = $$restProps;

	let messageInput = '';
	let messagesContainer: HTMLElement;
	let selectedModel = 'gpt-4.1';

	const models = [
		{ id: 'gpt-4.1', name: 'GPT-4.1' },
		{ id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini' },
		{ id: 'gpt-4.5-preview', name: 'GPT-4.5 Preview' },
		{ id: 'claude-sonnet-4-20250514', name: 'Claude Sonnet 4' },
		{ id: 'claude-opus-4-20250514', name: 'Claude Opus 4' },
		{ id: 'o3', name: 'o3' },
		{ id: 'o4-mini', name: 'o4 Mini' },
	];

	onMount(async () => {
		await chat.loadConversations();
	});

	// Auto-scroll to bottom when new messages arrive
	$: if ($messages.length > 0 && messagesContainer) {
		tick().then(() => {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		});
	}

	async function handleSendMessage() {
		if (!messageInput.trim() || $isStreaming) return;

		const content = messageInput.trim();
		messageInput = '';

		try {
			await chat.sendMessage(content, selectedModel);
		} catch (error: any) {
			addToast('error', 'Error', error.message || 'Failed to send message');
		}
	}

	async function handleNewChat() {
		chat.clearCurrentConversation();
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

	function formatTimestamp(date: Date) {
		return new Intl.DateTimeFormat('en-US', {
			hour: 'numeric',
			minute: '2-digit',
			hour12: true,
		}).format(date);
	}
</script>

<svelte:head>
	<title>Chat | Reality Transformer</title>
</svelte:head>

<div class="chat-layout">
	<!-- Conversation sidebar -->
	<div class="conversations-panel">
		<div class="panel-header">
			<h3>Conversations</h3>
			<button class="new-chat-btn" on:click={handleNewChat}>
				<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M12 5v14"/>
					<path d="M5 12h14"/>
				</svg>
				New Chat
			</button>
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
	</div>

	<!-- Main chat area -->
	<div class="chat-main">
		<!-- Messages -->
		<div class="messages-container" bind:this={messagesContainer}>
			{#if $messages.length === 0}
				<div class="welcome-screen">
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
					<div class="message" class:user={message.role === 'user'} class:assistant={message.role === 'assistant'}>
						<div class="message-avatar">
							{#if message.role === 'user'}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
									<circle cx="12" cy="7" r="4"/>
								</svg>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M12 8V4H8"/>
									<rect width="16" height="12" x="4" y="8" rx="2"/>
									<path d="M2 14h2"/>
									<path d="M20 14h2"/>
									<path d="M15 13v2"/>
									<path d="M9 13v2"/>
								</svg>
							{/if}
						</div>
						<div class="message-content">
							<div class="message-header">
								<span class="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
								<span class="message-time">{formatTimestamp(message.createdAt)}</span>
							</div>
							<div class="message-text">
								{message.content}
							</div>
						</div>
					</div>
				{/each}

				{#if $isStreaming}
					<div class="message assistant">
						<div class="message-avatar">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M12 8V4H8"/>
								<rect width="16" height="12" x="4" y="8" rx="2"/>
								<path d="M2 14h2"/>
								<path d="M20 14h2"/>
								<path d="M15 13v2"/>
								<path d="M9 13v2"/>
							</svg>
						</div>
						<div class="message-content">
							<div class="typing-indicator">
								<span></span>
								<span></span>
								<span></span>
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

			<div class="input-wrapper">
				<textarea
					bind:value={messageInput}
					on:keydown={handleKeyDown}
					placeholder="Type your message..."
					rows="1"
					disabled={$isStreaming}
				></textarea>
				<button
					class="send-btn"
					on:click={handleSendMessage}
					disabled={!messageInput.trim() || $isStreaming}
				>
					{#if $isStreaming}
						<div class="spinner-small"></div>
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="m22 2-7 20-4-9-9-4Z"/>
							<path d="M22 2 11 13"/>
						</svg>
					{/if}
				</button>
			</div>
		</div>
	</div>
</div>

<style>
	.chat-layout {
		display: flex;
		height: 100%;
	}

	/* Conversations panel */
	.conversations-panel {
		width: 280px;
		background: hsl(var(--card));
		border-right: 1px solid hsl(var(--border));
		display: flex;
		flex-direction: column;
	}

	.panel-header {
		padding: 1rem;
		border-bottom: 1px solid hsl(var(--border));
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.panel-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: hsl(var(--muted-foreground));
	}

	.new-chat-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		background: hsl(var(--primary));
		color: hsl(var(--primary-foreground));
		border: none;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.new-chat-btn:hover {
		opacity: 0.9;
	}

	.conversations-list {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.conversation-item {
		width: 100%;
		padding: 0.75rem;
		background: none;
		border: none;
		border-radius: 0.5rem;
		text-align: left;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.conversation-item:hover {
		background: hsl(var(--accent));
	}

	.conversation-item.active {
		background: hsl(var(--accent));
	}

	.conversation-title {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: hsl(var(--foreground));
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.conversation-time {
		display: block;
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
		margin-top: 0.25rem;
	}

	.empty-conversations {
		padding: 2rem 1rem;
		text-align: center;
	}

	.empty-conversations p {
		font-size: 0.875rem;
		color: hsl(var(--muted-foreground));
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
	}

	.welcome-screen h2 {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	.welcome-screen p {
		color: hsl(var(--muted-foreground));
		margin-bottom: 2rem;
	}

	.starter-prompts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
		justify-content: center;
		max-width: 600px;
	}

	.starter-prompt {
		padding: 0.75rem 1rem;
		background: hsl(var(--card));
		border: 1px solid hsl(var(--border));
		border-radius: 0.5rem;
		color: hsl(var(--foreground));
		font-size: 0.875rem;
		cursor: pointer;
		transition: border-color 0.2s, background-color 0.2s;
	}

	.starter-prompt:hover {
		border-color: hsl(var(--primary));
		background: hsl(var(--accent));
	}

	/* Messages */
	.message {
		display: flex;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.message-avatar {
		width: 36px;
		height: 36px;
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.message.user .message-avatar {
		background: hsl(var(--primary));
		color: hsl(var(--primary-foreground));
	}

	.message.assistant .message-avatar {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.message-content {
		flex: 1;
		min-width: 0;
	}

	.message-header {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		margin-bottom: 0.25rem;
	}

	.message-role {
		font-weight: 600;
		font-size: 0.875rem;
	}

	.message-time {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
	}

	.message-text {
		font-size: 0.9375rem;
		line-height: 1.6;
		white-space: pre-wrap;
	}

	/* Typing indicator */
	.typing-indicator {
		display: flex;
		gap: 0.25rem;
		padding: 0.5rem 0;
	}

	.typing-indicator span {
		width: 8px;
		height: 8px;
		background: hsl(var(--muted-foreground));
		border-radius: 50%;
		animation: bounce 1.4s infinite ease-in-out both;
	}

	.typing-indicator span:nth-child(1) {
		animation-delay: -0.32s;
	}

	.typing-indicator span:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}

	/* Input area */
	.input-area {
		padding: 1rem 1.5rem;
		border-top: 1px solid hsl(var(--border));
		background: hsl(var(--card));
	}

	.input-controls {
		margin-bottom: 0.75rem;
	}

	.model-select {
		padding: 0.5rem 0.75rem;
		background: hsl(var(--background));
		border: 1px solid hsl(var(--border));
		border-radius: 0.375rem;
		color: hsl(var(--foreground));
		font-size: 0.75rem;
		cursor: pointer;
	}

	.input-wrapper {
		display: flex;
		gap: 0.75rem;
		align-items: flex-end;
	}

	.input-wrapper textarea {
		flex: 1;
		padding: 0.75rem 1rem;
		background: hsl(var(--background));
		border: 1px solid hsl(var(--border));
		border-radius: 0.5rem;
		color: hsl(var(--foreground));
		font-size: 0.9375rem;
		resize: none;
		min-height: 44px;
		max-height: 200px;
		line-height: 1.5;
	}

	.input-wrapper textarea:focus {
		outline: none;
		border-color: hsl(var(--ring));
	}

	.input-wrapper textarea:disabled {
		opacity: 0.6;
	}

	.send-btn {
		padding: 0.75rem;
		background: hsl(var(--primary));
		color: hsl(var(--primary-foreground));
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.send-btn:hover:not(:disabled) {
		opacity: 0.9;
	}

	.send-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.spinner-small {
		width: 20px;
		height: 20px;
		border: 2px solid transparent;
		border-top-color: currentColor;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
