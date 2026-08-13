export type EvaluateConfigurationInput = {
	part_ids: number[];
};

export type ConfigurationIssue = {
	code: string;
	details: Record<string, unknown>;
};

export type ConfigurationEvaluationOutput = {
	is_valid: boolean;
	issues: ConfigurationIssue[];
};
