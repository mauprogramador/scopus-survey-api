from enum import StrEnum, unique


@unique
class Language(StrEnum):
    EN_US = "en-US"
    PT_BR = "pt-BR"


@unique
class Templates(StrEnum):
    SEARCH = "search.html"
    TABLE = "table.html"
    ERROR = "error.html"
