<script lang="ts">
	import { resolve } from '$app/paths';
	import CatalogPhoto from '$lib/components/CatalogPhoto.svelte';
	import OrderStatusText from '$lib/components/OrderStatusText.svelte';
	import { orderMessages } from '$lib/messages/order';
	import { uiMessages } from '$lib/messages/ui';
	import { syncedOrderState } from '$lib/states/syncedOrderState.svelte';
	import { partCategoryLabels } from '$lib/types/partCategory';
	import type { PartCategory } from '$lib/types/part';

	let { data } = $props();
	// 確認画面は syncedOrderState を正とする。ドラフトは見ない。
	const order = $derived(syncedOrderState.order ?? data.order);

	function formatPrice(value: string): string {
		return `¥${Number(value).toLocaleString('ja-JP')}`;
	}

	function categoryLabel(category: string): string {
		return partCategoryLabels[category as PartCategory] ?? category;
	}
</script>

<svelte:head>
	<title>{uiMessages.orderDetailTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<div class="flex items-end justify-between gap-4">
		<h1 class="text-2xl font-semibold text-fg">{uiMessages.orderDetailTitle}</h1>
		<a class="text-sm text-accent" href={resolve('/orders')}>{uiMessages.backToOrders}</a>
	</div>
	{#if data.notFound || order === null}
		<p class="mt-6 text-base text-danger">{orderMessages.notFound}</p>
	{:else}
		<div class="mt-6 flex gap-6">
			<section class="min-w-0 flex-1 rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
				<ul class="flex flex-col">
					{#each order.lines as line (line.sku)}
						<li class="flex items-center gap-4 border-b border-border py-4 last:border-b-0">
							<CatalogPhoto
								category={line.category}
								sku={line.sku}
								alt={line.name}
								class="h-20 w-20 shrink-0 rounded-md object-cover"
							/>
							<div class="min-w-0 flex-1">
								<p class="text-sm text-fg-muted">{categoryLabel(line.category)}</p>
								<p class="mt-1 text-base text-fg">{line.name}</p>
								<p class="mt-1 text-sm text-fg-muted">{line.sku}</p>
							</div>
							<p class="text-base font-medium text-fg tabular-nums">
								{formatPrice(line.unit_price)}
							</p>
						</li>
					{/each}
				</ul>
			</section>
			<aside class="flex w-full max-w-sm shrink-0 flex-col gap-6">
				<section class="rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
					<div class="flex items-start justify-between gap-4">
						<div class="min-w-0">
							<p class="text-sm text-fg-muted">{uiMessages.orderNumber}</p>
							<p class="mt-1 text-sm break-all text-fg">{order.public_id}</p>
						</div>
						<OrderStatusText status={order.status} />
					</div>
					<p class="mt-6 flex items-baseline justify-between border-t border-border pt-4">
						<span class="text-sm text-fg-muted">{uiMessages.total}</span>
						<span class="text-lg font-semibold text-accent tabular-nums">
							{formatPrice(order.total_price)}
						</span>
					</p>
					<p class="mt-2 text-sm text-fg-muted">{uiMessages.taxIncludedNote}</p>
					<p class="text-sm text-fg-muted">{uiMessages.shippingZeroNote}</p>
				</section>
				<section class="rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
					<h2 class="text-lg font-semibold text-fg">{uiMessages.shippingTitle}</h2>
					<div class="mt-3 flex flex-col gap-1 text-base text-fg">
						<p>{order.recipient_name}</p>
						<p>{order.postal_code}</p>
						<p>{order.prefecture}{order.city}{order.address_line}</p>
						<p>{order.phone}</p>
					</div>
				</section>
			</aside>
		</div>
	{/if}
</main>
