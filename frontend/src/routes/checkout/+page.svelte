<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { evaluateConfiguration } from '$lib/api/configurations';
	import { createOrder, getOrder } from '$lib/api/orders';
	import PartSummaryList from '$lib/components/PartSummaryList.svelte';
	import { isApiError } from '$lib/errors/apiError';
	import { messageForApiError, messageForCode } from '$lib/messages/errorDisplay';
	import { uiMessages } from '$lib/messages/ui';
	import {
		hasRequiredParts,
		orderDraftState,
		resetDraft,
		toPartIds
	} from '$lib/states/orderDraftState.svelte';
	import { setSyncedOrder } from '$lib/states/syncedOrderState.svelte';
	import type { ConfigurationEvaluationOutput } from '$lib/types/configuration';

	let { data } = $props();
	let evaluationOverride = $state<ConfigurationEvaluationOutput | null>(null);
	const evaluation = $derived(evaluationOverride ?? data.evaluation);
	const loadErrorMessage = $derived(data.loadError === '' ? '' : messageForCode(data.loadError));
	let actionError = $state('');
	const errorMessage = $derived(actionError !== '' ? actionError : loadErrorMessage);
	let submitting = $state(false);
	let createdPublicId = $state<string | null>(null);

	async function loadEvaluation(): Promise<void> {
		actionError = '';
		evaluationOverride = null;
		try {
			evaluationOverride = await evaluateConfiguration({ part_ids: toPartIds() });
		} catch (error) {
			actionError = isApiError(error) ? messageForApiError(error) : uiMessages.unknownError;
		}
	}

	async function pay(event: Event): Promise<void> {
		event.preventDefault();
		actionError = '';
		if (!hasRequiredParts()) {
			return;
		}
		submitting = true;
		try {
			// POST 成功後は GET だけ再試行する。同じドラフトで二重注文しない。
			if (createdPublicId === null) {
				const created = await createOrder({
					part_ids: toPartIds(),
					...orderDraftState.shipping
				});
				createdPublicId = created.public_id;
			}
			const order = await getOrder(createdPublicId);
			setSyncedOrder(order);
			resetDraft();
			await goto(resolve(`/orders/${createdPublicId}`));
		} catch (error) {
			actionError = isApiError(error) ? messageForApiError(error) : uiMessages.unknownError;
		} finally {
			submitting = false;
		}
	}

	// 非活性は UX。最終判定は backend。
	const canPay = $derived(
		hasRequiredParts() && evaluation !== null && evaluation.is_valid && !submitting
	);
</script>

<svelte:head>
	<title>{uiMessages.checkoutTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<div class="flex items-end justify-between gap-4">
		<div>
			<h1 class="text-2xl font-semibold text-fg">{uiMessages.checkoutTitle}</h1>
			<p class="mt-1 text-sm text-fg-muted">{uiMessages.mockPaymentNote}</p>
		</div>
		<a class="text-sm text-accent" href={resolve('/configure')}>{uiMessages.backToConfigure}</a>
	</div>
	{#if errorMessage !== ''}
		<p class="mt-4 text-sm text-danger" role="alert">{errorMessage}</p>
	{/if}
	<div class="mt-6 flex gap-6">
		<div class="flex min-w-0 flex-1 flex-col gap-6">
			<section class="rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
				<h2 class="text-lg font-semibold text-fg">{uiMessages.compatibilityTitle}</h2>
				<button
					type="button"
					class="mt-4 rounded-md border border-border px-4 py-2 text-base text-fg hover:bg-bg"
					onclick={loadEvaluation}
				>
					{uiMessages.checkCompatibility}
				</button>
				{#if evaluation !== null}
					<ul class="mt-3 flex flex-col gap-1">
						{#if evaluation.is_valid}
							<li class="text-sm text-success">{uiMessages.compatible}</li>
						{:else}
							{#each evaluation.issues as issue (issue.code)}
								<li class="text-sm text-danger">{messageForCode(issue.code)}</li>
							{/each}
						{/if}
					</ul>
				{/if}
			</section>
			<form
				id="checkout-form"
				class="flex flex-col gap-4 rounded-lg border border-border bg-bg-elevated p-5 shadow-sm"
				onsubmit={pay}
			>
				<h2 class="text-lg font-semibold text-fg">{uiMessages.shippingTitle}</h2>
				<label class="flex flex-col gap-1 text-sm text-fg">
					{uiMessages.recipientName}
					<input
						class="rounded-md border border-border bg-bg p-3 text-base text-fg"
						bind:value={orderDraftState.shipping.recipient_name}
						required
					/>
				</label>
				<label class="flex flex-col gap-1 text-sm text-fg">
					{uiMessages.postalCode}
					<input
						class="rounded-md border border-border bg-bg p-3 text-base text-fg"
						bind:value={orderDraftState.shipping.postal_code}
						pattern={'[0-9]{7}'}
						required
					/>
				</label>
				<label class="flex flex-col gap-1 text-sm text-fg">
					{uiMessages.prefecture}
					<input
						class="rounded-md border border-border bg-bg p-3 text-base text-fg"
						bind:value={orderDraftState.shipping.prefecture}
						required
					/>
				</label>
				<label class="flex flex-col gap-1 text-sm text-fg">
					{uiMessages.city}
					<input
						class="rounded-md border border-border bg-bg p-3 text-base text-fg"
						bind:value={orderDraftState.shipping.city}
						required
					/>
				</label>
				<label class="flex flex-col gap-1 text-sm text-fg">
					{uiMessages.addressLine}
					<input
						class="rounded-md border border-border bg-bg p-3 text-base text-fg"
						bind:value={orderDraftState.shipping.address_line}
						required
					/>
				</label>
				<label class="flex flex-col gap-1 text-sm text-fg">
					{uiMessages.phone}
					<input
						class="rounded-md border border-border bg-bg p-3 text-base text-fg"
						bind:value={orderDraftState.shipping.phone}
						pattern={'[0-9]{10,11}'}
						required
					/>
				</label>
			</form>
		</div>
		<aside class="w-full max-w-sm shrink-0">
			<section class="sticky top-20 rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
				<h2 class="text-lg font-semibold text-fg">{uiMessages.summaryTitle}</h2>
				<div class="mt-4">
					<PartSummaryList parts={data.parts} />
				</div>
				<button
					class="mt-4 w-full rounded-md bg-bg-brand px-4 py-3 text-base font-medium text-fg-inverse hover:opacity-90 disabled:opacity-40"
					type="submit"
					form="checkout-form"
					disabled={!canPay}
				>
					{uiMessages.pay}
				</button>
				<p class="mt-3 text-sm text-fg-muted">{uiMessages.mockPaymentNote}</p>
			</section>
		</aside>
	</div>
</main>
