<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { onAuthenticationRequired } from '$lib/api/authenticationExpiry';
	import { deleteSession } from '$lib/api/sessions';
	import AppHeader from '$lib/components/AppHeader.svelte';
	import StoreFooter from '$lib/components/StoreFooter.svelte';
	import { currentUserState } from '$lib/states/currentUserState.svelte';
	import { clearClientSession } from '$lib/states/clientSession';
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';

	let { children } = $props();

	onAuthenticationRequired(() => {
		clearClientSession();
		void goto(resolve('/login'));
	});

	async function logout(): Promise<void> {
		try {
			await deleteSession();
		} finally {
			clearClientSession();
			await goto(resolve('/login'));
		}
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if currentUserState.user}
	<AppHeader currentPath={page.url.pathname} onlogout={logout} />
{/if}
{@render children()}
{#if currentUserState.user}
	<StoreFooter />
{/if}
