import { listParts } from '$lib/api/parts';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	return { parts: await listParts() };
};
