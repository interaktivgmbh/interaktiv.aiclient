from interaktiv.aiclient import logger
from typing import Optional
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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
