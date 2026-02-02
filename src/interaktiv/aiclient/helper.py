from concurrent import futures
from contextlib import contextmanager
from interaktiv.aiclient import logger
from interaktiv.aiclient.session import _SessionManager
from typing import Any
from typing import Coroutine
from typing import Generator
from typing import Optional
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import asyncio


_session_manager = _SessionManager()


@contextmanager
def batch_session() -> Generator[None, None, None]:
    """
    Context manager that maintains a persistent event loop for batch operations.

    Use this when making multiple batch calls to ensure the httpx connection pool
    is reused across calls, preventing connection errors.

    Example:
        with batch_session():
            for batch in batches:
                ai_client.batch(batch)
    """
    started = _session_manager.start()
    try:
        yield
    finally:
        if started:
            _session_manager.stop()


def get_model_name_from_slug(slug: str, context=None) -> str:
    factory = getUtility(
        IVocabularyFactory, name="interaktiv.aiclient.model_vocabulary"
    )
    vocabulary: Optional[SimpleVocabulary] = factory(context)

    if vocabulary is None:
        logger.warning("'model_vocabulary' vocabulary not found.")
        return slug

    try:
        term: SimpleTerm = vocabulary.getTerm(slug)
        return getattr(term, "title", slug)
    except LookupError:
        return slug


def safe_execute_async(coro: Coroutine[Any, Any, Any]) -> Any:
    if _session_manager.active:
        return _session_manager.run(coro)

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
