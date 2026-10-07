import pytest


IMAGE = {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAAA"}}

# prompt, expected result, expected messages sent (None: nothing sent)
SCENARIOS = {
    "system and user": (
        [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}],
        "echo: sys hi",
        [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}],
    ),
    "text and image blocks": (
        [{"role": "user", "content": [{"type": "text", "text": "describe"}, IMAGE]}],
        "echo: describe ",
        [{"role": "user", "content": [{"type": "text", "text": "describe"}, IMAGE]}],
    ),
    "empty prompt": ([], None, None),
    "no prompt": (None, None, None),
    "null content in the answer": (
        [{"role": "user", "content": "case:null"}],
        "",
        [{"role": "user", "content": "case:null"}],
    ),
    "API error": (
        [{"role": "user", "content": "case:400"}],
        None,
        [{"role": "user", "content": "case:400"}],
    ),
}

# prompt, expected exception, whether a request is sent
FAILURES = {
    "error object in a 200 answer": (
        [{"role": "user", "content": "case:err200"}],
        ValueError,
        True,
    ),
    "choices null": ([{"role": "user", "content": "case:nochoices"}], TypeError, True),
}


class TestCompatibility:
    @pytest.mark.parametrize("name", SCENARIOS)
    def test_scenario(self, name, ai_client, openrouter):
        # setup
        prompt, expected_result, expected_messages = SCENARIOS[name]

        # do it
        res = ai_client.call(prompt)

        # post condition
        assert res == expected_result
        if expected_messages is None:
            assert openrouter.requests == []
        else:
            sent = [body["messages"] for body in openrouter.bodies]
            assert sent == [expected_messages]
            assert openrouter.bodies[0]["stream"] is False

    @pytest.mark.parametrize("name", FAILURES)
    def test_failure(self, name, ai_client, openrouter):
        # setup
        prompt, exception, sends_request = FAILURES[name]

        # do it
        with pytest.raises(exception):
            ai_client.call(prompt)

        # post condition
        assert len(openrouter.requests) == int(sends_request)

    @pytest.mark.parametrize("marker", ["case:500", "case:429"])
    def test_retries_server_errors(self, marker, ai_client, openrouter):
        # do it
        res = ai_client.call([{"role": "user", "content": marker}])

        # post condition
        assert res is None
        assert len(openrouter.requests) == 3  # max_retries = 2

    def test_does_not_retry_client_errors(self, ai_client, openrouter):
        # do it
        res = ai_client.call([{"role": "user", "content": "case:400"}])

        # post condition
        assert res is None
        assert len(openrouter.requests) == 1
