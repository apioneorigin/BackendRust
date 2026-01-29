<script lang="ts">
	import { onMount } from 'svelte';
	import { documents, documentList, addToast } from '$lib/stores';
	import type { Document } from '$lib/stores/documents';

	// Accept SvelteKit props
	export let data: Record<string, unknown> = {};
	let _restProps = $$restProps;

	let domainFilter = '';

	onMount(async () => {
		await documents.loadDocuments();
	});

	$: filteredDocs = domainFilter
		? $documentList.filter(d => d.domain === domainFilter)
		: $documentList;

	$: domains = [...new Set($documentList.map(d => d.domain).filter(Boolean))];

	async function handleDeleteDocument(docId: string) {
		if (confirm('Are you sure you want to delete this document?')) {
			await documents.deleteDocument(docId);
			addToast('info', 'Document deleted', 'The document has been removed');
		}
	}

	function formatDate(date: Date) {
		return new Intl.DateTimeFormat('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		}).format(date);
	}
</script>

<svelte:head>
	<title>Documents | Reality Transformer</title>
</svelte:head>

<div class="documents-page">
	<header class="page-header">
		<div>
			<h1>Documents</h1>
			<p>Your transformation documents and outputs</p>
		</div>
	</header>

	<!-- Filters -->
	{#if domains.length > 0}
		<div class="filters">
			<select bind:value={domainFilter}>
				<option value="">All domains</option>
				{#each domains as domain}
					<option value={domain}>{domain}</option>
				{/each}
			</select>
		</div>
	{/if}

	<!-- Documents grid -->
	<div class="documents-grid">
		{#if filteredDocs.length === 0}
			<div class="empty-state">
				<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
					<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
					<polyline points="14 2 14 8 20 8"/>
				</svg>
				<h3>No documents yet</h3>
				<p>Documents will appear here as you complete transformations</p>
			</div>
		{:else}
			{#each filteredDocs as doc (doc.id)}
				<div class="document-card">
					<div class="document-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
							<polyline points="14 2 14 8 20 8"/>
						</svg>
					</div>

					<div class="document-info">
						<h3 class="document-title">{doc.title}</h3>
						{#if doc.goalTitle}
							<p class="document-goal">Goal: {doc.goalTitle}</p>
						{/if}
						<div class="document-meta">
							{#if doc.domain}
								<span class="document-domain">{doc.domain}</span>
							{/if}
							<span class="document-date">Updated {formatDate(doc.lastUpdatedAt)}</span>
						</div>
					</div>

					<div class="document-actions">
						<a href="/documents/{doc.id}" class="btn-view">View</a>
						<button class="btn-delete" on:click={() => handleDeleteDocument(doc.id)}>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M3 6h18"/>
								<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
								<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
							</svg>
						</button>
					</div>
				</div>
			{/each}
		{/if}
	</div>
</div>

<style>
	.documents-page {
		padding: 1.5rem;
		max-width: 1000px;
		margin: 0 auto;
	}

	.page-header {
		margin-bottom: 1.5rem;
	}

	.page-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: 0.25rem;
	}

	.page-header p {
		color: hsl(var(--muted-foreground));
		font-size: 0.875rem;
	}

	.filters {
		margin-bottom: 1.5rem;
	}

	.filters select {
		padding: 0.5rem 0.75rem;
		background: hsl(var(--background));
		border: 1px solid hsl(var(--border));
		border-radius: 0.375rem;
		color: hsl(var(--foreground));
		font-size: 0.875rem;
	}

	.documents-grid {
		display: grid;
		gap: 1rem;
	}

	.document-card {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: hsl(var(--card));
		border: 1px solid hsl(var(--border));
		border-radius: 0.75rem;
		transition: border-color 0.2s;
	}

	.document-card:hover {
		border-color: hsl(var(--primary) / 0.5);
	}

	.document-icon {
		width: 48px;
		height: 48px;
		background: hsl(var(--accent));
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: hsl(var(--primary));
		flex-shrink: 0;
	}

	.document-info {
		flex: 1;
		min-width: 0;
	}

	.document-title {
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: 0.25rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.document-goal {
		font-size: 0.8125rem;
		color: hsl(var(--muted-foreground));
		margin-bottom: 0.25rem;
	}

	.document-meta {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
	}

	.document-domain {
		padding: 0.125rem 0.5rem;
		background: hsl(var(--accent));
		border-radius: 9999px;
	}

	.document-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.btn-view {
		padding: 0.5rem 1rem;
		background: hsl(var(--primary));
		color: hsl(var(--primary-foreground));
		border: none;
		border-radius: 0.375rem;
		font-size: 0.8125rem;
		font-weight: 500;
		text-decoration: none;
	}

	.btn-delete {
		padding: 0.5rem;
		background: none;
		border: 1px solid hsl(var(--border));
		border-radius: 0.375rem;
		color: hsl(var(--muted-foreground));
		cursor: pointer;
	}

	.btn-delete:hover {
		color: hsl(0 84% 60%);
		border-color: hsl(0 84% 60%);
	}

	.empty-state {
		text-align: center;
		padding: 3rem;
		color: hsl(var(--muted-foreground));
	}

	.empty-state svg {
		margin-bottom: 1rem;
		opacity: 0.5;
	}

	.empty-state h3 {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: hsl(var(--foreground));
	}
</style>
