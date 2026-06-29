from typing import Self

from tqdm import tqdm

from src.core.config.config import ENV


class _DisabledProgressBar:
    def step(self):
        pass

    def close(self):
        pass


class ProgressBar:
    _FORMAT = (
        "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
        "{percentage:.2f}% \x1b[35m\u25fe\x1b[93m[{elapsed_s:.3f}s, "
        "{rate_fmt}]"
    )
    _PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"

    def __new__(cls, *args) -> Self | _DisabledProgressBar:  # type: ignore
        if not ENV.progress_bar:
            return super().__new__(_DisabledProgressBar)

        return super().__new__(cls)

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

    def close(self):
        self._progress_bar.close()
