import { apiPost } from '$lib/api/client';
import type { CreateRegistrationInput, CurrentUserOutput } from '$lib/types/currentUser';

export async function createRegistration(
	input: CreateRegistrationInput
): Promise<CurrentUserOutput> {
	return apiPost<CurrentUserOutput>('/api/v1/registrations', input);
}
