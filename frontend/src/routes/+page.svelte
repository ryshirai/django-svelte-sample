<script lang="ts">
	import { uiMessages } from '$lib/messages/ui';
</script>

<svelte:head>
	<title>{uiMessages.siteName}</title>
</svelte:head>

<main class="mx-auto max-w-3xl p-6">
	<p class="text-base text-fg-muted">{uiMessages.siteName}</p>
</main>
