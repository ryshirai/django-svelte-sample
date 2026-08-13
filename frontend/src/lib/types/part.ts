export type PartCategory =
	'cpu' | 'motherboard' | 'memory' | 'storage' | 'psu' | 'case' | 'gpu' | 'cpu_cooler';

export type PartOutput = {
	id: number;
	sku: string;
	name: string;
	category: PartCategory;
	// Decimal は JSON では文字列。
	unit_price: string;
	stock_quantity: number;
	is_listed: boolean;
	socket: string;
	tdp_watts: number | null;
	memory_type: string;
	form_factor: string;
	memory_slot_count: number | null;
	sata_port_count: number | null;
	m2_slot_count: number | null;
	module_count: number | null;
	capacity_gb: number | null;
	length_mm: number | null;
	interface: string;
	wattage: number | null;
	max_gpu_length_mm: number | null;
	max_cooler_height_mm: number | null;
	height_mm: number | null;
};

export type CreatePartInput = Omit<PartOutput, 'id'>;
export type UpdatePartInput = Partial<CreatePartInput>;
