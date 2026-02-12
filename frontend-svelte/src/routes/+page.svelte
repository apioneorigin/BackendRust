<div class="loading-container">
	<div class="spinner"></div>
</div>

<style>
	.loading-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid hsl(var(--muted));
		border-top-color: hsl(var(--primary));
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
