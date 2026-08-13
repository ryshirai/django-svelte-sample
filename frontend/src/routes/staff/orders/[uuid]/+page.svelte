<script lang="ts">
	import {
		cancelStaffOrder,
		getStaffOrder,
		prepareStaffOrder,
		shipStaffOrder
	} from '$lib/api/staffOrders';
	import CatalogPhoto from '$lib/components/CatalogPhoto.svelte';
	import OrderStatusText from '$lib/components/OrderStatusText.svelte';
	import { isApiError } from '$lib/errors/apiError';
	import { messageForApiError } from '$lib/messages/errorDisplay';
	import { uiMessages } from '$lib/messages/ui';
	import type { OrderOutput } from '$lib/types/order';
	import type { PartCategory } from '$lib/types/part';
	import { partCategoryLabels } from '$lib/types/partCategory';

	let { data } = $props();
	let orderOverride = $state<OrderOutput | null>(null);
	const order = $derived(orderOverride ?? data.order);
	let errorMessage = $state('');

	async function refresh(): Promise<void> {
		// 操作後は GET し直して画面の正にする。
		orderOverride = await getStaffOrder(order.public_id);
	}

	async function run(action: (id: string) => Promise<void>): Promise<void> {
		errorMessage = '';
		try {
			await action(order.public_id);
			await refresh();
		} catch (error) {
			errorMessage = isApiError(error) ? messageForApiError(error) : uiMessages.unknownError;
		}
	}

	function categoryLabel(category: string): string {
		return partCategoryLabels[category as PartCategory] ?? category;
	}
</script>

<svelte:head>
	<title>{uiMessages.orderDetailTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<h1 class="text-2xl font-semibold text-fg">{uiMessages.orderDetailTitle}</h1>
	{#if errorMessage !== ''}
		<p class="mt-4 text-sm text-danger">{errorMessage}</p>
	{/if}
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
							¥{Number(line.unit_price).toLocaleString('ja-JP')}
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
						¥{Number(order.total_price).toLocaleString('ja-JP')}
					</span>
				</p>
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
			<!-- 押せる遷移だけ活性。拒否は backend が再判定する。 -->
			<div class="flex flex-col gap-2">
				<button
					type="button"
					class="rounded-md bg-bg-brand px-4 py-2 text-base font-medium text-fg-inverse hover:opacity-90 disabled:opacity-40"
					disabled={order.status !== 'paid'}
					onclick={() => run(prepareStaffOrder)}
				>
					{uiMessages.prepare}
				</button>
				<button
					type="button"
					class="rounded-md bg-bg-brand px-4 py-2 text-base font-medium text-fg-inverse hover:opacity-90 disabled:opacity-40"
					disabled={order.status !== 'preparing'}
					onclick={() => run(shipStaffOrder)}
				>
					{uiMessages.ship}
				</button>
				<button
					type="button"
					class="rounded-md border border-danger px-4 py-2 text-base text-danger hover:bg-bg-elevated disabled:opacity-40"
					disabled={order.status === 'shipped' || order.status === 'cancelled'}
					onclick={() => run(cancelStaffOrder)}
				>
					{uiMessages.cancel}
				</button>
			</div>
		</aside>
	</div>
</main>
