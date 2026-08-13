import { getOrder } from '$lib/api/orders';
import { isApiError } from '$lib/errors/apiError';
import { setSyncedOrder } from '$lib/states/syncedOrderState.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	try {
		const order = await getOrder(params.uuid);
		setSyncedOrder(order);
		return { order, notFound: false };
	} catch (error) {
		// 他人・不存在は Kit の 404 にせず、画面で案内する。
		if (isApiError(error) && error.code === 'order.not_found') {
			setSyncedOrder(null);
			return { order: null, notFound: true };
		}
		throw error;
	}
};
