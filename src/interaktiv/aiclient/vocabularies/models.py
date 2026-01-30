from interaktiv.aiclient import logger
from plone.memoize import ram
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from requests.exceptions import HTTPError
from requests.exceptions import JSONDecodeError
from time import time
from typing import Any
from typing import Dict
from typing import List
from zope.component import getUtility
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import requests


def does_model_qualify(model: Dict[str, Any]) -> bool:
    architecture: Dict[str, Any] = model.get("architecture", {})

    # make sure the model supports image and text input
    input_modalities: List[str] = architecture.get("input_modalities", [])
    input_qualifies = "image" in input_modalities and "text" in input_modalities

    # make sure the model supports outputs text
    output_modalities: List[str] = architecture.get("output_modalities", [])
    output_qualifies = "text" in output_modalities

    return input_qualifies and output_qualifies


# noinspection PyUnusedLocal
def _models_cache_key(method) -> float:
    # Cache for 24 hours
    cache_duration = 60 * 60 * 24
    return time() // cache_duration


@ram.cache(_models_cache_key)
def get_openrouter_models() -> List[Dict[str, Any]]:
    registry: Registry = getUtility(IRegistry)
    api_url: str = registry.get("interaktiv.aiclient.openrouter_api_url")

    if api_url:
        models_api_url = f"{api_url}/models"

        with requests.Session() as session:
            retries = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )
            session.mount("https://", HTTPAdapter(max_retries=retries))

            try:
                res = session.get(models_api_url, timeout=60)
                res.raise_for_status()

                data = res.json()
                models = data["data"]

                # return only relevant models
                qualified_models = filter(does_model_qualify, models)
                return list(qualified_models)
            except HTTPError as e:
                logger.error(
                    f"Retrieving models from OpenRouter failed "
                    f"with status code {e.response.status_code}."
                )
            except (KeyError, JSONDecodeError):
                logger.error(
                    "Retrieving models from OpenRouter failed "
                    "because the response body is invalid."
                )

    return []


def format_model(model: Dict[str, Any]) -> Dict[str, str]:
    return {
        "value": model["id"],
        "token": model["id"],
        "title": model["name"],
    }


# noinspection PyUnusedLocal
@provider(IVocabularyFactory)
def model_vocabulary(context) -> SimpleVocabulary:
    models = get_openrouter_models()

    # reduce model data for SimpleTerm
    formatted_models = [format_model(model) for model in models]
    sorted_models = sorted(formatted_models, key=lambda model: model["title"])

    terms = [SimpleTerm(**model) for model in sorted_models]

    return SimpleVocabulary(terms)
