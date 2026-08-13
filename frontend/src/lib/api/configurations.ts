import { apiPost } from '$lib/api/client';
import type {
	ConfigurationEvaluationOutput,
	EvaluateConfigurationInput
} from '$lib/types/configuration';

export async function evaluateConfiguration(
	input: EvaluateConfigurationInput
): Promise<ConfigurationEvaluationOutput> {
	return apiPost<ConfigurationEvaluationOutput>('/api/v1/configurations/evaluations', input);
}
