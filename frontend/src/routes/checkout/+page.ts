import { evaluateConfiguration } from '$lib/api/configurations';
import { listParts } from '$lib/api/parts';
import { toPartIds } from '$lib/states/orderDraftState.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	const parts = await listParts();
	// レジ表示時点のドラフトを一度評価する。$effect では呼ばない。
	const evaluation = await evaluateConfiguration({ part_ids: toPartIds() });
	return { parts, evaluation };
};
