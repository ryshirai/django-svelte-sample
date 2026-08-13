<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { evaluateConfiguration } from '$lib/api/configurations';
	import { catalogHeroAuth } from '$lib/catalogImages';
	import PartSummaryList from '$lib/components/PartSummaryList.svelte';
	import { isApiError } from '$lib/errors/apiError';
	import { messageForApiError, messageForCode } from '$lib/messages/errorDisplay';
	import { uiMessages } from '$lib/messages/ui';
	import {
		clearPart,
		hasRequiredParts,
		orderDraftState,
		selectPart,
		toPartIds
	} from '$lib/states/orderDraftState.svelte';
	import type { ConfigurationEvaluationOutput } from '$lib/types/configuration';
	import type { PartCategory, PartOutput } from '$lib/types/part';
	import { partCategories, requiredPartCategories } from '$lib/types/partCategory';
	import CategoryRail from './CategoryRail.svelte';
	import PartCard from './PartCard.svelte';

	let { data } = $props();
	let selectedCategory = $state<PartCategory>('cpu');
	let evaluation = $state<ConfigurationEvaluationOutput | null>(null);
	let errorMessage = $state('');

	const visibleParts = $derived(
		data.parts.filter((part: PartOutput) => part.category === selectedCategory)
	);

	const chosenNames = $derived.by(() => {
		const names = {} as Record<PartCategory, string | null>;
		for (const category of partCategories) {
			const id = orderDraftState.partIdsByCategory[category];
			names[category] =
				id === null ? null : (data.parts.find((part: PartOutput) => part.id === id)?.name ?? null);
		}
		return names;
	});

	const requiredSelected = $derived(
		requiredPartCategories.filter(
			(category) => orderDraftState.partIdsByCategory[category] !== null
		).length
	);

	// クリックとレジ直前だけ。$effect では呼ばない。
	async function checkCompatibility(): Promise<boolean> {
		errorMessage = '';
		evaluation = null;
		try {
			const next = await evaluateConfiguration({ part_ids: toPartIds() });
			evaluation = next;
			return next.is_valid;
		} catch (error) {
			errorMessage = isApiError(error) ? messageForApiError(error) : uiMessages.unknownError;
			return false;
		}
	}

	async function goCheckout(): Promise<void> {
		const valid = await checkCompatibility();
		if (valid && hasRequiredParts()) {
			await goto(resolve('/checkout'));
		}
	}
</script>

<svelte:head>
	<title>{uiMessages.configureTitle} · {uiMessages.siteName}</title>
</svelte:head>

<main class="p-6">
	<section class="relative overflow-hidden rounded-lg">
		<img src={catalogHeroAuth} alt="" class="h-48 w-full object-cover" />
		<div class="absolute inset-0 bg-bg-brand/60"></div>
		<div class="absolute inset-0 flex flex-col justify-end p-6">
			<h1 class="text-3xl font-semibold text-fg-inverse">{uiMessages.configureTitle}</h1>
			<p class="mt-2 text-sm text-fg-inverse/80">{uiMessages.configureLead}</p>
			<p class="mt-2 text-sm text-fg-inverse/80">
				{uiMessages.requiredProgress}
				{requiredSelected} / {requiredPartCategories.length}
			</p>
		</div>
	</section>
	{#if errorMessage !== ''}
		<p class="mt-4 text-sm text-danger" role="alert">{errorMessage}</p>
	{/if}
	<section class="mt-6">
		<CategoryRail
			{selectedCategory}
			{chosenNames}
			onselect={(category) => (selectedCategory = category)}
		/>
	</section>
	<div class="mt-6 flex gap-6">
		<section class="min-w-0 flex-1">
			<h2 class="text-lg font-semibold text-fg">{uiMessages.partsHeading}</h2>
			{#if visibleParts.length === 0}
				<p class="mt-4 rounded-lg border border-border bg-bg-elevated p-4 text-sm text-fg-muted">
					{uiMessages.emptyParts}
				</p>
			{:else}
				<ul class="mt-4 grid grid-cols-2 gap-4">
					{#each visibleParts as part (part.id)}
						<li>
							<PartCard
								{part}
								selected={orderDraftState.partIdsByCategory[part.category] === part.id}
								onselect={(next) => selectPart(next.category, next.id)}
								onclear={(next) => clearPart(next.category)}
							/>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
		<aside class="w-full max-w-sm shrink-0">
			<section class="sticky top-20 rounded-lg border border-border bg-bg-elevated p-5 shadow-sm">
				<h2 class="text-lg font-semibold text-fg">{uiMessages.summaryTitle}</h2>
				<div class="mt-4">
					<PartSummaryList parts={data.parts} />
				</div>
				<div class="mt-4 flex flex-col gap-2">
					<button
						type="button"
						class="rounded-md border border-border px-4 py-2 text-base text-fg hover:bg-bg"
						onclick={checkCompatibility}
					>
						{uiMessages.checkCompatibility}
					</button>
					<button
						type="button"
						class="rounded-md bg-bg-brand px-4 py-3 text-base font-medium text-fg-inverse hover:opacity-90 disabled:opacity-40"
						onclick={goCheckout}
						disabled={!hasRequiredParts()}
					>
						{uiMessages.goCheckout}
					</button>
				</div>
				{#if evaluation !== null}
					<ul class="mt-4 flex flex-col gap-1">
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
		</aside>
	</div>
</main>
