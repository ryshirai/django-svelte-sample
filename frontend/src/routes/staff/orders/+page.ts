import { listStaffOrders } from '$lib/api/staffOrders';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	try {
		return { orders: await listStaffOrders() };
	} catch (error) {
		throwLoadFailure(error);
	}
};
