import type { CurrentUserOutput } from '$lib/types/currentUser';

// layout の load が埋める。401 のときは null。
export const currentUserState = $state<{ user: CurrentUserOutput | null }>({
	user: null
});

export function setCurrentUser(user: CurrentUserOutput | null): void {
	currentUserState.user = user;
}
