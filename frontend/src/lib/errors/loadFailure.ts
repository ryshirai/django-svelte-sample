import { error } from '@sveltejs/kit';
import { isApiError } from '$lib/errors/apiError';

export function throwLoadFailure(caught: unknown): never {
	if (isApiError(caught)) {
		error(caught.httpStatus, { message: caught.code });
	}
	throw caught;
}
