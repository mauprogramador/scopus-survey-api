from fastapi import HTTPException


class HttpException(HTTPException):
    def __init__(self, status_code: int, message: str) -> None:
        self.success = False
        self.status_code = status_code
        self.message = message
        super().__init__(status_code, message)

    def to_dict(self):
        return {'success': self.success, 'message': self.message}


class Unauthorized(HttpException):
    def __init__(self, message: str) -> None:
        super().__init__(401, message)


class Forbidden(HttpException):
    def __init__(self, message: str) -> None:
        super().__init__(403, message)


class NotFound(HttpException):
    def __init__(self, message: str) -> None:
        super().__init__(404, message)


class UnprocessableContent(HttpException):
    def __init__(self, message: str) -> None:
        super().__init__(422, message)


class FailedDependency(HttpException):
    def __init__(self, message: str) -> None:
        super().__init__(424, message)


class ScopusApiError(HttpException):
    def __init__(
        self, message: str, status: str, detail: str, success: bool = None
    ) -> None:
        super().__init__(422, message)
        self.status = status
        self.detail = detail
        self.success = success or False

    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'status': self.status,
            'detail': self.detail,
        }


class InternalError(HttpException):
    def __init__(self, message: str) -> None:
        super().__init__(500, message)
