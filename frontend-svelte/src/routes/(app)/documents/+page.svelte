<script lang="ts">
	import { onMount } from 'svelte';
	import { documents, documentList, addToast } from '$lib/stores';
	import type { Document } from '$lib/stores/documents';
	import { Button, Spinner } from '$lib/components/ui';

	let domainFilter = '';
	let isLoading = true;
	let searchQuery = '';

	onMount(async () => {
		await documents.loadDocuments();
		isLoading = false;
	});

	$: filteredDocs = $documentList.filter((d) => {
		const matchesDomain = !domainFilter || d.domain === domainFilter;
		const matchesSearch =
			!searchQuery ||
			d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
			d.goalTitle?.toLowerCase().includes(searchQuery.toLowerCase());
		return matchesDomain && matchesSearch;
	});

	$: domains = [...new Set($documentList.map((d) => d.domain).filter(Boolean))];

	async function handleDeleteDocument(docId: string) {
		if (confirm('Are you sure you want to delete this document?')) {
			await documents.deleteDocument(docId);
			addToast('info', 'Document deleted');
		}
	}

	function formatDate(date: Date) {
		return new Intl.DateTimeFormat('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		}).format(date);
	}

	function formatRelativeTime(date: Date) {
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const minutes = Math.floor(diff / 60000);
		const hours = Math.floor(diff / 3600000);
		const days = Math.floor(diff / 86400000);

		if (minutes < 1) return 'Just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days < 7) return `${days}d ago`;
		return formatDate(date);
	}
</script>

<svelte:head>
	<title>Documents | Reality Transformer</title>
</svelte:head>

<div class="documents-page">
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
					<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
					<polyline points="14 2 14 8 20 8" />
				</svg>
			</div>
			<div>
				<h1>Documents</h1>
				<p>Your transformation documents and outputs</p>
			</div>
		</div>
		<div class="header-stats">
			<div class="stat-item">
				<span class="stat-value">{$documentList.length}</span>
				<span class="stat-label">Total</span>
			</div>
			<div class="stat-item">
				<span class="stat-value">{domains.length}</span>
				<span class="stat-label">Domains</span>
			</div>
		</div>
	</header>

	<!-- Filters -->
	<div class="filters-section">
		<div class="search-box">
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
				<circle cx="11" cy="11" r="8" />
				<path d="m21 21-4.3-4.3" />
			</svg>
			<input type="text" placeholder="Search documents..." bind:value={searchQuery} />
		</div>

		{#if domains.length > 0}
			<select bind:value={domainFilter} class="domain-filter">
				<option value="">All domains</option>
				{#each domains as domain}
					<option value={domain}>{domain}</option>
				{/each}
			</select>
		{/if}
	</div>

	<!-- Documents grid -->
	{#if isLoading}
		<div class="loading-state">
			<Spinner size="lg" />
			<p>Loading documents...</p>
		</div>
	{:else if filteredDocs.length === 0}
		<div class="empty-state">
			<div class="empty-icon">
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
					<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
					<polyline points="14 2 14 8 20 8" />
					<line x1="16" x2="8" y1="13" y2="13" />
					<line x1="16" x2="8" y1="17" y2="17" />
					<line x1="10" x2="8" y1="9" y2="9" />
				</svg>
			</div>
			<h3>No documents yet</h3>
			<p>Documents will appear here as you complete transformations</p>
			<a href="/chat" class="empty-action">
				<Button variant="primary">Start a conversation</Button>
			</a>
		</div>
	{:else}
		<div class="documents-grid">
			{#each filteredDocs as doc (doc.id)}
				<div class="document-card">
					<div class="card-header">
						<div class="document-icon">
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
								<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
								<polyline points="14 2 14 8 20 8" />
							</svg>
						</div>
						{#if doc.domain}
							<span class="document-domain">{doc.domain}</span>
						{/if}
					</div>

					<div class="card-body">
						<h3 class="document-title">{doc.title}</h3>
						{#if doc.goalTitle}
							<p class="document-goal">{doc.goalTitle}</p>
						{/if}
					</div>

					<div class="card-footer">
						<span class="document-date" title={formatDate(doc.lastUpdatedAt)}>
							{formatRelativeTime(doc.lastUpdatedAt)}
						</span>
						<div class="document-actions">
							<a href="/documents/{doc.id}" class="action-btn view-btn">
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
									<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
									<circle cx="12" cy="12" r="3" />
								</svg>
								View
							</a>
							<button class="action-btn delete-btn" on:click={() => handleDeleteDocument(doc.id)}>
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
									<path d="M3 6h18" />
									<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
									<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
								</svg>
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.documents-page {
		padding: 1.5rem;
		max-width: 1200px;
		margin: 0 auto;
		animation: fadeIn 0.2s ease;
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

	/* Filters */
	.filters-section {
		display: flex;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.search-box {
		flex: 1;
		max-width: 400px;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.625rem;
		transition: border-color 0.15s ease, box-shadow 0.15s ease;
	}

	.search-box:focus-within {
		border-color: var(--color-primary-400);
		box-shadow: 0 0 0 3px var(--color-primary-100);
	}

	[data-theme='dark'] .search-box:focus-within {
		box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.3);
	}

	.search-box svg {
		color: var(--color-text-hint);
		flex-shrink: 0;
	}

	.search-box input {
		flex: 1;
		border: none;
		background: transparent;
		color: var(--color-text-source);
		font-size: 0.875rem;
		outline: none;
	}

	.search-box input::placeholder {
		color: var(--color-text-hint);
	}

	.domain-filter {
		padding: 0.75rem 1rem;
		background: var(--color-field-surface);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.625rem;
		color: var(--color-text-manifest);
		font-size: 0.875rem;
		cursor: pointer;
		transition: border-color 0.15s ease;
	}

	.domain-filter:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	/* Loading state */
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

	/* Empty state */
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

	.empty-action {
		text-decoration: none;
	}

	/* Documents grid */
	.documents-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 1rem;
	}

	.document-card {
		display: flex;
		flex-direction: column;
		padding: 1.25rem;
		background: var(--color-field-surface);
		box-shadow: var(--shadow-elevated);
		border-radius: 12px;
		transition: transform 0.15s ease, box-shadow 0.15s ease;
	}

	.document-card:hover {
		transform: translateY(-2px);
	}

	.card-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.document-icon {
		width: 40px;
		height: 40px;
		background: var(--color-primary-50);
		border-radius: 0.625rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-primary-500);
	}

	[data-theme='dark'] .document-icon {
		background: var(--color-primary-900);
		color: var(--color-primary-300);
	}

	.document-domain {
		padding: 0.25rem 0.75rem;
		background: var(--color-accent);
		color: white;
		border-radius: 9999px;
		font-size: 0.6875rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}

	.card-body {
		flex: 1;
		margin-bottom: 1rem;
	}

	.document-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 0.375rem;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.document-goal {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.card-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-top: 1rem;
		border-top: 1px solid var(--color-veil-thin);
	}

	.document-date {
		font-size: 0.75rem;
		color: var(--color-text-hint);
	}

	.document-actions {
		display: flex;
		gap: 0.5rem;
	}

	.action-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.75rem;
		border-radius: 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
		text-decoration: none;
	}

	.view-btn {
		background: var(--color-primary-500);
		color: white;
		border: none;
	}

	.view-btn:hover {
		background: var(--color-primary-600);
	}

	.delete-btn {
		background: transparent;
		border: 1px solid var(--color-veil-soft);
		color: var(--color-text-whisper);
	}

	.delete-btn:hover {
		border-color: var(--color-error-400);
		color: var(--color-error-500);
		background: var(--color-error-50);
	}

	[data-theme='dark'] .delete-btn:hover {
		background: rgba(239, 68, 68, 0.1);
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.documents-page {
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

		.filters-section {
			flex-direction: column;
		}

		.search-box {
			max-width: none;
		}

		.documents-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
