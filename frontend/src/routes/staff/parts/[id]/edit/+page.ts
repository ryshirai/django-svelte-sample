import { getStaffPart } from '$lib/api/staffParts';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	try {
		return { part: await getStaffPart(Number(params.id)) };
	} catch (error) {
		throwLoadFailure(error);
	}
};
