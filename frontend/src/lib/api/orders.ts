import { apiGet, apiPost } from '$lib/api/client';
import type {
	CreateOrderInput,
	CreateOrderOutput,
	OrderListItemOutput,
	OrderOutput
} from '$lib/types/order';

export async function createOrder(input: CreateOrderInput): Promise<CreateOrderOutput> {
	return apiPost<CreateOrderOutput>('/api/v1/orders', input);
}

export async function listOrders(): Promise<OrderListItemOutput[]> {
	return apiGet<OrderListItemOutput[]>('/api/v1/orders');
}

export async function getOrder(publicId: string): Promise<OrderOutput> {
	return apiGet<OrderOutput>(`/api/v1/orders/${publicId}`);
}
