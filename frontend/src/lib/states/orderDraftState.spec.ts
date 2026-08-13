import { beforeEach, describe, expect, it } from 'vitest';
import {
	hasRequiredParts,
	resetDraft,
	selectPart,
	toPartIds
} from '$lib/states/orderDraftState.svelte';

describe('orderDraftState', () => {
	beforeEach(() => {
		resetDraft();
	});

	it('keeps selected part ids after subsequent imports', async () => {
		selectPart('cpu', 10);
		const imported = await import('$lib/states/orderDraftState.svelte');
		expect(imported.orderDraftState.partIdsByCategory.cpu).toBe(10);
		expect(imported.toPartIds()).toEqual([10]);
	});

	it('clears the draft', () => {
		selectPart('cpu', 10);
		resetDraft();
		expect(toPartIds()).toEqual([]);
		expect(hasRequiredParts()).toBe(false);
	});
});
