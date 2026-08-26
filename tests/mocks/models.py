import contextlib
import cProfile
import io
import logging
import pstats
import re
import shutil
import time
import tracemalloc
from typing import Any, Self

from pandas import DataFrame

from src.core.domain.types import Json


class MockAsyncContext:
    """Mock async contexts `async with`"""

    def __call__(self, *args: Any, **kwds: Any) -> Self:
        return self

    async def __await__(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class ReportTracker:
    _NOTE = "[{}] Duration ({:.4f}s) exceeded limit ({:.4f}s)"
    # e.g. 45 function calls
    _INDENT_RE = re.compile(r"\n? *(\d* function calls)")
    _FILTER = (tracemalloc.Filter(True, "*/src*"),)
    _TOP = 10  # Top bottlenecks functions
    _TOLERANCE = 0.30  # 30%

    def __init__(self) -> None:
        self._metrics: list[Json] = []
        self._profiler: cProfile.Profile | None = None
        self._snapshot: tracemalloc.Snapshot | None = None
        self._peak_bytes: float | None = None

    @contextlib.contextmanager
    def timeit(self, expected_time: float, op_name: str):
        time_limit = expected_time * (1 + self._TOLERANCE)
        half_limit = time_limit / 2.0

        start_time = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start_time

        if elapsed > time_limit:
            status = "FAILED (Too Slow)"
        elif elapsed < half_limit:
            status = "OPPORTUNITY (Fast)"
        else:
            status = "PASSED"

        report = {
            "Operation": op_name,
            "Elapsed (s)": round(elapsed, 4),
            "Target (s)": round(expected_time, 4),
            "Limit (s)": round(time_limit, 4),
            "Status": status,
        }
        self._metrics.append(report)

        note = self._NOTE.format(op_name, elapsed, time_limit)
        assert elapsed <= time_limit, note

    @contextlib.contextmanager
    def measure(self):
        logging.disable(logging.CRITICAL)

        if self._profiler is None:
            self._profiler = cProfile.Profile()

        tracemalloc.start()
        self._profiler.enable()

        try:
            yield
        finally:
            self._profiler.disable()

        self._snapshot = tracemalloc.take_snapshot()
        _, peak_bytes = tracemalloc.get_traced_memory()

        tracemalloc.stop()
        logging.disable(logging.NOTSET)
        self._peak_bytes = round(peak_bytes / (1024**2), 2)

    def _header(self, title: str, lib: str) -> None:
        print(f"\n\033[37;1m{title}\033[m (\033[36m{lib}\033[m)\n")

    def show_report(self):
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
        print()
        print(" \033[93mReport\033[m ".center((width + 8), "-"))
        self._header("Operational Metrics", "time.perf_counter")

        df = DataFrame(self._metrics)
        print(df.to_string(index=False))

        if not self._profiler and not self._snapshot:
            print()

        if self._profiler is not None:
            buffer = io.StringIO()
            stats = pstats.Stats(self._profiler, stream=buffer)

            stats.sort_stats("cumulative")
            stats.print_stats("/src", self._TOP)

            stats.sort_stats("tottime")
            stats.print_stats("/src", self._TOP)

            self._header(f"Top {self._TOP} CPU Bottlenecks", "cProfile")
            print(self._INDENT_RE.sub(r"   \1", buffer.getvalue().strip()))

        if self._snapshot is not None:
            self._header(f"Top {self._TOP} Memory Allocations", "tracemalloc")
            total = len(self._snapshot.statistics("lineno"))

            snapshot = self._snapshot.filter_traces(self._FILTER)
            stats = snapshot.statistics("lineno")

            print(
                f"List reduced from {total} to {len(stats)} "
                "due to restriction <'/src'>\n"
                f"List reduced from {len(stats)} to {self._TOP} "
                f"due to restriction <{self._TOP}>\n"
            )

            for stat in stats[: self._TOP]:
                print(
                    f"{stat.traceback[0]}: {stat.size / 1024:.1f} "
                    f"KiB ({stat.count} blocks)"
                )

            main_tsize = sum(stat.size for stat in stats) / 1024
            print(f"\nTotal Allocated: {main_tsize:.1f} KiB")

            other = stats[self._TOP :]
            if other:
                other_tsize = sum(stat.size for stat in other) / 1024
                print(f"Other {len(other)} Processes: {other_tsize:.1f} KiB")

            if self._peak_bytes is not None:
                print(f"Peak Memory: {self._peak_bytes} MiB\n")
