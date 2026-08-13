import { page } from 'vitest/browser';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import PartForm from './PartForm.svelte';
import { emptyPartForm } from './partFormDefaults';

describe('PartForm', () => {
	it('replaces cpu attribute fields when the category changes to memory', async () => {
		render(PartForm, {
			value: emptyPartForm('cpu'),
			submitLabel: '保存',
			errorMessage: '',
			onsubmit: async () => undefined
		});

		await expect.element(page.getByLabelText('socket')).toBeInTheDocument();
		await page.getByLabelText('カテゴリ').selectOptions('memory');
		await expect.element(page.getByLabelText('memory_type')).toBeInTheDocument();
		await expect.element(page.getByLabelText('socket')).not.toBeInTheDocument();
	});
});
