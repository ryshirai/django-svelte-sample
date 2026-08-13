import { listOrders } from '$lib/api/orders';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	try {
		return { orders: await listOrders() };
	} catch (error) {
		throwLoadFailure(error);
	}
};
