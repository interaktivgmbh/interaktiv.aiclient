from interaktiv.aiclient.helper import get_model_name_from_slug
from interaktiv.aiclient.vocabularies.models import model_vocabulary
from unittest import mock

import requests


SAMPLE_RESPONSE = {
    "data": [
        {
            "id": "openai/gpt-4",
            "canonical_slug": "openai/gpt-4",
            "hugging_face_id": None,
            "name": "OpenAI: GPT-4",
            "created": 1685232000,
            "description": "OpenAI's flagship model, GPT-4 is a large-scale multimodal language model capable of solving difficult problems with greater accuracy than previous models due to its broader general knowledge and advanced reasoning capabilities. Training data: up to Sep 2021.",
            "context_length": 8191,
            "architecture": {
                "modality": "text-\u003etext",
                "input_modalities": ["text"],
                "output_modalities": ["text"],
                "tokenizer": "GPT",
                "instruct_type": None,
            },
            "pricing": {
                "prompt": "0.00003",
                "completion": "0.00006",
                "request": "0",
                "image": "0",
                "web_search": "0",
                "internal_reasoning": "0",
            },
            "top_provider": {
                "context_length": 8191,
                "max_completion_tokens": 4096,
                "is_moderated": True,
            },
            "per_request_limits": None,
            "supported_parameters": [
                "frequency_penalty",
                "logit_bias",
                "logprobs",
                "max_tokens",
                "presence_penalty",
                "response_format",
                "seed",
                "stop",
                "structured_outputs",
                "temperature",
                "tool_choice",
                "tools",
                "top_logprobs",
                "top_p",
            ],
            "default_parameters": {},
        },
        {
            "id": "google/gemini-2.5-flash-image",
            "canonical_slug": "google/gemini-2.5-flash-image",
            "hugging_face_id": "",
            "name": "Google: Gemini 2.5 Flash Image (Nano Banana)",
            "created": 1759870431,
            "description": 'Gemini 2.5 Flash Image, a.k.a. "Nano Banana," is now generally available. It is a state of the art image generation model with contextual understanding. It is capable of image generation, edits, and multi-turn conversations. Aspect ratios can be controlled with the [image_config API Parameter](https://openrouter.ai/docs/features/multimodal/image-generation#image-aspect-ratio-configuration)',
            "context_length": 32768,
            "architecture": {
                "modality": "text+image-\u003etext+image",
                "input_modalities": ["image", "text"],
                "output_modalities": ["image", "text"],
                "tokenizer": "Gemini",
                "instruct_type": None,
            },
            "pricing": {
                "prompt": "0.0000003",
                "completion": "0.0000025",
                "request": "0",
                "image": "0.001238",
                "web_search": "0",
                "internal_reasoning": "0",
            },
            "top_provider": {
                "context_length": 32768,
                "max_completion_tokens": 32768,
                "is_moderated": False,
            },
            "per_request_limits": None,
            "supported_parameters": [
                "max_tokens",
                "response_format",
                "seed",
                "structured_outputs",
                "temperature",
                "top_p",
            ],
            "default_parameters": {
                "temperature": None,
                "top_p": None,
                "frequency_penalty": None,
            },
        },
    ]
}


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.exceptions.HTTPError(response=self)

    def json(self):
        return self._json_data


class TestHelper:
    @mock.patch("interaktiv.aiclient.vocabularies.models.requests.get")
    def test_get_model_name_from_slug(self, mock_requests_get, portal):
        # setup
        mock_requests_get.return_value = MockResponse(SAMPLE_RESPONSE)
        vocabulary = model_vocabulary(None)

        # pre condition
        terms = [term.value for term in vocabulary]
        assert "google/gemini-2.5-flash-image" in terms

        # do it
        res = get_model_name_from_slug("google/gemini-2.5-flash-image", portal)

        # post condition
        assert res == "Google: Gemini 2.5 Flash Image (Nano Banana)"

    @mock.patch("interaktiv.aiclient.helper.getUtility")
    def test_get_model_name_from_slug__no_vocabulary(self, mock_getutility, portal):
        # setup
        mock_getutility.return_value = lambda x: None

        # do it
        # if in any case the vocabulary can't be found, the slug should simply be returned
        res = get_model_name_from_slug("google/gemini-2.5-flash-image", portal)

        # post condition
        assert res == "google/gemini-2.5-flash-image"

    @mock.patch("interaktiv.aiclient.vocabularies.models.requests.get")
    def test_get_model_name_from_slug__not_found(self, mock_requests_get, portal):
        # setup
        mock_requests_get.return_value = MockResponse(SAMPLE_RESPONSE)
        vocabulary = model_vocabulary(None)

        # pre condition
        terms = [term.value for term in vocabulary]
        assert "bla/blabla" not in terms

        # do it
        # if the slug doesn't correspond to a model, the slug should simply be returned
        res = get_model_name_from_slug("bla/blabla", portal)

        # post condition
        assert res == "bla/blabla"
