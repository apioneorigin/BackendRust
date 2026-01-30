<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth, addToast } from '$lib/stores';
	import { Button, Spinner } from '$lib/components/ui';

	let email = '';
	let password = '';
	let isLoading = false;
	let error = '';

	async function handleSubmit() {
		error = '';
		isLoading = true;

		try {
			const success = await auth.login(email, password);
			if (success) {
				addToast('success', 'Welcome back!');
				goto('/chat');
			} else {
				error = 'Invalid email or password';
			}
		} catch (e: any) {
			error = e.message || 'Login failed';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Login | Reality Transformer</title>
</svelte:head>

<div class="auth-container">
	<div class="auth-card card-elevated">
		<div class="auth-logo">
			<div class="logo-icon">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="32"
					height="32"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
				</svg>
			</div>
			<span class="logo-text">Reality Transformer</span>
		</div>

		<div class="auth-header">
			<h1>Welcome back</h1>
			<p>Sign in to continue your transformation journey</p>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="auth-form">
			{#if error}
				<div class="error-message" role="alert">
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
						<circle cx="12" cy="12" r="10" />
						<line x1="12" x2="12" y1="8" y2="12" />
						<line x1="12" x2="12.01" y1="16" y2="16" />
					</svg>
					{error}
				</div>
			{/if}

			<div class="form-group">
				<label for="email">Email</label>
				<input
					type="email"
					id="email"
					bind:value={email}
					placeholder="you@example.com"
					required
					disabled={isLoading}
					class="input-field"
				/>
			</div>

			<div class="form-group">
				<label for="password">Password</label>
				<input
					type="password"
					id="password"
					bind:value={password}
					placeholder="Enter your password"
					required
					disabled={isLoading}
					class="input-field"
				/>
			</div>

			<Button variant="primary" type="submit" fullWidth loading={isLoading}>
				{isLoading ? 'Signing in...' : 'Sign In'}
			</Button>
		</form>

		<div class="auth-footer">
			<p>
				Don't have an account?
				<a href="/register">Create one</a>
			</p>
		</div>
	</div>
</div>

<style>
	.auth-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100dvh;
		padding: 1.5rem;
		background: var(--color-field-void);
		background-image: var(--gradient-field-presence);
	}

	.auth-card {
		width: 100%;
		max-width: 420px;
		padding: 2.5rem;
	}

	.auth-logo {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		margin-bottom: 2rem;
	}

	.logo-icon {
		width: 48px;
		height: 48px;
		background: var(--gradient-primary);
		border-radius: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}

	.logo-text {
		font-size: 1.25rem;
		font-weight: 700;
		background: var(--gradient-primary);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.auth-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.auth-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.auth-header p {
		color: var(--color-text-whisper);
		font-size: 0.9375rem;
	}

	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-manifest);
	}

	.input-field {
		padding: 0.875rem 1rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.75rem;
		color: var(--color-text-source);
		font-size: 0.9375rem;
		transition:
			border-color 0.15s ease,
			box-shadow 0.15s ease;
	}

	.input-field:focus {
		outline: none;
		border-color: var(--color-primary-400);
		box-shadow: 0 0 0 3px rgba(15, 76, 117, 0.1);
	}

	.input-field:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.input-field::placeholder {
		color: var(--color-text-hint);
	}

	.error-message {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.875rem 1rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid var(--color-error-500);
		border-radius: 0.75rem;
		color: var(--color-error-500);
		font-size: 0.875rem;
	}

	.auth-footer {
		margin-top: 2rem;
		padding-top: 1.5rem;
		border-top: 1px solid var(--color-veil-thin);
		text-align: center;
		font-size: 0.875rem;
		color: var(--color-text-whisper);
	}

	.auth-footer a {
		color: var(--color-primary-500);
		text-decoration: none;
		font-weight: 500;
		transition: color 0.15s ease;
	}

	.auth-footer a:hover {
		color: var(--color-primary-600);
		text-decoration: underline;
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.auth-card {
			padding: 1.5rem;
		}
	}
</style>
