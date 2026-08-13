<script lang="ts">
	import { resolve } from '$app/paths';
	import SiteMark from '$lib/components/SiteMark.svelte';
	import { uiMessages } from '$lib/messages/ui';
	import { currentUserState } from '$lib/states/currentUserState.svelte';
	import { toPartIds } from '$lib/states/orderDraftState.svelte';

	type Props = {
		currentPath: string;
		onlogout: () => Promise<void>;
	};

	let { currentPath, onlogout }: Props = $props();

	const selectedCount = $derived(toPartIds().length);

	function isCurrent(href: string): boolean {
		return currentPath === href || currentPath.startsWith(`${href}/`);
	}

	function navClass(href: string): string {
		const base = 'rounded-md px-3 py-1 text-base';
		if (isCurrent(href)) {
			return `${base} bg-fg-inverse/10 text-fg-inverse`;
		}
		return `${base} text-fg-inverse/80 hover:bg-fg-inverse/10 hover:text-fg-inverse`;
	}
</script>

<header class="sticky top-0 z-10 bg-bg-brand shadow-sm">
	<div class="flex items-center gap-6 px-6 py-3">
		<a href={resolve('/configure')} class="flex items-center gap-2 text-fg-inverse">
			<SiteMark />
			<span>
				<span class="block text-lg font-semibold tracking-wide">{uiMessages.siteName}</span>
				<span class="block text-sm text-fg-inverse/60">{uiMessages.footerLegal}</span>
			</span>
		</a>
		<nav class="flex flex-1 items-center gap-1">
			<a
				href={resolve('/configure')}
				class={navClass('/configure')}
				aria-current={isCurrent('/configure') ? 'page' : undefined}
			>
				{uiMessages.navConfigure}
			</a>
			<a
				href={resolve('/orders')}
				class={navClass('/orders')}
				aria-current={isCurrent('/orders') ? 'page' : undefined}
			>
				{uiMessages.navOrders}
			</a>
			<a
				href={resolve('/checkout')}
				class="flex items-center gap-2 {navClass('/checkout')}"
				aria-current={isCurrent('/checkout') ? 'page' : undefined}
			>
				{uiMessages.navCheckout}
				{#if selectedCount > 0}
					<span class="rounded-full bg-accent px-2 py-0 text-sm text-fg-inverse"
						>{selectedCount}</span
					>
				{/if}
			</a>
			{#if currentUserState.user?.is_staff}
				<a
					href={resolve('/staff/parts')}
					class={navClass('/staff/parts')}
					aria-current={isCurrent('/staff/parts') ? 'page' : undefined}
				>
					{uiMessages.navStaffParts}
				</a>
				<a
					href={resolve('/staff/orders')}
					class={navClass('/staff/orders')}
					aria-current={isCurrent('/staff/orders') ? 'page' : undefined}
				>
					{uiMessages.navStaffOrders}
				</a>
			{/if}
		</nav>
		{#if currentUserState.user}
			<p class="text-sm text-fg-inverse/70">{currentUserState.user.email}</p>
			<button
				type="button"
				class="rounded-md border border-fg-inverse/30 px-3 py-1 text-sm text-fg-inverse hover:bg-fg-inverse/10"
				onclick={() => void onlogout()}
			>
				{uiMessages.logout}
			</button>
		{/if}
	</div>
</header>
