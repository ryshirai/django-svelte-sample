import { listParts } from '$lib/api/parts';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	try {
		return { parts: await listParts() };
	} catch (error) {
		throwLoadFailure(error);
	}
};
