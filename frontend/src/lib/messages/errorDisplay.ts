import type { ApiError } from '$lib/errors/apiError';
import { authenticationMessages } from '$lib/messages/authentication';
import { configurationMessages } from '$lib/messages/configuration';
import { orderMessages } from '$lib/messages/order';
import { partMessages } from '$lib/messages/part';
import { uiMessages } from '$lib/messages/ui';

const byCode: Record<string, string> = {
	'authentication.invalid_credentials': authenticationMessages.invalidCredentials,
	'authentication.required': authenticationMessages.required,
	'authentication.staff_required': authenticationMessages.staffRequired,
	'registration.email_already_used': authenticationMessages.emailAlreadyUsed,
	'input.invalid': uiMessages.inputInvalid,
	'part.not_found': partMessages.notFound,
	'part.sku_already_used': partMessages.skuAlreadyUsed,
	'part.invalid_attributes': partMessages.invalidAttributes,
	'order.not_found': orderMessages.notFound,
	'order.part_unlisted': orderMessages.partUnlisted,
	'order.insufficient_stock': orderMessages.insufficientStock,
	'order.invalid_status_transition': orderMessages.invalidStatusTransition,
	...configurationMessages
};

export function messageForApiError(error: ApiError): string {
	// 画面文言の正本。backend の error.message は使わない。
	return byCode[error.code] ?? uiMessages.unknownError;
}

export function messageForCode(code: string): string {
	return byCode[code] ?? uiMessages.unknownError;
}
