import { ApiError } from '$lib/errors/apiError';

type Envelope = {
	error?: {
		code?: string;
		message?: string;
		details?: Record<string, unknown>;
	};
};

export async function apiGet<T>(path: string): Promise<T> {
	return apiRequest<T>(path, { method: 'GET' });
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
	return apiRequest<T>(path, { method: 'POST', body });
}

export async function apiPatch<T>(path: string, body?: unknown): Promise<T> {
	return apiRequest<T>(path, { method: 'PATCH', body });
}

export async function apiDelete(path: string): Promise<void> {
	await apiRequest<undefined>(path, { method: 'DELETE', empty: true });
}

async function apiRequest<T>(
	path: string,
	options: { method: string; body?: unknown; empty?: boolean }
): Promise<T> {
	const headers = new Headers();
	if (options.body !== undefined) {
		headers.set('Content-Type', 'application/json');
	}
	const csrf = readCsrfToken();
	if (csrf !== '') {
		// session cookie と対で送る。csrftoken は HttpOnly ではない。
		headers.set('X-CSRFToken', csrf);
	}
	const response = await fetch(path, {
		method: options.method,
		credentials: 'include',
		headers,
		body: options.body === undefined ? undefined : JSON.stringify(options.body)
	});
	// 204 は JSON 本文がない。
	if (response.status === 204 || options.empty) {
		if (!response.ok) {
			throw await toApiError(response);
		}
		return undefined as T;
	}
	const payload = (await response.json()) as Envelope & T;
	if (!response.ok) {
		throw toApiErrorFromPayload(payload, response.status);
	}
	return payload;
}

async function toApiError(response: Response): Promise<ApiError> {
	try {
		const payload = (await response.json()) as Envelope;
		return toApiErrorFromPayload(payload, response.status);
	} catch {
		return new ApiError('unknown', {}, response.status);
	}
}

function toApiErrorFromPayload(payload: Envelope, httpStatus: number): ApiError {
	const error = payload.error;
	// 未定義 code は unknown。frontend 側で code を発明しない。
	return new ApiError(error?.code ?? 'unknown', error?.details ?? {}, httpStatus);
}

function readCsrfToken(): string {
	if (typeof document === 'undefined') {
		return '';
	}
	const match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
	if (match === null) {
		return '';
	}
	return decodeURIComponent(match[1]);
}
