import { redirect } from '@sveltejs/kit';
import { ensureCsrfCookie } from '$lib/api/csrf';
import { getCurrentUser } from '$lib/api/currentUser';
import { isApiError } from '$lib/errors/apiError';
import { currentUserState, setCurrentUser } from '$lib/states/currentUserState.svelte';
import type { LayoutLoad } from './$types';

// cookie / CSRF をブラウザで扱う。SSR しない。
export const ssr = false;

export const load: LayoutLoad = async ({ url }) => {
	// 初期化は CSRF → current-user。$effect では fetch しない。
	await ensureCsrfCookie();
	try {
		setCurrentUser(await getCurrentUser());
	} catch (error) {
		if (isApiError(error) && error.code === 'authentication.required') {
			setCurrentUser(null);
		} else {
			throw error;
		}
	}

	const path = url.pathname;
	const user = currentUserState.user;
	const publicPaths = new Set(['/login', '/register']);
	if (user === null && !publicPaths.has(path)) {
		redirect(302, '/login');
	}
	if (user !== null && (publicPaths.has(path) || path === '/')) {
		redirect(302, '/configure');
	}
	// スタッフ画面は UI で隠す。API は IsAdminUser で 403 のまま。
	if (user !== null && path.startsWith('/staff') && !user.is_staff) {
		redirect(302, '/configure');
	}
	return { user };
};
