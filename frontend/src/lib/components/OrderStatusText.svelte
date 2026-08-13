<script lang="ts">
	import { uiMessages } from '$lib/messages/ui';

	type Props = {
		status: string;
	};

	let { status }: Props = $props();

	const labels: Record<string, string> = {
		paid: uiMessages.orderStatusPaid,
		preparing: uiMessages.orderStatusPreparing,
		shipped: uiMessages.orderStatusShipped,
		cancelled: uiMessages.orderStatusCancelled
	};

	const tones: Record<string, string> = {
		paid: 'bg-bg-subtle text-fg',
		preparing: 'bg-bg-subtle text-warning',
		shipped: 'bg-bg-subtle text-success',
		cancelled: 'bg-bg-subtle text-danger'
	};
</script>

<span
	class="inline-block rounded-full px-3 py-1 text-sm whitespace-nowrap {tones[status] ??
		'bg-bg-subtle text-fg'}"
>
	{labels[status] ?? status}
</span>
