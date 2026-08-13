import { apiGet, apiPatch, apiPost } from '$lib/api/client';
import type { CreatePartInput, PartOutput, UpdatePartInput } from '$lib/types/part';

export async function listStaffParts(): Promise<PartOutput[]> {
	return apiGet<PartOutput[]>('/api/v1/staff/parts');
}

export async function getStaffPart(partId: number): Promise<PartOutput> {
	return apiGet<PartOutput>(`/api/v1/staff/parts/${partId}`);
}

export async function createStaffPart(input: CreatePartInput): Promise<PartOutput> {
	return apiPost<PartOutput>('/api/v1/staff/parts', input);
}

export async function updateStaffPart(partId: number, input: UpdatePartInput): Promise<PartOutput> {
	return apiPatch<PartOutput>(`/api/v1/staff/parts/${partId}`, input);
}
