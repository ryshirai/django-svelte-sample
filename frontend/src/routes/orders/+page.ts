import { listOrders } from '$lib/api/orders';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	return { orders: await listOrders() };
};
