from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


def get_model_name_from_slug(slug: str, context=None) -> str:
    factory = getUtility(IVocabularyFactory, name="interaktiv.aiclient.model_vocabulary")
    vocabulary = factory(context)

    term = vocabulary.getTerm(slug)
    return term.title if term else slug
