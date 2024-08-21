from toml import load

from app.core.common.types import Poetry, PyprojectTool, TomlSettings
from app.core.config.scopus import NULL


class PyprojectToml:
    """Loads and retrieves Pyproject.toml configuration data"""

    __FILENAME = "pyproject.toml"
    __ENCODING = "utf-8"
    __APP = "app.framework.fastapi.main:app"
    __VERSION = "2.0.0"
    __HOST = "127.0.0.1"
    __PORT = 8000

    def __init__(self) -> None:
        """Loads and retrieves Pyproject.toml configuration data"""
        with open(self.__FILENAME, encoding=self.__ENCODING) as file:
            pyproject = load(file)

        tools: PyprojectTool = pyproject.get("tool", {})
        self.__application: TomlSettings = pyproject.get("application", {})
        self.__poetry: Poetry = tools.get("poetry", {})
        self.__author: str = self.__poetry.get("authors", [NULL])[0]

    @property
    def title(self) -> str:
        name = self.__poetry.get("name", NULL)
        return name if isinstance(name, str) else NULL

    @property
    def version(self) -> str:
        version = self.__poetry.get("version", self.__VERSION)
        return version if isinstance(version, str) else self.__VERSION

    @property
    def description(self) -> str:
        description = self.__poetry.get("description", NULL)
        return description if isinstance(description, str) else NULL

    @property
    def name(self) -> str:
        return self.__author[: self.__author.rindex(" ")]

    @property
    def email(self) -> str:
        start, end = self.__author.index("<"), self.__author.rindex(">")
        return self.__author[start + 1 : end]

    @property
    def documentation(self) -> str:
        documentation = self.__poetry.get("documentation", NULL)
        return documentation if isinstance(documentation, str) else NULL

    @property
    def reload(self) -> bool:
        reload = self.__application.get("reload", False)
        return reload if isinstance(reload, bool) else False

    @property
    def debug(self) -> bool:
        debug = self.__application.get("debug", False)
        return debug if isinstance(debug, bool) else False

    @property
    def logging_file(self) -> bool:
        logging_file = self.__application.get("logging_file", False)
        return logging_file if isinstance(logging_file, bool) else False

    @property
    def host(self) -> str:
        host = self.__application.get("host", self.__HOST)
        return host if isinstance(host, str) else self.__HOST

    @property
    def port(self) -> int:
        port = self.__application.get("port", self.__PORT)
        return port if isinstance(port, int) else self.__PORT

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
