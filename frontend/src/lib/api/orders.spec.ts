import { afterEach, describe, expect, it, vi } from 'vitest';
import { createOrder, getOrder } from '$lib/api/orders';

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('orders api', () => {
	it('creates an order then fetches the saved order', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValueOnce(
				new Response(JSON.stringify({ public_id: 'abc-123' }), {
					status: 201,
					headers: { 'Content-Type': 'application/json' }
				})
			)
			.mockResolvedValueOnce(
				new Response(
					JSON.stringify({
						public_id: 'abc-123',
						status: 'paid',
						total_price: '1000',
						created_at: '2026-08-13T00:00:00+09:00',
						recipient_name: '山田太郎',
						postal_code: '1600022',
						prefecture: '東京都',
						city: '新宿区',
						address_line: '新宿1-1-1',
						phone: '09012345678',
						lines: []
					}),
					{ status: 200, headers: { 'Content-Type': 'application/json' } }
				)
			);
		vi.stubGlobal('fetch', fetchMock);

		const created = await createOrder({
			part_ids: [1],
			recipient_name: '山田太郎',
			postal_code: '1600022',
			prefecture: '東京都',
			city: '新宿区',
			address_line: '新宿1-1-1',
			phone: '09012345678'
		});
		const order = await getOrder(created.public_id);
		expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/orders');
		expect(fetchMock.mock.calls[1]?.[0]).toBe('/api/v1/orders/abc-123');
		expect(order.public_id).toBe('abc-123');
		expect(order.status).toBe('paid');
	});
});
