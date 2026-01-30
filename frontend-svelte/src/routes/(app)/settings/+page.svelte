<script lang="ts">
	import { user, auth, theme, addToast, credits } from '$lib/stores';
	import { Button, Card, Spinner } from '$lib/components/ui';
	import { api } from '$lib/utils/api';

	let isLoading = false;
	let isSaving = false;
	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';

	// User preferences
	let displayName = $user?.name || '';
	let emailNotifications = true;

	async function handleChangePassword() {
		if (!currentPassword || !newPassword || !confirmPassword) {
			addToast('error', 'Please fill in all password fields');
			return;
		}

		if (newPassword !== confirmPassword) {
			addToast('error', 'New passwords do not match');
			return;
		}

		if (newPassword.length < 8) {
			addToast('error', 'Password must be at least 8 characters');
			return;
		}

		isSaving = true;
		try {
			await api.post('/api/auth/change-password', {
				current_password: currentPassword,
				new_password: newPassword
			});
			addToast('success', 'Password changed successfully');
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		} catch (error: any) {
			addToast('error', error.message || 'Failed to change password');
		} finally {
			isSaving = false;
		}
	}

	async function handleUpdateProfile() {
		isSaving = true;
		try {
			await api.patch('/api/user/preferences', {
				name: displayName,
				email_notifications: emailNotifications
			});
			addToast('success', 'Profile updated successfully');
		} catch (error: any) {
			addToast('error', error.message || 'Failed to update profile');
		} finally {
			isSaving = false;
		}
	}

	function toggleTheme() {
		theme.toggle();
	}
</script>

<svelte:head>
	<title>Settings | Reality Transformer</title>
</svelte:head>

<div class="settings-page">
	<div class="settings-header">
		<h1>Settings</h1>
		<p>Manage your account preferences and security</p>
	</div>

	<div class="settings-content">
		<!-- Profile Section -->
		<section class="settings-section">
			<h2>Profile</h2>
			<Card variant="default" padding="lg">
				<div class="form-group">
					<label for="email">Email</label>
					<input
						type="email"
						id="email"
						value={$user?.email || ''}
						disabled
						class="input-field disabled"
					/>
					<p class="help-text">Your email cannot be changed</p>
				</div>

				<div class="form-group">
					<label for="displayName">Display Name</label>
					<input
						type="text"
						id="displayName"
						bind:value={displayName}
						placeholder="Enter your display name"
						class="input-field"
					/>
				</div>

				<div class="form-actions">
					<Button variant="primary" on:click={handleUpdateProfile} loading={isSaving}>
						Save Changes
					</Button>
				</div>
			</Card>
		</section>

		<!-- Appearance Section -->
		<section class="settings-section">
			<h2>Appearance</h2>
			<Card variant="default" padding="lg">
				<div class="setting-row">
					<div class="setting-info">
						<h3>Theme</h3>
						<p>Choose between light and dark mode</p>
					</div>
					<div class="setting-control">
						<button class="theme-toggle" on:click={toggleTheme}>
							{#if $theme.isDark}
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
									<circle cx="12" cy="12" r="4" />
									<path d="M12 2v2" />
									<path d="M12 20v2" />
									<path d="m4.93 4.93 1.41 1.41" />
									<path d="m17.66 17.66 1.41 1.41" />
									<path d="M2 12h2" />
									<path d="M20 12h2" />
									<path d="m6.34 17.66-1.41 1.41" />
									<path d="m19.07 4.93-1.41 1.41" />
								</svg>
								<span>Light Mode</span>
							{:else}
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
									<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
								</svg>
								<span>Dark Mode</span>
							{/if}
						</button>
					</div>
				</div>
			</Card>
		</section>

		<!-- Security Section -->
		<section class="settings-section">
			<h2>Security</h2>
			<Card variant="default" padding="lg">
				<h3>Change Password</h3>
				<div class="form-group">
					<label for="currentPassword">Current Password</label>
					<input
						type="password"
						id="currentPassword"
						bind:value={currentPassword}
						placeholder="Enter current password"
						class="input-field"
					/>
				</div>

				<div class="form-group">
					<label for="newPassword">New Password</label>
					<input
						type="password"
						id="newPassword"
						bind:value={newPassword}
						placeholder="Enter new password"
						class="input-field"
					/>
				</div>

				<div class="form-group">
					<label for="confirmPassword">Confirm New Password</label>
					<input
						type="password"
						id="confirmPassword"
						bind:value={confirmPassword}
						placeholder="Confirm new password"
						class="input-field"
					/>
				</div>

				<div class="form-actions">
					<Button variant="outline" on:click={handleChangePassword} loading={isSaving}>
						Change Password
					</Button>
				</div>
			</Card>
		</section>

		<!-- Credits Section -->
		<section class="settings-section">
			<h2>Credits & Usage</h2>
			<Card variant="default" padding="lg">
				<div class="credits-display">
					<div class="credits-amount">
						<span class="credits-value">{$credits?.balance || 0}</span>
						<span class="credits-label">Credits Remaining</span>
					</div>
					<Button variant="primary" on:click={() => window.location.href = '/add-credits'}>
						Add Credits
					</Button>
				</div>
			</Card>
		</section>

		<!-- Danger Zone -->
		<section class="settings-section danger-zone">
			<h2>Danger Zone</h2>
			<Card variant="default" padding="lg">
				<div class="setting-row">
					<div class="setting-info">
						<h3>Delete Account</h3>
						<p>Permanently delete your account and all associated data</p>
					</div>
					<div class="setting-control">
						<Button variant="danger">Delete Account</Button>
					</div>
				</div>
			</Card>
		</section>
	</div>
</div>

<style>
	.settings-page {
		padding: 2rem;
		max-width: 800px;
		margin: 0 auto;
		overflow-y: auto;
		height: 100%;
	}

	.settings-header {
		margin-bottom: 2rem;
	}

	.settings-header h1 {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--color-text-source);
		margin-bottom: 0.5rem;
	}

	.settings-header p {
		color: var(--color-text-whisper);
	}

	.settings-content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.settings-section h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 1rem;
	}

	.settings-section h3 {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text-source);
		margin-bottom: 1rem;
	}

	.form-group {
		margin-bottom: 1.25rem;
	}

	.form-group label {
		display: block;
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-manifest);
		margin-bottom: 0.5rem;
	}

	.input-field {
		width: 100%;
		padding: 0.75rem 1rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.625rem;
		color: var(--color-text-source);
		font-size: 0.9375rem;
		transition: border-color 0.15s ease;
	}

	.input-field:focus {
		outline: none;
		border-color: var(--color-primary-400);
	}

	.input-field.disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.help-text {
		font-size: 0.75rem;
		color: var(--color-text-hint);
		margin-top: 0.375rem;
	}

	.form-actions {
		margin-top: 1.5rem;
	}

	.setting-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.setting-info h3 {
		margin-bottom: 0.25rem;
	}

	.setting-info p {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
		margin: 0;
	}

	.theme-toggle {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		background: var(--color-field-depth);
		border: 1px solid var(--color-veil-thin);
		border-radius: 0.625rem;
		color: var(--color-text-manifest);
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.theme-toggle:hover {
		background: var(--color-field-elevated);
		border-color: var(--color-veil-present);
	}

	.credits-display {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.credits-amount {
		display: flex;
		flex-direction: column;
	}

	.credits-value {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-primary-500);
	}

	.credits-label {
		font-size: 0.8125rem;
		color: var(--color-text-whisper);
	}

	.danger-zone h2 {
		color: var(--color-error-500);
	}

	/* Mobile responsive */
	@media (max-width: 767px) {
		.settings-page {
			padding: 1rem;
		}

		.setting-row {
			flex-direction: column;
			align-items: flex-start;
		}

		.setting-control {
			margin-top: 1rem;
		}

		.credits-display {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}
	}
</style>
