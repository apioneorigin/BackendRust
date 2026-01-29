<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth, addToast } from '$lib/stores';

	let name = '';
	let email = '';
	let password = '';
	let confirmPassword = '';
	let isLoading = false;
	let error = '';

	async function handleSubmit() {
		error = '';

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (password.length < 8) {
			error = 'Password must be at least 8 characters';
			return;
		}

		isLoading = true;

		try {
			const success = await auth.register(email, password, name || undefined);
			if (success) {
				addToast('success', 'Welcome!', 'Your account has been created');
				goto('/chat');
			} else {
				error = 'Registration failed';
			}
		} catch (e: any) {
			error = e.message || 'Registration failed';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Register | Reality Transformer</title>
</svelte:head>

<div class="auth-container">
	<div class="auth-card">
		<div class="auth-header">
			<h1>Create Account</h1>
			<p>Start your transformation journey today</p>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="auth-form">
			{#if error}
				<div class="error-message" role="alert">
					{error}
				</div>
			{/if}

			<div class="form-group">
				<label for="name">Name (optional)</label>
				<input
					type="text"
					id="name"
					bind:value={name}
					placeholder="Your name"
					disabled={isLoading}
				/>
			</div>

			<div class="form-group">
				<label for="email">Email</label>
				<input
					type="email"
					id="email"
					bind:value={email}
					placeholder="you@example.com"
					required
					disabled={isLoading}
				/>
			</div>

			<div class="form-group">
				<label for="password">Password</label>
				<input
					type="password"
					id="password"
					bind:value={password}
					placeholder="At least 8 characters"
					required
					disabled={isLoading}
				/>
			</div>

			<div class="form-group">
				<label for="confirmPassword">Confirm Password</label>
				<input
					type="password"
					id="confirmPassword"
					bind:value={confirmPassword}
					placeholder="Confirm your password"
					required
					disabled={isLoading}
				/>
			</div>

			<button type="submit" class="btn-primary" disabled={isLoading}>
				{#if isLoading}
					<span class="spinner-small"></span>
					Creating account...
				{:else}
					Create Account
				{/if}
			</button>
		</form>

		<div class="auth-footer">
			<p>
				Already have an account?
				<a href="/login">Sign in</a>
			</p>
		</div>
	</div>
</div>

<style>
	.auth-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		padding: 1rem;
		background: linear-gradient(135deg, hsl(var(--background)) 0%, hsl(var(--muted)) 100%);
	}

	.auth-card {
		width: 100%;
		max-width: 400px;
		padding: 2rem;
		background: hsl(var(--card));
		border: 1px solid hsl(var(--border));
		border-radius: 1rem;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
	}

	.auth-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.auth-header h1 {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	.auth-header p {
		color: hsl(var(--muted-foreground));
		font-size: 0.875rem;
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
		font-size: 0.875rem;
		font-weight: 500;
	}

	.form-group input {
		padding: 0.75rem 1rem;
		border: 1px solid hsl(var(--border));
		border-radius: 0.5rem;
		background: hsl(var(--background));
		color: hsl(var(--foreground));
		font-size: 1rem;
		transition: border-color 0.2s, box-shadow 0.2s;
	}

	.form-group input:focus {
		outline: none;
		border-color: hsl(var(--ring));
		box-shadow: 0 0 0 3px hsl(var(--ring) / 0.1);
	}

	.form-group input:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-primary {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: hsl(var(--primary));
		color: hsl(var(--primary-foreground));
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.btn-primary:hover:not(:disabled) {
		opacity: 0.9;
	}

	.btn-primary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.spinner-small {
		width: 16px;
		height: 16px;
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

	.error-message {
		padding: 0.75rem 1rem;
		background: hsl(0 84% 60% / 0.1);
		border: 1px solid hsl(0 84% 60%);
		border-radius: 0.5rem;
		color: hsl(0 84% 60%);
		font-size: 0.875rem;
	}

	.auth-footer {
		margin-top: 1.5rem;
		text-align: center;
		font-size: 0.875rem;
		color: hsl(var(--muted-foreground));
	}

	.auth-footer a {
		color: hsl(var(--primary));
		text-decoration: none;
		font-weight: 500;
	}

	.auth-footer a:hover {
		text-decoration: underline;
	}
</style>
