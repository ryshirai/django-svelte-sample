<script lang="ts">
	type Props = {
		class?: string;
	};

	let { class: className = 'h-6 w-6 text-accent' }: Props = $props();
</script>

<svg class={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
	<path
		fill-rule="evenodd"
		d="M7 2.75h10A2.25 2.25 0 0 1 19.25 5v13A2.25 2.25 0 0 1 17 20.25h-3.25v1h-3.5v-1H7A2.25 2.25 0 0 1 4.75 18V5A2.25 2.25 0 0 1 7 2.75zm1.5 3.5h7v1.75h-7V6.25zm0 3.25h3.5v1.5h-3.5V9.5z"
	/>
</svg>
