import type { CreatePartInput, PartCategory, PartOutput } from '$lib/types/part';

export function emptyPartForm(category: PartCategory = 'cpu'): CreatePartInput {
	return {
		sku: '',
		name: '',
		category,
		unit_price: '1',
		stock_quantity: 0,
		is_listed: true,
		socket: '',
		tdp_watts: null,
		memory_type: '',
		form_factor: '',
		memory_slot_count: null,
		sata_port_count: null,
		m2_slot_count: null,
		module_count: null,
		capacity_gb: null,
		length_mm: null,
		interface: '',
		wattage: null,
		max_gpu_length_mm: null,
		max_cooler_height_mm: null,
		height_mm: null
	};
}

export function partToForm(part: PartOutput): CreatePartInput {
	return {
		sku: part.sku,
		name: part.name,
		category: part.category,
		unit_price: part.unit_price,
		stock_quantity: part.stock_quantity,
		is_listed: part.is_listed,
		socket: part.socket,
		tdp_watts: part.tdp_watts,
		memory_type: part.memory_type,
		form_factor: part.form_factor,
		memory_slot_count: part.memory_slot_count,
		sata_port_count: part.sata_port_count,
		m2_slot_count: part.m2_slot_count,
		module_count: part.module_count,
		capacity_gb: part.capacity_gb,
		length_mm: part.length_mm,
		interface: part.interface,
		wattage: part.wattage,
		max_gpu_length_mm: part.max_gpu_length_mm,
		max_cooler_height_mm: part.max_cooler_height_mm,
		height_mm: part.height_mm
	};
}

export function fieldsForCategory(category: PartCategory): string[] {
	// カテゴリごとの属性表示。幅バリアントではない。
	const map: Record<PartCategory, string[]> = {
		cpu: ['socket', 'tdp_watts'],
		motherboard: [
			'socket',
			'memory_type',
			'form_factor',
			'memory_slot_count',
			'sata_port_count',
			'm2_slot_count'
		],
		memory: ['memory_type', 'module_count', 'capacity_gb'],
		storage: ['interface'],
		psu: ['wattage'],
		case: ['form_factor', 'max_gpu_length_mm', 'max_cooler_height_mm'],
		gpu: ['length_mm', 'tdp_watts'],
		cpu_cooler: ['socket', 'height_mm']
	};
	return map[category];
}
