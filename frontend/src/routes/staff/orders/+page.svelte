<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import OrderStatusText from '$lib/components/OrderStatusText.svelte';
	import { uiMessages } from '$lib/messages/ui';

	let { data } = $props();

	function openOrder(publicId: string): void {
		void goto(resolve(`/staff/orders/${publicId}`));
	}
</script>

<svelte:head>
	<title>{uiMessages.staffOrdersTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<h1 class="text-2xl font-semibold text-fg">{uiMessages.staffOrdersTitle}</h1>
	<div class="mt-6 overflow-hidden rounded-lg border border-border bg-bg-elevated shadow-sm">
		<table class="w-full text-left text-base">
			<thead>
				<tr class="border-b border-border bg-bg-subtle text-sm font-medium text-fg-muted">
					<th class="px-4 py-3">{uiMessages.orderNumber}</th>
					<th class="px-4 py-3">{uiMessages.status}</th>
					<th class="px-4 py-3">{uiMessages.total}</th>
					<th class="px-4 py-3">{uiMessages.orderedAt}</th>
				</tr>
			</thead>
			<tbody>
				{#each data.orders as order (order.public_id)}
					<tr
						class="cursor-pointer border-b border-border last:border-b-0 hover:bg-bg"
						onclick={() => openOrder(order.public_id)}
					>
						<td class="px-4 py-3">
							<a class="text-sm text-fg" href={resolve(`/staff/orders/${order.public_id}`)}>
								{order.public_id}
							</a>
						</td>
						<td class="px-4 py-3"><OrderStatusText status={order.status} /></td>
						<td class="px-4 py-3 tabular-nums">
							¥{Number(order.total_price).toLocaleString('ja-JP')}
						</td>
						<td class="px-4 py-3 text-sm text-fg-muted">
							{new Date(order.created_at).toLocaleString('ja-JP')}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</main>
