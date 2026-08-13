<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { messageForCode } from '$lib/messages/errorDisplay';
	import { uiMessages } from '$lib/messages/ui';

	const message = $derived(messageForCode(page.error?.message ?? ''));
</script>

<main class="p-6">
	<h1 class="text-2xl font-semibold text-fg">{uiMessages.unknownError}</h1>
	<p class="mt-4 text-sm text-danger" role="alert">{message}</p>
	{#if page.status === 401}
		<p class="mt-4 text-sm">
			<a class="text-accent" href={resolve('/login')}>{uiMessages.toLogin}</a>
		</p>
	{:else}
		<p class="mt-4 text-sm">
			<a class="text-accent" href={resolve('/configure')}>{uiMessages.backToConfigure}</a>
		</p>
	{/if}
</main>
