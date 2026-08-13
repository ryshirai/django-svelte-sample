import { getStaffOrder } from '$lib/api/staffOrders';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	return { order: await getStaffOrder(params.uuid) };
};
