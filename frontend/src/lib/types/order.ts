export type CreateOrderInput = {
	part_ids: number[];
	recipient_name: string;
	postal_code: string;
	prefecture: string;
	city: string;
	address_line: string;
	phone: string;
};

export type CreateOrderOutput = {
	// 作成応答は public_id だけ。続けて GET /orders/{uuid} する。
	public_id: string;
};

export type OrderListItemOutput = {
	public_id: string;
	status: 'paid' | 'preparing' | 'shipped' | 'cancelled';
	// Decimal は JSON では文字列。
	total_price: string;
	created_at: string;
};

export type OrderLineOutput = {
	category: string;
	sku: string;
	name: string;
	unit_price: string;
	quantity: number;
};

export type OrderOutput = OrderListItemOutput & {
	recipient_name: string;
	postal_code: string;
	prefecture: string;
	city: string;
	address_line: string;
	phone: string;
	lines: OrderLineOutput[];
};
