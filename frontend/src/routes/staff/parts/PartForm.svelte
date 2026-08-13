<script lang="ts">
	import { uiMessages } from '$lib/messages/ui';
	import type { CreatePartInput } from '$lib/types/part';
	import { partCategories, partCategoryLabels } from '$lib/types/partCategory';
	import PartAttributeFields from './PartAttributeFields.svelte';

	type Props = {
		value: CreatePartInput;
		submitLabel: string;
		onsubmit: (value: CreatePartInput) => Promise<void>;
		errorMessage: string;
	};

	let { value, submitLabel, onsubmit, errorMessage }: Props = $props();
	let form = $state.raw({ ...value });

	async function submit(event: Event): Promise<void> {
		event.preventDefault();
		await onsubmit(form);
	}
</script>

{#if errorMessage !== ''}
	<p class="mb-4 text-sm text-danger">{errorMessage}</p>
{/if}
<form class="flex flex-col gap-4" onsubmit={submit}>
	<label class="flex flex-col gap-1 text-sm text-fg">
		{uiMessages.sku}
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.sku}
			required
		/>
	</label>
	<label class="flex flex-col gap-1 text-sm text-fg">
		{uiMessages.name}
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.name}
			required
		/>
	</label>
	<label class="flex flex-col gap-1 text-sm text-fg">
		{uiMessages.category}
		<select
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.category}
		>
			{#each partCategories as category (category)}
				<option value={category}>{partCategoryLabels[category]}</option>
			{/each}
		</select>
	</label>
	<label class="flex flex-col gap-1 text-sm text-fg">
		{uiMessages.unitPrice}
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			min="1"
			bind:value={form.unit_price}
			required
		/>
	</label>
	<label class="flex flex-col gap-1 text-sm text-fg">
		{uiMessages.stockQuantity}
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			min="0"
			bind:value={form.stock_quantity}
			required
		/>
	</label>
	<label class="flex items-center gap-2 text-sm text-fg">
		<input type="checkbox" bind:checked={form.is_listed} />
		{uiMessages.isListed}
	</label>
	<PartAttributeFields bind:form />
	<button
		class="rounded-md bg-bg-brand px-4 py-3 text-base font-medium text-fg-inverse hover:opacity-90"
		type="submit"
	>
		{submitLabel}
	</button>
</form>
