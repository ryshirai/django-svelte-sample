<script lang="ts">
	import { catalogHeroAuth } from '$lib/catalogImages';
	import { uiMessages } from '$lib/messages/ui';
	import SiteMark from './SiteMark.svelte';
	import type { Snippet } from 'svelte';

	type Props = {
		title: string;
		lead: string;
		children: Snippet;
	};

	let { title, lead, children }: Props = $props();
</script>

<div class="fixed inset-0 z-0 flex">
	<section class="relative min-w-0 flex-1">
		<img src={catalogHeroAuth} alt="" class="absolute inset-0 h-full w-full object-cover" />
		<div class="absolute inset-0 bg-bg-brand/60"></div>
		<div class="relative flex h-full flex-col justify-end p-10">
			<div class="flex items-center gap-3">
				<SiteMark class="h-8 w-8 text-accent" />
				<p class="text-lg font-semibold tracking-wide text-fg-inverse">{uiMessages.siteName}</p>
			</div>
			<p class="mt-6 text-3xl font-semibold text-fg-inverse">{uiMessages.authHeroTitle}</p>
			<p class="mt-3 max-w-md text-base text-fg-inverse/80">{uiMessages.authHeroBody}</p>
		</div>
	</section>
	<section
		class="flex w-full max-w-lg shrink-0 flex-col justify-center overflow-auto bg-bg px-10 py-8"
	>
		<h1 class="text-2xl font-semibold text-fg">{title}</h1>
		<p class="mt-2 text-sm text-fg-muted">{lead}</p>
		{@render children()}
	</section>
</div>
