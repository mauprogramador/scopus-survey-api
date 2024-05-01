from http import HTTPStatus

from fastapi import Response

from app.adapters.gateway.api_config import ApiConfig


class ScopusApiError(Exception):
    DEFAULT_DETAIL = 'null'
    DECODING = 'utf-8'

    def __init__(self, response: Response) -> None:
        self.success = False
        self.status_code = 422

        self.message = 'Invalid Response from Scopus API'
        super().__init__(self.message)

        status_phrase = HTTPStatus(response.status_code).phrase
        self.status = f'{response.status_code} - {status_phrase}'

        self.detail = ApiConfig.RESPONSES.get(
            response.status_code, self.DEFAULT_DETAIL
        )
        self.body = response.body.decode(self.DECODING)

    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'status': self.status,
            'detail': self.detail,
            'body': self.body,
        }
