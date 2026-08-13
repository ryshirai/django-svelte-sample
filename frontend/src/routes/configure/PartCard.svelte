<script lang="ts">
	import CatalogPhoto from '$lib/components/CatalogPhoto.svelte';
	import { uiMessages } from '$lib/messages/ui';
	import type { PartOutput } from '$lib/types/part';

	type Props = {
		part: PartOutput;
		selected: boolean;
		onselect: (part: PartOutput) => void;
		onclear: (part: PartOutput) => void;
	};

	let { part, selected, onselect, onclear }: Props = $props();

	function formatPrice(value: string): string {
		return `¥${Number(value).toLocaleString('ja-JP')}`;
	}

	const cardClass = $derived(
		selected
			? 'flex flex-col overflow-hidden rounded-lg border-2 border-accent bg-bg-elevated'
			: 'flex flex-col overflow-hidden rounded-lg border border-border bg-bg-elevated'
	);
</script>

<article class={cardClass}>
	<CatalogPhoto
		category={part.category}
		sku={part.sku}
		alt={part.name}
		class="h-48 w-full object-cover"
	/>
	<div class="flex flex-1 flex-col p-4">
		<p class="font-medium text-fg">{part.name}</p>
		<p class="mt-1 text-sm text-fg-muted">{part.sku}</p>
		<p class="mt-3 text-lg font-semibold text-accent tabular-nums">
			{formatPrice(part.unit_price)}
		</p>
		<div class="mt-4 flex items-center justify-between gap-3">
			{#if part.stock_quantity < 1}
				<span class="text-sm text-danger">{uiMessages.outOfStock}</span>
			{:else}
				<span class="text-sm text-fg-muted">
					{uiMessages.stock}
					{part.stock_quantity}
				</span>
			{/if}
			{#if selected}
				<button
					type="button"
					class="rounded-md border border-border px-3 py-1 text-sm text-fg hover:bg-bg"
					onclick={() => onclear(part)}
				>
					{uiMessages.clear}
				</button>
			{:else}
				<button
					type="button"
					class="rounded-md bg-bg-brand px-3 py-1 text-sm font-medium text-fg-inverse hover:opacity-90 disabled:opacity-40"
					onclick={() => onselect(part)}
					disabled={part.stock_quantity < 1}
				>
					{uiMessages.select}
				</button>
			{/if}
		</div>
	</div>
</article>
