from contextlib import ExitStack
from typing import Self

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from src.core.config.config import LOG


class ProgressBar:
    """Display a progress bar for running tasks"""

    _PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"
    _FORMAT = (
        "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
        "{percentage:.2f}% \x1b[35m\u25fe\x1b[93m[{elapsed_s:.3f}s, "
        "{rate_fmt}]"
    )
    _COLOR = "green"
    _POSITION = 0
    _LENGTH = 100

    def __init__(
        self, total: int, step: int = None, start: int = None
    ) -> None:
        """Display a progress bar for running tasks"""
        self._stack = ExitStack()
        self._total = total
        self._step = 1 if step is None else step

        self._progress_bar = tqdm(
            desc=self._PREFIX,
            total=total,
            ncols=self._LENGTH,
            bar_format=self._FORMAT,
            position=self._POSITION,
            colour=self._COLOR,
        )

        if start is not None:
            self._progress_bar.update(start * step)

    def step(self) -> None:
        progress = int(self._progress_bar.n)
        fits = (progress + self._step) < self._total
        step = self._step if fits else (self._total - progress)
        self._progress_bar.update(step)

    def close(self) -> None:
        self._progress_bar.close()

    def __enter__(self) -> Self:
        self._stack.enter_context(logging_redirect_tqdm(LOG.logger))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._progress_bar.close()
        return self._stack.__exit__(exc_type, exc_val, exc_tb)
