class BusinessError(Exception):
    code: str
    http_status: int = 400

    def __init__(self, *, details: dict[str, object] | None = None) -> None:
        self.details = details or {}
