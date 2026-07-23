from typing import Any, Self

from pydantic import (
    Field,
    ValidationError,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


# e.g. 127.0.0.1, 0.0.0.0
_HOST_PATTERN = r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )

    secret_key: str = Field(
        exclude=True,
        frozen=True,
        repr=False,
        min_length=32,
        max_length=128,
    )
    host: str = Field(
        default="127.0.0.1",
        pattern=_HOST_PATTERN,
        min_length=7,
        max_length=15,
    )
    port: int = Field(default=8000, gt=0, lt=65535, decimal_places=None)
    reload: bool = Field(default=False)
    workers: int = Field(default=1, gt=0, lt=5, decimal_places=None)
    logging_file: bool = Field(default=False)
    debug: bool = Field(default=False)
    progress_bar: bool = Field(default=True)

    @classmethod
    def settings_customise_sources(  # pylint: disable=R0913,R0917
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (dotenv_settings, env_settings)

    @model_validator(mode="after")
    def check_reload_with_workers(self) -> Self:
        if self.reload is True and self.workers > 1:
            raise ValueError(
                "\033[33mConfiguration conflict error:\033[31m cannot"
                " use reload together with multiple workers\033[m"
            )
        return self

    @field_validator("secret_key", mode="wrap")
    @classmethod
    def validate_secret_key(
        cls, value: Any, handler: ValidatorFunctionWrapHandler
    ) -> Any:
        try:
            return handler(value)
        except ValidationError as exc:
            raise ValueError(
                "\033[33mSecret Key error:\033[31m You must set a valid "
                "SECRET_KEY in .env with 32-128 characters\033[m"
            ) from exc
