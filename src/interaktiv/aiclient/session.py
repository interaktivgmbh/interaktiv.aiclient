from concurrent import futures
from typing import Any
from typing import Coroutine
from typing import Optional

import asyncio
import contextlib
import threading


class _SessionManager:
    """
    Manages a persistent event loop for batch operations.

    This ensures that the same event loop (and thus the same httpx connection pool)
    is reused across multiple batch calls, preventing connection errors that occur
    when asyncio.run() creates and destroys event loops between calls.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._executor: Optional[futures.ThreadPoolExecutor] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def start(self) -> bool:
        with self._lock:
            if self._active:
                return False
            self._active = True
            self._executor = futures.ThreadPoolExecutor(max_workers=1)
            return True

    def stop(self) -> None:
        with self._lock:
            if not self._active:
                return

            if self._loop is not None and self._executor is not None:

                def _close_loop():
                    if self._loop and not self._loop.is_closed():
                        self._loop.close()

                with contextlib.suppress(Exception):
                    self._executor.submit(_close_loop).result(timeout=5)

            if self._executor is not None:
                self._executor.shutdown(wait=True)

            self._active = False
            self._executor = None
            self._loop = None

    def run(self, coro: Coroutine[Any, Any, Any]) -> Any:
        if not self._active or self._executor is None:
            raise RuntimeError("No active session.")

        def _run_in_thread():
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
            return self._loop.run_until_complete(coro)

        future = self._executor.submit(_run_in_thread)
        return future.result()
