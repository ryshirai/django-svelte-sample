import { apiGet } from '$lib/api/client';
import type { PartCategory, PartOutput } from '$lib/types/part';

export async function listParts(category?: PartCategory): Promise<PartOutput[]> {
	const query = category === undefined ? '' : `?category=${category}`;
	return apiGet<PartOutput[]>(`/api/v1/parts${query}`);
}

export async function getPart(partId: number): Promise<PartOutput> {
	return apiGet<PartOutput>(`/api/v1/parts/${partId}`);
}
