type AuthenticationRequiredHandler = () => void;

let handler: AuthenticationRequiredHandler | null = null;

export function onAuthenticationRequired(next: AuthenticationRequiredHandler): void {
	handler = next;
}

export function notifyAuthenticationRequired(): void {
	handler?.();
}
