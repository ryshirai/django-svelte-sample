<script lang="ts">
	import CatalogPhoto from '$lib/components/CatalogPhoto.svelte';
	import { uiMessages } from '$lib/messages/ui';
	import { orderDraftState } from '$lib/states/orderDraftState.svelte';
	import type { PartOutput } from '$lib/types/part';
	import { partCategories, partCategoryLabels } from '$lib/types/partCategory';

	type Props = {
		parts: PartOutput[];
	};

	let { parts }: Props = $props();

	function selectedPart(category: (typeof partCategories)[number]): PartOutput | null {
		const id = orderDraftState.partIdsByCategory[category];
		if (id === null) {
			return null;
		}
		return parts.find((part) => part.id === id) ?? null;
	}

	function formatPrice(value: string): string {
		return `¥${Number(value).toLocaleString('ja-JP')}`;
	}

	// UX 合計。決済金額の正ではない。
	const total = $derived.by(() => {
		let sum = 0;
		for (const category of partCategories) {
			const part = selectedPart(category);
			if (part !== null) {
				sum += Number(part.unit_price);
			}
		}
		return sum;
	});
</script>

<ul class="flex flex-col">
	{#each partCategories as category (category)}
		{@const part = selectedPart(category)}
		<li class="flex gap-3 border-b border-border py-2 last:border-b-0">
			<CatalogPhoto
				{category}
				sku={part?.sku}
				alt=""
				class="h-10 w-10 shrink-0 rounded-md object-cover"
			/>
			<div class="min-w-0 flex-1">
				<div class="flex justify-between gap-3 text-sm">
					<span class="text-fg-muted">{partCategoryLabels[category]}</span>
					<span class="text-fg tabular-nums"
						>{part === null ? '—' : formatPrice(part.unit_price)}</span
					>
				</div>
				<p class="mt-1 text-sm text-fg">
					{part === null ? uiMessages.unselected : part.name}
				</p>
			</div>
		</li>
	{/each}
</ul>
<p class="mt-4 flex items-baseline justify-between border-t border-border pt-4">
	<span class="text-sm text-fg-muted">{uiMessages.total}</span>
	<span class="text-lg font-semibold text-accent tabular-nums"
		>¥{total.toLocaleString('ja-JP')}</span
	>
</p>
<p class="mt-2 text-sm text-fg-muted">{uiMessages.taxIncludedNote}</p>
<p class="text-sm text-fg-muted">{uiMessages.shippingZeroNote}</p>
