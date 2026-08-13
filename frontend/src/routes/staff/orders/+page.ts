import { listStaffOrders } from '$lib/api/staffOrders';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	return { orders: await listStaffOrders() };
};
