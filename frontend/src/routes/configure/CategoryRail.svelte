<script lang="ts">
	import CatalogPhoto from '$lib/components/CatalogPhoto.svelte';
	import { uiMessages } from '$lib/messages/ui';
	import type { PartCategory } from '$lib/types/part';
	import {
		partCategories,
		partCategoryLabels,
		requiredPartCategories
	} from '$lib/types/partCategory';

	type Props = {
		selectedCategory: PartCategory;
		chosenNames: Record<PartCategory, string | null>;
		onselect: (category: PartCategory) => void;
	};

	let { selectedCategory, chosenNames, onselect }: Props = $props();

	function isRequired(category: PartCategory): boolean {
		return requiredPartCategories.includes(category);
	}

	function tileClass(category: PartCategory): string {
		if (selectedCategory === category) {
			return 'flex w-full min-w-0 flex-col gap-2 rounded-lg border-2 border-accent bg-bg-elevated p-2 text-left';
		}
		return 'flex w-full min-w-0 flex-col gap-2 rounded-lg border border-border bg-bg-elevated p-2 text-left hover:bg-bg';
	}
</script>

<ul class="grid grid-cols-8 gap-2">
	{#each partCategories as category (category)}
		{@const chosenName = chosenNames[category]}
		<li class="min-w-0">
			<button
				type="button"
				class={tileClass(category)}
				aria-pressed={selectedCategory === category}
				onclick={() => onselect(category)}
			>
				<CatalogPhoto {category} alt="" class="h-16 w-full rounded-md object-cover" />
				<span class="block truncate text-sm font-medium text-fg"
					>{partCategoryLabels[category]}</span
				>
				<span class="block truncate text-sm text-fg-muted">
					{#if chosenName !== null}
						{chosenName}
					{:else if isRequired(category)}
						{uiMessages.required} · {uiMessages.unselected}
					{:else}
						{uiMessages.optional}
					{/if}
				</span>
			</button>
		</li>
	{/each}
</ul>
