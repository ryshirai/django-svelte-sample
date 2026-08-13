import { apiGet } from '$lib/api/client';
import type { CurrentUserOutput } from '$lib/types/currentUser';

export async function getCurrentUser(): Promise<CurrentUserOutput> {
	return apiGet<CurrentUserOutput>('/api/v1/current-user');
}
