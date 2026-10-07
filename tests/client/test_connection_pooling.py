from concurrent.futures import ThreadPoolExecutor
from interaktiv.aiclient.helper import batch_session
from plone import api


def user(text):
    return [{"role": "user", "content": text}]


def sent_prompts(openrouter):
    return sorted(body["messages"][0]["content"] for body in openrouter.bodies)


class TestConnectionPooling:
    def test_sequential_calls_share_one_connection(self, ai_client, openrouter):
        # do it
        results = [ai_client.call(user(f"call {i}")) for i in range(20)]

        # post condition
        assert results == [f"echo: call {i}" for i in range(20)]
        assert sent_prompts(openrouter) == sorted(f"call {i}" for i in range(20))
        assert openrouter.connections == 1

    def test_consecutive_batches_reuse_connections(self, ai_client, openrouter):
        # do it
        for round_ in range(5):
            prompts = [user(f"case:sleep {round_}-{i}") for i in range(6)]
            results = ai_client.batch(prompts)
            assert results == [f"echo: case:sleep {round_}-{i}" for i in range(6)]

        # post condition
        assert len(openrouter.requests) == 30  # nothing sent twice
        assert openrouter.connections <= 3  # max_concurrent_requests

    def test_batch_concurrency_is_limited(self, ai_client, openrouter):
        # do it
        ai_client.batch([user(f"case:sleep {i}") for i in range(9)])

        # post condition
        assert len(openrouter.requests) == 9
        assert openrouter.connections <= 3

    def test_batches_in_batch_session(self, ai_client, openrouter):
        # do it
        with batch_session():
            first = ai_client.batch([user(f"a{i}") for i in range(4)])
            second = ai_client.batch([user(f"b{i}") for i in range(4)])

        # post condition
        assert first == [f"echo: a{i}" for i in range(4)]
        assert second == [f"echo: b{i}" for i in range(4)]
        assert len(openrouter.requests) == 8

    def test_calls_and_batches_mixed(self, ai_client, openrouter):
        # do it
        ai_client.call(user("one"))
        ai_client.batch([user("two"), user("three")])
        ai_client.call(user("four"))

        # post condition
        assert sent_prompts(openrouter) == ["four", "one", "three", "two"]

    def test_concurrent_callers(self, ai_client, openrouter):
        """Zope serves requests from several threads, sharing the utility."""
        # do it
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(
                pool.map(lambda i: ai_client.call(user(f"case:sleep {i}")), range(40))
            )

        # post condition
        assert results == [f"echo: case:sleep {i}" for i in range(40)]
        assert len(openrouter.requests) == 40
        assert openrouter.connections <= 8

    def test_server_closing_connections(self, ai_client, openrouter):
        # setup
        openrouter.close_connections = True

        # do it
        results = [ai_client.call(user(f"call {i}")) for i in range(5)]

        # post condition
        assert results == [f"echo: call {i}" for i in range(5)]
        assert len(openrouter.requests) == 5
        assert openrouter.connections == 5

    def test_reload_keeps_working(self, ai_client, openrouter):
        # setup
        ai_client.call(user("before"))
        api.portal.set_registry_record("interaktiv.aiclient.timeout", 2.0)

        # do it
        ai_client.reload()
        ai_client.call(user("after"))

        # post condition
        assert sent_prompts(openrouter) == ["after", "before"]
