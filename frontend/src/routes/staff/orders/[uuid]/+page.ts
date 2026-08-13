import { getStaffOrder } from '$lib/api/staffOrders';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	try {
		return { order: await getStaffOrder(params.uuid) };
	} catch (error) {
		throwLoadFailure(error);
	}
};
