import { listStaffParts } from '$lib/api/staffParts';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	try {
		return { parts: await listStaffParts() };
	} catch (error) {
		throwLoadFailure(error);
	}
};
