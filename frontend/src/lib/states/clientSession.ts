import { setCurrentUser } from '$lib/states/currentUserState.svelte';
import { resetDraft } from '$lib/states/orderDraftState.svelte';
import { setSyncedOrder } from '$lib/states/syncedOrderState.svelte';

export function clearClientSession(): void {
	setCurrentUser(null);
	resetDraft();
	setSyncedOrder(null);
}
