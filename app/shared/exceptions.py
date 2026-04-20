

class ServiceError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "SERVICE_ERROR",
        errors: dict[str, list[str]] | None = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        self.errors = errors
