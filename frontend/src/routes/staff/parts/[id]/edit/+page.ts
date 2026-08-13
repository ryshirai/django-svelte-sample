import { getStaffPart } from '$lib/api/staffParts';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	return { part: await getStaffPart(Number(params.id)) };
};
