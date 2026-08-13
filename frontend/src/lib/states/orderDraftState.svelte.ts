import type { PartCategory } from '$lib/types/part';

export type DraftShipping = {
	recipient_name: string;
	postal_code: string;
	prefecture: string;
	city: string;
	address_line: string;
	phone: string;
};

export type PartIdsByCategory = Record<PartCategory, number | null>;

const emptyParts = (): PartIdsByCategory => ({
	cpu: null,
	motherboard: null,
	memory: null,
	storage: null,
	psu: null,
	case: null,
	gpu: null,
	cpu_cooler: null
});

const emptyShipping = (): DraftShipping => ({
	recipient_name: '',
	postal_code: '',
	prefecture: '',
	city: '',
	address_line: '',
	phone: ''
});

// 未保存ドラフトの正。メモリのみ。画面遷移では残り、リロードで消える。
export const orderDraftState = $state<{
	partIdsByCategory: PartIdsByCategory;
	shipping: DraftShipping;
}>({
	partIdsByCategory: emptyParts(),
	shipping: emptyShipping()
});

export function selectPart(category: PartCategory, partId: number): void {
	orderDraftState.partIdsByCategory = {
		...orderDraftState.partIdsByCategory,
		[category]: partId
	};
}

export function clearPart(category: PartCategory): void {
	orderDraftState.partIdsByCategory = {
		...orderDraftState.partIdsByCategory,
		[category]: null
	};
}

export function setShipping(partial: Partial<DraftShipping>): void {
	orderDraftState.shipping = { ...orderDraftState.shipping, ...partial };
}

export function resetDraft(): void {
	orderDraftState.partIdsByCategory = emptyParts();
	orderDraftState.shipping = emptyShipping();
}

export function toPartIds(): number[] {
	// 選択の正は part id。未選択（任意カテゴリ含む）は送らない。
	return Object.values(orderDraftState.partIdsByCategory).filter(
		(partId): partId is number => partId !== null
	);
}

export const requiredCategories: PartCategory[] = [
	'cpu',
	'motherboard',
	'memory',
	'storage',
	'psu',
	'case'
];

export function hasRequiredParts(): boolean {
	return requiredCategories.every(
		(category) => orderDraftState.partIdsByCategory[category] !== null
	);
}
