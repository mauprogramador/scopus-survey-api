from tqdm import tqdm


class ProgressBar:
    """Display a progress bar for running tasks"""

    __PREFIX = "\x1b[93m[\x1b[92mPROGRESS\x1b[93m]\x1b[m"
    __FORMAT = (
        "{desc}\x1b[93m {n_fmt}/{total_fmt} \u2503\x1b[m{bar}\x1b[93m\u2503 "
        "{percentage:.2f}% \x1b[35m\u25FE\x1b[93m[{elapsed_s:.3f}s, "
        "{rate_fmt}]"
    )
    __COLOR = "green"
    __POSITION = 0
    __LENGTH = 100

    def __init__(
        self, total: int, step: int = None, start: int = None
    ) -> None:
        """Display a progress bar for running tasks"""
        self.__was_started = True
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

    def step_progress(self) -> None:
        if self.__was_started:
            progress = int(self.__progress_bar.n)
            fits = (progress + self.__step) < self.__total
            step = self.__step if fits else (self.__total - progress)
            self.__progress_bar.update(step)

    def close(self) -> None:
        self.__progress_bar.close()
