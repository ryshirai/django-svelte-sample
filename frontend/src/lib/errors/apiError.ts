export type ApiErrorCode =
	| 'authentication.invalid_credentials'
	| 'authentication.required'
	| 'authentication.staff_required'
	| 'registration.email_already_used'
	| 'input.invalid'
	| 'part.not_found'
	| 'part.sku_already_used'
	| 'part.invalid_attributes'
	| 'configuration.incomplete'
	| 'configuration.duplicate_category'
	| 'configuration.unknown_category'
	| 'configuration.socket_mismatch'
	| 'configuration.memory_type_mismatch'
	| 'configuration.memory_slot_exceeded'
	| 'configuration.form_factor_mismatch'
	| 'configuration.storage_interface_unsupported'
	| 'configuration.gpu_too_long'
	| 'configuration.cooler_socket_mismatch'
	| 'configuration.cooler_too_tall'
	| 'configuration.psu_wattage_insufficient'
	| 'order.not_found'
	| 'order.part_unlisted'
	| 'order.insufficient_stock'
	| 'order.invalid_status_transition';

const API_ERROR_CODES = new Set<string>([
	'authentication.invalid_credentials',
	'authentication.required',
	'authentication.staff_required',
	'registration.email_already_used',
	'input.invalid',
	'part.not_found',
	'part.sku_already_used',
	'part.invalid_attributes',
	'configuration.incomplete',
	'configuration.duplicate_category',
	'configuration.unknown_category',
	'configuration.socket_mismatch',
	'configuration.memory_type_mismatch',
	'configuration.memory_slot_exceeded',
	'configuration.form_factor_mismatch',
	'configuration.storage_interface_unsupported',
	'configuration.gpu_too_long',
	'configuration.cooler_socket_mismatch',
	'configuration.cooler_too_tall',
	'configuration.psu_wattage_insufficient',
	'order.not_found',
	'order.part_unlisted',
	'order.insufficient_stock',
	'order.invalid_status_transition'
]);

export class ApiError extends Error {
	readonly code: ApiErrorCode | 'unknown';
	readonly details: Record<string, unknown>;
	readonly httpStatus: number;

	constructor(code: string, details: Record<string, unknown>, httpStatus: number) {
		super(code);
		this.code = isApiErrorCode(code) ? code : 'unknown';
		this.details = details;
		this.httpStatus = httpStatus;
	}
}

export function isApiError(error: unknown): error is ApiError {
	return error instanceof ApiError;
}

export function isApiErrorCode(code: string): code is ApiErrorCode {
	return API_ERROR_CODES.has(code);
}
