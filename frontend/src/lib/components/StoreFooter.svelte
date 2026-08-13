<script lang="ts">
	import { resolve } from '$app/paths';
	import { uiMessages } from '$lib/messages/ui';
	import SiteMark from './SiteMark.svelte';
</script>

<footer class="border-t border-border bg-bg-brand px-6 py-8 text-fg-inverse">
	<div class="flex items-start justify-between gap-6">
		<div class="flex items-center gap-3">
			<SiteMark />
			<div>
				<p class="text-lg font-semibold tracking-wide">{uiMessages.siteName}</p>
				<p class="mt-1 text-sm text-fg-inverse/70">{uiMessages.siteTagline}</p>
			</div>
		</div>
		<div class="flex flex-col items-end gap-2 text-sm text-fg-inverse/80">
			<p>{uiMessages.footerLegal}</p>
			<p>{uiMessages.mockPaymentNote}</p>
			<a class="text-accent" href={resolve('/configure')}>{uiMessages.navConfigure}</a>
		</div>
	</div>
</footer>
