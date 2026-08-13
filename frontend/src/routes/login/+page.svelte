<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { createSession } from '$lib/api/sessions';
	import AuthPanel from '$lib/components/AuthPanel.svelte';
	import { isApiError } from '$lib/errors/apiError';
	import { messageForApiError } from '$lib/messages/errorDisplay';
	import { uiMessages } from '$lib/messages/ui';
	import { setCurrentUser } from '$lib/states/currentUserState.svelte';

	let email = $state('');
	let password = $state('');
	let errorMessage = $state('');
	let submitting = $state(false);

	async function submit(event: Event): Promise<void> {
		event.preventDefault();
		errorMessage = '';
		submitting = true;
		try {
			const user = await createSession({ email, password });
			setCurrentUser(user);
			await goto(resolve('/configure'));
		} catch (error) {
			errorMessage = isApiError(error) ? messageForApiError(error) : uiMessages.unknownError;
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>{uiMessages.loginTitle} · {uiMessages.siteName}</title>
</svelte:head>

<AuthPanel title={uiMessages.loginTitle} lead={uiMessages.loginLead}>
	{#if errorMessage !== ''}
		<p id="login-error" class="mt-4 text-sm text-danger" role="alert">{errorMessage}</p>
	{/if}
	<form class="mt-6 flex flex-col gap-4" onsubmit={submit}>
		<label class="flex flex-col gap-1 text-sm text-fg">
			{uiMessages.email}
			<input
				class="rounded-md border border-border bg-bg p-3 text-base text-fg"
				type="email"
				bind:value={email}
				required
				aria-invalid={errorMessage !== ''}
				aria-describedby={errorMessage !== '' ? 'login-error' : undefined}
			/>
		</label>
		<label class="flex flex-col gap-1 text-sm text-fg">
			{uiMessages.password}
			<input
				class="rounded-md border border-border bg-bg p-3 text-base text-fg"
				type="password"
				bind:value={password}
				required
				minlength="8"
				aria-invalid={errorMessage !== ''}
				aria-describedby={errorMessage !== '' ? 'login-error' : undefined}
			/>
		</label>
		<button
			class="rounded-md bg-bg-brand px-4 py-3 text-base font-medium text-fg-inverse hover:opacity-90 disabled:opacity-40"
			type="submit"
			disabled={submitting}
		>
			{uiMessages.submitLogin}
		</button>
	</form>
	<p class="mt-4 text-sm">
		<a class="text-accent" href={resolve('/register')}>{uiMessages.toRegister}</a>
	</p>
</AuthPanel>
