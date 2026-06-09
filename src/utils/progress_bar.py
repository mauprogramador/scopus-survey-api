import contextlib
from typing import Self

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from src.core.config.config import ENV
from src.utils import logger


class _DisabledProgressBar:
    def step(self):
        pass


class ProgressBar:
    """Display a progress bar for running tasks"""

    _FORMAT = (
        "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
        "{percentage:.2f}% \x1b[35m\u25fe\x1b[93m[{elapsed_s:.3f}s, "
        "{rate_fmt}]"
    )
    _PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"

    def __init__(
        self, total: int, step: int = None, start: int = None
    ) -> None:
        """Display a progress bar for running tasks"""
        self._stack = contextlib.ExitStack()
        self._total = total
        self._step = 1 if step is None else step

        self._progress_bar = tqdm(
            desc=self._PREFIX,
            total=total,
            ncols=100,
            bar_format=self._FORMAT,
            position=0,
            colour="green",
        )

        if start is not None:
            self._progress_bar.update(start * step)

    @staticmethod
    def start(total: int, step: int = None, start: int = None):
        if ENV.progress_bar:
            return ProgressBar(total, step, start)
        return contextlib.nullcontext(_DisabledProgressBar())

    def step(self) -> None:
        progress = int(self._progress_bar.n)
        fits = (progress + self._step) < self._total
        step = self._step if fits else (self._total - progress)
        self._progress_bar.update(step)

    def __enter__(self) -> Self:
        self._stack.enter_context(logging_redirect_tqdm([logger.LOGGER]))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._progress_bar.close()
        return self._stack.__exit__(exc_type, exc_val, exc_tb)
