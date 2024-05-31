class BaseException(Exception):
    default_message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class NotFoundException(BaseException):
    default_message = "Not Found"


class InsertionException(BaseException):
    default_message = "Invalid data"
