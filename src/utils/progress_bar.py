import asyncio
import contextlib
from collections.abc import Callable, Generator
from typing import Any, Literal

from tqdm import tqdm

from src.core.config.config import ENV


_FORMAT = (
    "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
    "{percentage:.2f}% \x1b[35m\u25fe\x1b[93m[{elapsed_s:.3f}s, {rate_fmt}]"
)
_PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"


@contextlib.contextmanager
def progress_bar(
    progress_range: range,
) -> Generator[Callable[[asyncio.Task], None], Any, Literal[False]]:
    disable = None if ENV.progress_bar else False

    pbar = tqdm(
        iterable=progress_range,
        desc=_PREFIX,
        total=progress_range.stop,
        ncols=100,
        disable=disable,  # Disable on non-TTY
        bar_format=_FORMAT,
        initial=progress_range.start,
        position=0,
        colour="green",
    )

    def _step(task: asyncio.Task) -> None:  # pylint: disable=W0613
        pbar.update()

    yield _step

    pbar.close()
    return False
