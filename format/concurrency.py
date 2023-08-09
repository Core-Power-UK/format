"""Handle formatting multiple files via multiprocessing.

Based off of black.concurrency.
"""
from __future__ import annotations

import asyncio
import os
import signal
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

from black.concurrency import cancel, maybe_install_uvloop, shutdown
from black.report import Changed, Report

from format import fix_file

if TYPE_CHECKING:
    from collections.abc import Sequence


def fix_multiple_files(files: Sequence[str]) -> int:
    """Fix multiple files.

    Similar to black.concurrency.reformat_many updated to use fix_file function.
    """
    maybe_install_uvloop()

    workers = os.cpu_count() or 1

    executor: Executor
    try:
        executor = ProcessPoolExecutor(max_workers=workers)
    except (ImportError, NotImplementedError, OSError):
        # We arrive here if the underlying system does not support multi-processing
        # like in AWS Lambda or Termux, in which case we gracefully fallback to
        # a ThreadPoolExecutor with just a single worker (more workers would not do us
        # any good due to the Global Interpreter Lock)
        executor = ThreadPoolExecutor(max_workers=1)

    report = Report()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            schedule_formatting(
                files=set(files),
                report=report,
                loop=loop,
                executor=executor,
            ),
        )
    finally:
        try:
            shutdown(loop)
        finally:
            asyncio.set_event_loop(None)

        if executor is not None:
            executor.shutdown()

    return report.return_code


async def schedule_formatting(
    files: set[str],
    report: Report,
    loop: asyncio.AbstractEventLoop,
    executor: Executor,
) -> None:
    """Run formatting of `files` in parallel using the provided `executor`.

    (Use ProcessPoolExecutors for actual parallelism.)

    Similar to black.concurrency.schedule_formatting updated to use fix_file function.
    """
    cancelled = []
    tasks = {
        asyncio.ensure_future(loop.run_in_executor(executor, fix_file, src)): src
        for src in sorted(files)
    }
    pending = tasks.keys()
    try:
        loop.add_signal_handler(signal.SIGINT, cancel, pending)
        loop.add_signal_handler(signal.SIGTERM, cancel, pending)
    except NotImplementedError:
        # There are no good alternatives for these on Windows.
        pass

    while pending:
        done, _ = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            src = tasks.pop(task)
            if task.cancelled():
                cancelled.append(task)
            elif task.exception():
                report.failed(Path(src), str(task.exception()))
            else:
                report.done(Path(src), Changed.YES if task.result() else Changed.NO)

    if cancelled:
        await asyncio.gather(*cancelled, return_exceptions=True)
