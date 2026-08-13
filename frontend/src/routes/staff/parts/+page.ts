import { listStaffParts } from '$lib/api/staffParts';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	return { parts: await listStaffParts() };
};
