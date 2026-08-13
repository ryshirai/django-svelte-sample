<script lang="ts">
	import { page } from '$app/state';
	import AppHeader from '$lib/components/AppHeader.svelte';
	import StoreFooter from '$lib/components/StoreFooter.svelte';
	import { currentUserState } from '$lib/states/currentUserState.svelte';
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if currentUserState.user}
	<AppHeader currentPath={page.url.pathname} />
{/if}
{@render children()}
{#if currentUserState.user}
	<StoreFooter />
{/if}
