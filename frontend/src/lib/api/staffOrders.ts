import { apiGet, apiPost } from '$lib/api/client';
import type { OrderListItemOutput, OrderOutput } from '$lib/types/order';

export async function listStaffOrders(): Promise<OrderListItemOutput[]> {
	return apiGet<OrderListItemOutput[]>('/api/v1/staff/orders');
}

export async function getStaffOrder(publicId: string): Promise<OrderOutput> {
	return apiGet<OrderOutput>(`/api/v1/staff/orders/${publicId}`);
}

export async function prepareStaffOrder(publicId: string): Promise<void> {
	await apiPost(`/api/v1/staff/orders/${publicId}/prepare`);
}

export async function shipStaffOrder(publicId: string): Promise<void> {
	await apiPost(`/api/v1/staff/orders/${publicId}/ship`);
}

export async function cancelStaffOrder(publicId: string): Promise<void> {
	await apiPost(`/api/v1/staff/orders/${publicId}/cancel`);
}
