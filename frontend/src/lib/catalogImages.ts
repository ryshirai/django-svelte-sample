import heroAuth from '$lib/assets/catalog/hero-auth.jpg';
import categoryCase from '$lib/assets/catalog/category-case.jpg';
import categoryCpu from '$lib/assets/catalog/category-cpu.jpg';
import categoryCpuCooler from '$lib/assets/catalog/category-cpu-cooler.jpg';
import categoryGpu from '$lib/assets/catalog/category-gpu.jpg';
import categoryMemory from '$lib/assets/catalog/category-memory.jpg';
import categoryMotherboard from '$lib/assets/catalog/category-motherboard.jpg';
import categoryPsu from '$lib/assets/catalog/category-psu.jpg';
import categoryStorage from '$lib/assets/catalog/category-storage.jpg';
import skuCaseItx from '$lib/assets/catalog/sku-CASE-ITX.jpg';
import skuClrTall from '$lib/assets/catalog/sku-CLR-TALL.jpg';
import skuCpu1700 from '$lib/assets/catalog/sku-CPU-1700-13400.jpg';
import skuGpuLong from '$lib/assets/catalog/sku-GPU-LONG.jpg';
import skuMemDdr4 from '$lib/assets/catalog/sku-MEM-DDR4-16.jpg';
import skuPsu300 from '$lib/assets/catalog/sku-PSU-300.jpg';
import type { PartCategory } from '$lib/types/part';

export const catalogHeroAuth = heroAuth;

const byCategory: Record<PartCategory, string> = {
	cpu: categoryCpu,
	motherboard: categoryMotherboard,
	memory: categoryMemory,
	storage: categoryStorage,
	psu: categoryPsu,
	case: categoryCase,
	gpu: categoryGpu,
	cpu_cooler: categoryCpuCooler
};

const bySku: Record<string, string> = {
	'CPU-AM5-7600': categoryCpu,
	'CPU-1700-13400': skuCpu1700,
	'MB-AM5-ATX': categoryMotherboard,
	'MEM-DDR5-32': categoryMemory,
	'MEM-DDR4-16': skuMemDdr4,
	'SSD-M2-1T': categoryStorage,
	'PSU-650': categoryPsu,
	'PSU-300': skuPsu300,
	'CASE-ATX': categoryCase,
	'CASE-ITX': skuCaseItx,
	'GPU-4070': categoryGpu,
	'GPU-LONG': skuGpuLong,
	'CLR-AM5-155': categoryCpuCooler,
	'CLR-TALL': skuClrTall
};

export function catalogPhotoFor(input: { category: string; sku?: string }): string {
	if (input.sku !== undefined) {
		const skuPhoto = bySku[input.sku];
		if (skuPhoto !== undefined) {
			return skuPhoto;
		}
	}
	const categoryPhoto = byCategory[input.category as PartCategory];
	if (categoryPhoto !== undefined) {
		return categoryPhoto;
	}
	return categoryCpu;
}
