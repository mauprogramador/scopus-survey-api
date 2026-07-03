from typing import Literal, Self

from tqdm import tqdm

from src.core.config.config import ENV


class ProgressBar:
    _FORMAT = (
        "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
        "{percentage:.2f}% \x1b[35m\u25fe\x1b[93m[{elapsed_s:.3f}s, "
        "{rate_fmt}]"
    )
    _PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"

    def __init__(
        self, total: int, step: int = None, start: int = None
    ) -> None:
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

    def step(self) -> None:
        progress = int(self._progress_bar.n)
        fits = (progress + self._step) < self._total
        step = self._step if fits else (self._total - progress)
        self._progress_bar.update(step)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
        self._progress_bar.close()
        return False


class _DisabledProgressBar(ProgressBar):
    def step(self):
        pass


def progress_bar(
    total: int, step: int = None, start: int = None
) -> ProgressBar | _DisabledProgressBar:
    if not ENV.progress_bar:
        return _DisabledProgressBar(total, step, start)

    return ProgressBar(total, step, start)
