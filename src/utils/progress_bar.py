from contextlib import ExitStack
from typing import Self

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from src.core.config.config import LOG


class ProgressBar:
    """Display a progress bar for running tasks"""

    __PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"
    __FORMAT = (
        "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
        "{percentage:.2f}% \x1b[35m\u25fe\x1b[93m[{elapsed_s:.3f}s, "
        "{rate_fmt}]"
    )
    __COLOR = "green"
    __POSITION = 0
    __LENGTH = 100

    def __init__(
        self, total: int, step: int = None, start: int = None
    ) -> None:
        """Display a progress bar for running tasks"""
        self.__stack = ExitStack()
        self.__total = total
        self.__step = 1 if step is None else step

        self.__progress_bar = tqdm(
            desc=self.__PREFIX,
            total=total,
            ncols=self.__LENGTH,
            bar_format=self.__FORMAT,
            position=self.__POSITION,
            colour=self.__COLOR,
        )

        if start is not None:
            self.__progress_bar.update(start * step)

    def step(self) -> None:
        progress = int(self.__progress_bar.n)
        fits = (progress + self.__step) < self.__total
        step = self.__step if fits else (self.__total - progress)
        self.__progress_bar.update(step)

    def close(self) -> None:
        self.__progress_bar.close()

    def __enter__(self) -> Self:
        self.__stack.enter_context(logging_redirect_tqdm(LOG.logger))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__progress_bar.close()
        return self.__stack.__exit__(exc_type, exc_val, exc_tb)
