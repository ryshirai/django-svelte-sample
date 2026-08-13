<script lang="ts">
	import { resolve } from '$app/paths';
	import OrderStatusText from '$lib/components/OrderStatusText.svelte';
	import { uiMessages } from '$lib/messages/ui';

	let { data } = $props();

	function formatPrice(value: string): string {
		return `¥${Number(value).toLocaleString('ja-JP')}`;
	}

	function formatDate(value: string): string {
		return new Date(value).toLocaleString('ja-JP');
	}
</script>

<svelte:head>
	<title>{uiMessages.ordersTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<h1 class="text-2xl font-semibold text-fg">{uiMessages.ordersTitle}</h1>
	{#if data.orders.length === 0}
		<section class="mt-6 rounded-lg border border-border bg-bg-elevated p-8 shadow-sm">
			<p class="text-base text-fg">{uiMessages.emptyOrders}</p>
			<p class="mt-2 text-sm text-fg-muted">{uiMessages.emptyOrdersLead}</p>
			<p class="mt-4">
				<a class="text-accent" href={resolve('/configure')}>{uiMessages.backToConfigure}</a>
			</p>
		</section>
	{:else}
		<ul class="mt-6 flex flex-col gap-4">
			{#each data.orders as order (order.public_id)}
				<li>
					<a
						class="flex items-center justify-between gap-6 rounded-lg border border-border bg-bg-elevated p-5 shadow-sm hover:bg-bg"
						href={resolve(`/orders/${order.public_id}`)}
					>
						<div class="min-w-0">
							<p class="text-sm text-fg-muted">{uiMessages.orderNumber}</p>
							<p class="mt-1 truncate text-sm text-fg">{order.public_id}</p>
							<p class="mt-2 text-sm text-fg-muted">{formatDate(order.created_at)}</p>
						</div>
						<OrderStatusText status={order.status} />
						<p class="text-lg font-semibold text-accent tabular-nums">
							{formatPrice(order.total_price)}
						</p>
						<span class="text-sm text-accent">{uiMessages.viewOrder}</span>
					</a>
				</li>
			{/each}
		</ul>
	{/if}
</main>
