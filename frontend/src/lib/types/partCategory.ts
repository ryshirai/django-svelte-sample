import type { PartCategory } from '$lib/types/part';

export const partCategories: PartCategory[] = [
	'cpu',
	'motherboard',
	'memory',
	'storage',
	'psu',
	'case',
	'gpu',
	'cpu_cooler'
];

export const partCategoryLabels: Record<PartCategory, string> = {
	cpu: 'CPU',
	motherboard: 'マザーボード',
	memory: 'メモリ',
	storage: 'ストレージ',
	psu: '電源',
	case: 'ケース',
	gpu: 'グラフィックボード',
	cpu_cooler: 'CPUクーラー'
};

// gpu と cpu_cooler は任意。それ以外は必須。
export const requiredPartCategories: PartCategory[] = [
	'cpu',
	'motherboard',
	'memory',
	'storage',
	'psu',
	'case'
];
