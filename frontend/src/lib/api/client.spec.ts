import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiGet, apiPost } from '$lib/api/client';
import { ApiError } from '$lib/errors/apiError';

afterEach(() => {
	vi.unstubAllGlobals();
});

function jsonResponse(body: unknown, status: number): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('api client', () => {
	it('maps an error envelope to ApiError', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockImplementation(() =>
				Promise.resolve(
					jsonResponse(
						{
							error: {
								code: 'order.not_found',
								message: '注文が見つかりません。',
								details: {}
							}
						},
						404
					)
				)
			)
		);

		const error = await apiGet('/api/v1/orders/missing').catch((caught) => caught);
		expect(error).toBeInstanceOf(ApiError);
		expect(error).toMatchObject({
			code: 'order.not_found',
			httpStatus: 404
		});
	});

	it('returns json on success', async () => {
		vi.stubGlobal(
			'fetch',
			vi
				.fn()
				.mockResolvedValue(jsonResponse({ id: 1, email: 'a@example.com', is_staff: false }, 200))
		);
		const result = await apiPost<{ email: string }>('/api/v1/sessions', {
			email: 'a@example.com',
			password: 'password1'
		});
		expect(result.email).toBe('a@example.com');
	});
});
