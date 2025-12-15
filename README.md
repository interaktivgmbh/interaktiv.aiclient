# interaktiv.aiclient

[![Code checks](https://github.com/interaktivgmbh/interaktiv.aiclient/actions/workflows/ci.yml/badge.svg)](https://github.com/interaktivgmbh/interaktiv.aiclient/actions/workflows/ci.yml)

This is a simple OpenRouter integration for Plone.

Tested for Plone `6.0.15`

## How to use

To get started, fill in your API key and select a model from the AI Client
controlpanel. Available models are fetched from the OpenRouter Models API.

You can then get the AI Client utility and call its `call` method with a prompt.

```python
from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.interfaces import IAIClient
from zope.component import getUtility

prompt = [
    {
        "role": "user",
        "content": "Hello World!"
    }
]

ai_client: AIClient = getUtility(IAIClient)
response = ai_client.call(prompt)
```

For more information on how to construct prompts, please refer to the
[OpenAI docs](https://platform.openai.com/docs/overview).

## Adding this add-on to your project

Install the add-on using `pip`:

```shell
pip install interaktiv.aiclient
```

or if you're using uv:

```shell
uv pip install interaktiv.aiclient
```

### Install from source

You can also install the add-on from the source. In your `mx.ini` file, add:

```ini
[interaktiv.aiclient]
url = git@github.com:interaktivgmbh/interaktiv.aiclient.git
rev = v1.0.0
extras = test
```

Or using https:

```ini
[interaktiv.aiclient]
url = https://github.com/interaktivgmbh/interaktiv.aiclient.git
rev = v1.0.0
extras = test
```

## Contribute

- [Issue tracker](https://github.com/interaktivgmbh/interaktiv.aiclient/issues)
- [Source code](https://github.com/interaktivgmbh/interaktiv.aiclient/)

## License

The project is licensed under GPLv2.

## Credits and acknowledgements

Generated using [Cookieplone (0.9.10)](https://github.com/plone/cookieplone) and [cookieplone-templates (eae593d)](https://github.com/plone/cookieplone-templates/commit/eae593d854b137cc3ab915e1c638170cbdfb3a78) on 2025-11-21 13:43:16.160908. A special thanks to all contributors and supporters!
