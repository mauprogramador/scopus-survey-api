from fastapi import Request

from app.core.config.config import TOKEN, TOML
from app.core.interfaces import CSVData


class TemplateContext:
    @staticmethod
    def get_application_context(request: Request):
        return {
            'request': request,
            'token': TOKEN,
            'version': TOML.version,
            'url': TOML.url,
        }

    @staticmethod
    def get_table_context(request: Request, data: CSVData.TableType):
        return {
            'request': request,
            'content': data,
            'version': TOML.version,
            'url': TOML.url,
        }
