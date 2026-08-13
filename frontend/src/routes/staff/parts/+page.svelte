<script lang="ts">
	import { resolve } from '$app/paths';
	import CatalogPhoto from '$lib/components/CatalogPhoto.svelte';
	import { uiMessages } from '$lib/messages/ui';
	import { partCategoryLabels } from '$lib/types/partCategory';

	let { data } = $props();
</script>

<svelte:head>
	<title>{uiMessages.staffPartsTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-semibold text-fg">{uiMessages.staffPartsTitle}</h1>
		<a
			class="rounded-md bg-bg-brand px-4 py-2 text-base font-medium text-fg-inverse hover:opacity-90"
			href={resolve('/staff/parts/new')}
		>
			{uiMessages.createPart}
		</a>
	</div>
	<div class="mt-6 overflow-hidden rounded-lg border border-border bg-bg-elevated shadow-sm">
		<table class="w-full text-left text-base">
			<thead>
				<tr class="border-b border-border bg-bg-subtle text-sm font-medium text-fg-muted">
					<th class="px-4 py-3" scope="col">{uiMessages.sku}</th>
					<th class="px-4 py-3" scope="col">{uiMessages.name}</th>
					<th class="px-4 py-3" scope="col">{uiMessages.category}</th>
					<th class="px-4 py-3" scope="col">{uiMessages.unitPrice}</th>
					<th class="px-4 py-3" scope="col">{uiMessages.stockQuantity}</th>
					<th class="px-4 py-3" scope="col">{uiMessages.isListed}</th>
				</tr>
			</thead>
			<tbody>
				{#each data.parts as part (part.id)}
					<tr class="border-b border-border last:border-b-0 hover:bg-bg">
						<td class="px-4 py-3">
							<span class="flex items-center gap-3">
								<CatalogPhoto
									category={part.category}
									sku={part.sku}
									alt=""
									class="h-10 w-10 shrink-0 rounded-md object-cover"
								/>
								<a class="font-medium text-fg" href={resolve(`/staff/parts/${part.id}/edit`)}>
									{part.sku}
								</a>
							</span>
						</td>
						<td class="px-4 py-3">{part.name}</td>
						<td class="px-4 py-3">{partCategoryLabels[part.category]}</td>
						<td class="px-4 py-3 tabular-nums">
							¥{Number(part.unit_price).toLocaleString('ja-JP')}
						</td>
						<td class="px-4 py-3">{part.stock_quantity}</td>
						<td class="px-4 py-3">
							{#if part.is_listed}
								<span class="inline-block rounded-full bg-bg-subtle px-3 py-1 text-sm text-success">
									{uiMessages.listed}
								</span>
							{:else}
								<span
									class="inline-block rounded-full bg-bg-subtle px-3 py-1 text-sm text-fg-muted"
								>
									{uiMessages.unlisted}
								</span>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</main>
