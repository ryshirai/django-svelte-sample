import { evaluateConfiguration } from '$lib/api/configurations';
import { listParts } from '$lib/api/parts';
import { isApiError } from '$lib/errors/apiError';
import { throwLoadFailure } from '$lib/errors/loadFailure';
import { toPartIds } from '$lib/states/orderDraftState.svelte';
import type { ConfigurationEvaluationOutput } from '$lib/types/configuration';
import type { PageLoad } from './$types';

function checkoutLoadError(error: unknown): string {
	if (!isApiError(error)) {
		return '';
	}
	if (
		error.code === 'order.part_unlisted' ||
		error.code === 'part.not_found' ||
		error.code.startsWith('configuration.')
	) {
		return error.code;
	}
	return '';
}

export const load: PageLoad = async () => {
	try {
		const parts = await listParts();
		let evaluation: ConfigurationEvaluationOutput | null = null;
		let loadError = '';
		try {
			// レジ表示時点のドラフトを一度評価する。$effect では呼ばない。
			evaluation = await evaluateConfiguration({ part_ids: toPartIds() });
		} catch (error) {
			loadError = checkoutLoadError(error);
			if (loadError === '') {
				throwLoadFailure(error);
			}
		}
		return { parts, evaluation, loadError };
	} catch (error) {
		throwLoadFailure(error);
	}
};
