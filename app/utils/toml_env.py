from os import getenv
from typing import Any, Type

from dotenv import load_dotenv
from toml import load

from app.core.common.types import TomlSettings


class TomlEnvConfig:
    """Loads and retrieves Pyproject.toml and ENV configuration data"""

    __APP = "app.framework.fastapi.app:app"
    __FILENAME = "pyproject.toml"
    __HOST = "127.0.0.1"
    __ENCODING = "utf-8"
    __VERSION = "3.0.0"
    __PORT = 8000

    def __init__(self) -> None:
        """Loads and retrieves Pyproject.toml and ENV configuration data"""
        with open(self.__FILENAME, encoding=self.__ENCODING) as file:
            pyproject = load(file)

        load_dotenv()
        self.__application: TomlSettings = pyproject.get("application", {})
        tools: dict[str, Any] = pyproject.get("tool", {})
        self.__poetry: dict[str, Any] = tools.get("poetry", {})

        self.__reload: bool = self.__getenv("reload", bool, False)
        self.__host: str = self.__getenv("host", str, self.__HOST)
        self.__port: int = self.__getenv("port", int, self.__PORT)
        self.__logging_file: bool = self.__getenv("logging_file", bool, False)
        self.__workers: int = self.__getenv("workers", int, 1)

    @property
    def url(self) -> str:
        return f"http://{self.__host}:{self.__port}"

    @property
    def version(self) -> str:
        value = self.__poetry.get("version")
        return self.__assure(value, str, self.__VERSION)

    @property
    def debug(self) -> bool:
        return self.__getenv("debug", bool, False)

    @property
    def uvicorn(self) -> TomlSettings:
        return {
            "app": self.__APP,
            "host": self.__host,
            "port": self.__port,
            "reload": self.__reload,
            "workers": self.__workers
        }

    @property
    def logger_config(self) -> TomlSettings:
        return {
            "debug": self.debug,
            "logging_file": self.__logging_file,
            "host": self.__host,
            "port": self.__port,
        }

    @property
    def pyproject(self) -> TomlSettings:
        return {
            "version": self.version,
            "debug": self.debug,
            "logging_file": self.__logging_file,
            "host": self.__host,
            "port": self.__port,
            "reload": self.__reload,
        }

    def __assure(self, value: Any, spected_type: Type, default: Any) -> Any:
        if value is None or type(value) is not spected_type:
            return default
        return value

    def __getenv(self, name: str, spected_type: Type, default: Any) -> Any:
        value = self.__application.get(name)
        toml_config = self.__assure(value, spected_type, default)
        env_variable = getenv(name.upper())
        if env_variable is not None:
            if spected_type is bool:
                env_variable = env_variable.title()
            try:
                return spected_type(env_variable)
            except ValueError:
                return toml_config
        return toml_config
