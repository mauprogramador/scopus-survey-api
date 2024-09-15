from os import getenv
from typing import Any, Type

from dotenv import load_dotenv
from toml import load

from app.core.common.types import Poetry, PyprojectTool, TomlSettings
from app.core.config.scopus import NULL


class TomlEnv:
    """Loads and retrieves Pyproject.toml and ENV configuration data"""

    __APP = "app.framework.fastapi.main:app"
    __FILENAME = "pyproject.toml"
    __AUTHORS = ["null <null@null>"]
    __HOST = "127.0.0.1"
    __ENCODING = "utf-8"
    __VERSION = "2.0.0"
    __PORT = 8000

    def __init__(self) -> None:
        """Loads and retrieves Pyproject.toml and ENV configuration data"""
        with open(self.__FILENAME, encoding=self.__ENCODING) as file:
            pyproject = load(file)

        load_dotenv()
        tools: PyprojectTool = pyproject.get("tool", {})
        self.__application: TomlSettings = pyproject.get("application", {})
        self.__poetry: Poetry = tools.get("poetry", {})

        value = self.__poetry.get("authors")
        authors: list = self.__assure(value, list, self.__AUTHORS)
        self.__author: str = self.__assure(authors[0], str, self.__AUTHORS[0])

    @property
    def title(self) -> str:
        value = self.__poetry.get("name")
        return self.__assure(value, str, NULL)

    @property
    def version(self) -> str:
        value = self.__poetry.get("version")
        return self.__assure(value, str, self.__VERSION)

    @property
    def description(self) -> str:
        value = self.__poetry.get("description")
        return self.__assure(value, str, NULL)

    @property
    def name(self) -> str:
        return self.__author[: self.__author.rindex(" ")]

    @property
    def email(self) -> str:
        start, end = self.__author.index("<"), self.__author.rindex(">")
        return self.__author[start + 1 : end]

    @property
    def documentation(self) -> str:
        value = self.__poetry.get("documentation")
        return self.__assure(value, str, NULL)

    @property
    def reload(self) -> bool:
        return self.__getenv("reload", bool, False)

    @property
    def debug(self) -> bool:
        return self.__getenv("debug", bool, False)

    @property
    def logging_file(self) -> bool:
        return self.__getenv("logging_file", bool, False)

    @property
    def host(self) -> str:
        return self.__getenv("host", str, self.__HOST)

    @property
    def port(self) -> int:
        return self.__getenv("port", int, self.__PORT)

    @property
    def uvicorn(self) -> TomlSettings:
        return {
            "app": self.__APP,
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
        }

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def pyproject(self) -> TomlSettings:
        return {
            "version": self.version,
            "debug": self.debug,
            "logging_file": self.logging_file,
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
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
