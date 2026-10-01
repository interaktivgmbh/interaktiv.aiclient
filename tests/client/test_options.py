from plone import api

import pytest


def user(text):
    return [{"role": "user", "content": text}]


class TestOptions:
    def test_options_are_sent(self, ai_client, openrouter):
        # do it
        ai_client.call(user("Hello"), max_tokens=500, temperature=0.2)

        # post condition
        body = openrouter.bodies[-1]
        assert body["max_tokens"] == 500
        assert body["temperature"] == 0.2

    def test_extra_body_is_sent(self, ai_client, openrouter):
        # do it
        ai_client.call(user("Hello"), extra_body={"reasoning": {"enabled": False}})

        # post condition
        assert openrouter.bodies[-1]["reasoning"] == {"enabled": False}

    def test_extra_body_keeps_the_provider_routing(self, ai_client, openrouter):
        # setup
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "mistralai/mistral-small"
        )
        ai_client.reload()

        # do it
        ai_client.call(user("Hello"), extra_body={"reasoning": {"enabled": False}})

        # post condition
        body = openrouter.bodies[-1]
        assert body["provider"] == {"only": ["Mistral"]}
        assert body["reasoning"] == {"enabled": False}

    def test_extra_body_can_override_the_provider(self, ai_client, openrouter):
        # setup
        api.portal.set_registry_record(
            "interaktiv.aiclient.openrouter_model", "mistralai/mistral-small"
        )
        ai_client.reload()

        # do it
        ai_client.call(user("Hello"), extra_body={"provider": {"sort": "price"}})

        # post condition
        assert openrouter.bodies[-1]["provider"] == {"sort": "price"}

    def test_batch_sends_the_options_with_every_prompt(self, ai_client, openrouter):
        # do it
        ai_client.batch([user("a"), user("b"), user("c")], max_tokens=42)

        # post condition
        assert [body["max_tokens"] for body in openrouter.bodies] == [42, 42, 42]

    def test_without_options_nothing_is_added(self, ai_client, openrouter):
        # do it
        ai_client.call(user("Hello"))

        # post condition
        assert set(openrouter.bodies[-1]) == {"model", "messages", "stream"}

    @pytest.mark.parametrize(
        "options",
        [{"max_token": 5}, {"reasoning": {"enabled": False}}, {"stream": True}],
    )
    def test_unknown_or_reserved_options_raise(self, ai_client, openrouter, options):
        # do it
        with pytest.raises(TypeError):
            ai_client.call(user("Hello"), **options)
        with pytest.raises(TypeError):
            ai_client.batch([user("a"), user("b")], **options)

        # post condition
        assert openrouter.requests == []
