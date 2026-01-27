from concurrent import futures
from interaktiv.aiclient import logger
from typing import Any
from typing import Coroutine
from typing import Optional
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import asyncio


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
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
