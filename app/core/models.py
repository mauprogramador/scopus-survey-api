from pydantic import BaseModel, Field


class ApiHeaders(BaseModel):
    content_type: str = Field(alias='Content-Type', default='application/json')
    accept: str = Field(alias='Accept', default='application/json')
    user_agent: str = Field(alias='User-Agent', default='Mozilla/5.0')
    apikey: str = Field(serialization_alias='X-ELS-APIKey')


class PageHeaders(BaseModel):
    cache_control: str = Field(alias='Cache-Control', default='no-cache')
    pragma: str = Field(alias='Pragma', default='no-cache')
    referer: str = Field(alias='Referer', default='https://www.scopus.com/')
    connection: str = Field(alias='Connection', default='keep-alive')
    content: str = Field(alias='Content-Type', default='text/plain')
    origin: str = Field(alias='Origin', default='https://www.scopus.com')
    accept_encoding: str = Field(
        alias='Accept-Encoding', default='gzip, deflate, br'
    )
    accept_charset: str = Field(
        alias='Accept-Charset', default='ISO-8859-1,utf-8;q=0.7,*;q=0.3'
    )
    accept_language: str = Field(
        alias='Accept-Language', default='pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    )
    accept: str = Field(
        alias='Accept',
        default=(
            'text/html,application/xhtml+xml,application/xml;q=0.9'
            ',image/avif,image/webp,image/apng,*/*;q=0.8,application/'
            'signed-exchange;v=b3;q=0.7'
        ),
    )
    user_agent: str = Field(
        alias='User-Agent',
        default=(
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ),
    )
