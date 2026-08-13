import { apiDelete, apiPost } from '$lib/api/client';
import type { CreateSessionInput, CurrentUserOutput } from '$lib/types/currentUser';

export async function createSession(input: CreateSessionInput): Promise<CurrentUserOutput> {
	return apiPost<CurrentUserOutput>('/api/v1/sessions', input);
}

export async function deleteSession(): Promise<void> {
	await apiDelete('/api/v1/sessions');
}
