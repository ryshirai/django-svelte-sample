<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { createStaffPart } from '$lib/api/staffParts';
	import { isApiError } from '$lib/errors/apiError';
	import { messageForApiError } from '$lib/messages/errorDisplay';
	import { uiMessages } from '$lib/messages/ui';
	import type { CreatePartInput } from '$lib/types/part';
	import PartForm from '../PartForm.svelte';
	import { emptyPartForm } from '../partFormDefaults';

	let errorMessage = $state('');

	async function save(value: CreatePartInput): Promise<void> {
		errorMessage = '';
		try {
			await createStaffPart({ ...value, unit_price: String(value.unit_price) });
			await goto(resolve('/staff/parts'));
		} catch (error) {
			errorMessage = isApiError(error) ? messageForApiError(error) : uiMessages.unknownError;
		}
	}
</script>

<svelte:head>
	<title>{uiMessages.staffPartNewTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="mx-auto max-w-3xl p-6">
	<h1 class="text-2xl font-semibold text-fg">{uiMessages.staffPartNewTitle}</h1>
	<section class="mt-6 rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
		<PartForm
			value={emptyPartForm()}
			submitLabel={uiMessages.savePart}
			onsubmit={save}
			{errorMessage}
		/>
	</section>
</main>
