import type { OrderOutput } from '$lib/types/order';

// 保存後の正。決済成功と /orders/[uuid] の load だけが書く。確認画面はドラフトを見ない。
export const syncedOrderState = $state<{ order: OrderOutput | null }>({
	order: null
});

export function setSyncedOrder(order: OrderOutput | null): void {
	syncedOrderState.order = order;
}
