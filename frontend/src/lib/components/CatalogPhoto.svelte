<script lang="ts">
	import { catalogPhotoFor } from '$lib/catalogImages';

	type Props = {
		category: string;
		sku?: string;
		alt: string;
		class?: string;
	};

	let { category, sku, alt, class: className }: Props = $props();
</script>

<img src={catalogPhotoFor({ category, sku })} {alt} class={className} />
