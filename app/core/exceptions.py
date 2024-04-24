class ScopusApiError(Exception):
    def __init__(
        self, message: str, status: str, detail: str, success: bool = None
    ) -> None:
        super().__init__(message)
        self.success = success or False
        self.status_code = 422
        self.message = message
        self.status = status
        self.detail = detail

    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'status': self.status,
            'detail': self.detail,
        }
