import { apiGet } from '$lib/api/client';

export async function ensureCsrfCookie(): Promise<void> {
	// 更新 API の前に csrftoken cookie を必ず載せる。
	await apiGet<undefined>('/api/v1/csrf');
}
