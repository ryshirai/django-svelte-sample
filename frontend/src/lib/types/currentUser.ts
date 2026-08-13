export type CurrentUserOutput = {
	id: number;
	email: string;
	is_staff: boolean;
};

export type CreateRegistrationInput = {
	email: string;
	password: string;
};

export type CreateSessionInput = {
	email: string;
	password: string;
};
