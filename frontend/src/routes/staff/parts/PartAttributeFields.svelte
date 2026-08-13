<script lang="ts">
	import type { CreatePartInput } from '$lib/types/part';
	import { fieldsForCategory } from './partFormDefaults';

	type Props = {
		form: CreatePartInput;
	};

	let { form = $bindable() }: Props = $props();
	const visible = $derived(fieldsForCategory(form.category));

	function numberOrNull(raw: string): number | null {
		if (raw === '') {
			return null;
		}
		return Number(raw);
	}
</script>

{#if visible.includes('socket')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		socket
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.socket}
		/>
	</label>
{/if}
{#if visible.includes('tdp_watts')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		tdp_watts
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.tdp_watts ?? ''}
			oninput={(event) => (form.tdp_watts = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('memory_type')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		memory_type
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.memory_type}
		/>
	</label>
{/if}
{#if visible.includes('form_factor')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		form_factor
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.form_factor}
		/>
	</label>
{/if}
{#if visible.includes('memory_slot_count')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		memory_slot_count
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.memory_slot_count ?? ''}
			oninput={(event) => (form.memory_slot_count = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('sata_port_count')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		sata_port_count
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.sata_port_count ?? ''}
			oninput={(event) => (form.sata_port_count = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('m2_slot_count')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		m2_slot_count
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.m2_slot_count ?? ''}
			oninput={(event) => (form.m2_slot_count = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('module_count')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		module_count
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.module_count ?? ''}
			oninput={(event) => (form.module_count = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('capacity_gb')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		capacity_gb
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.capacity_gb ?? ''}
			oninput={(event) => (form.capacity_gb = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('length_mm')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		length_mm
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.length_mm ?? ''}
			oninput={(event) => (form.length_mm = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('interface')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		interface
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			bind:value={form.interface}
		/>
	</label>
{/if}
{#if visible.includes('wattage')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		wattage
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.wattage ?? ''}
			oninput={(event) => (form.wattage = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('max_gpu_length_mm')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		max_gpu_length_mm
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.max_gpu_length_mm ?? ''}
			oninput={(event) => (form.max_gpu_length_mm = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('max_cooler_height_mm')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		max_cooler_height_mm
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.max_cooler_height_mm ?? ''}
			oninput={(event) => (form.max_cooler_height_mm = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
{#if visible.includes('height_mm')}
	<label class="flex flex-col gap-1 text-sm text-fg">
		height_mm
		<input
			class="rounded-md border border-border bg-bg p-3 text-base text-fg"
			type="number"
			value={form.height_mm ?? ''}
			oninput={(event) => (form.height_mm = numberOrNull(event.currentTarget.value))}
		/>
	</label>
{/if}
