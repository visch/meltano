"""Various small utilities for working with futures."""

from __future__ import annotations

import asyncio
import typing as t

import structlog

from meltano.core.runner import RunnerError
from meltano.core.utils import human_size

if t.TYPE_CHECKING:
    from asyncio import Task

logger = structlog.stdlib.get_logger(__name__)


def all_done(tasks: list[Task], done: set[Task]) -> bool:
    """Iterate through a task list checking if ALL tasks are in the done set."""
    return all(idx in done for idx in tasks)


def first_failed_future(exception_future: Task, done: set[Task]) -> Task | None:
    """Check if a future is completed and return the first failed (if any).

    Args:
        exception_future: The future you want to check and who's futures should
            be returned if an exception was raised.
        done: The set of completed futures you want to search.

    Returns:
        The first future that failed.
    """
    if exception_future in done:
        futures_done, _ = exception_future.result()
        if futures_failed := [
            future for future in futures_done if future.exception() is not None
        ]:
            return futures_failed.pop()
    return None


def handle_line_length_limit_error(
    exception: BaseException,
    *,
    line_length_limit: int,
    stream_buffer_size: int,
    stream_name: str,
) -> None:
    """Handle `asyncio.LimitOverrunError` from any plugin output stream.

    Args:
        exception: The exception to handle, which should be a `ValueError` with
            a `asyncio.LimitOverrunError` as its context.
        line_length_limit: The line length limit.
        stream_buffer_size: The stream buffer size.
        stream_name: A human-readable name for the stream that exceeded the
            limit, e.g. `"'tap-gitlab' stderr"`.

    Raises:
        RunnerError: An exception raised from the `asyncio.LimitOverrunError`.
    """
    # StreamReader.readline can raise a ValueError wrapping a LimitOverrunError:
    # https://github.com/python/cpython/blob/v3.12.7/Lib/asyncio/streams.py#L577
    if not isinstance(exception, ValueError):
        return

    contextual_exception = exception.__context__
    if not isinstance(contextual_exception, asyncio.LimitOverrunError):
        return

    logger.error(
        f"A line written to {stream_name} exceeded the line length limit "  # noqa: G004
        f"of {human_size(line_length_limit)} (half the buffer size "
        f"of {human_size(stream_buffer_size)}).",
    )
    logger.error(
        "To let this line be processed, increase the 'elt.buffer_size' "
        "setting to at least double the size of the largest expected line, "
        "and try again.",
    )
    logger.error(
        "To learn more, visit "
        "https://docs.meltano.com/reference/settings#eltbuffer_size",
    )
    raise RunnerError("Output line length limit exceeded") from contextual_exception  # noqa: EM101, TRY003
