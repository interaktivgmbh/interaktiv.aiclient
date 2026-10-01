"""A local HTTP/1.1 keep-alive server imitating OpenRouter's chat completions.

The answer is picked by a marker in the prompt text, e.g. ``case:500``.
"""

from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

import itertools
import json
import threading
import time


def completion(content):
    return {
        "id": "gen-1",
        "object": "chat.completion",
        "created": 1,
        "model": "test/model",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": content},
            }
        ],
    }


ANSWERS = {
    "case:null": (200, completion(None)),
    "case:err200": (200, {"error": {"message": "upstream failed", "code": 502}}),
    "case:nochoices": (200, {**completion(""), "choices": None}),
    "case:500": (500, {"error": {"message": "boom"}}),
    "case:400": (400, {"error": {"message": "bad request"}}),
    "case:429": (429, {"error": {"message": "rate limited"}}),
}


def prompt_text(body):
    parts = []
    for message in body["messages"]:
        content = message["content"]
        if isinstance(content, str):
            parts.append(content)
        else:
            parts.extend(block.get("text", "") for block in content)
    return " ".join(parts)


class FakeOpenRouter:
    def __init__(self):
        self.requests = []
        self.connections = 0
        self.slow_seconds = 0.0
        self.close_connections = False
        self._lock = threading.Lock()
        server = self
        connection_ids = itertools.count(1)

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def setup(self):
                super().setup()
                self.connection_id = next(connection_ids)
                with server._lock:
                    server.connections += 1

            def log_message(self, *args):
                pass

            def do_POST(self):
                length = int(self.headers["Content-Length"])
                body = json.loads(self.rfile.read(length))
                with server._lock:
                    headers = {
                        key.lower(): value for key, value in self.headers.items()
                    }
                    server.requests.append((self.connection_id, headers, body))
                status, payload = server.answer(body)
                data = json.dumps(payload).encode()
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(data)))
                    if server.close_connections:
                        self.send_header("Connection", "close")
                    self.end_headers()
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # the client gave up (timeout)

        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._httpd.daemon_threads = True
        self.url = f"http://127.0.0.1:{self._httpd.server_address[1]}/api/v1"
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def answer(self, body):
        text = prompt_text(body)
        if "case:slow" in text:
            time.sleep(self.slow_seconds)
        if "case:sleep" in text:
            time.sleep(0.2)
        for marker, answer in ANSWERS.items():
            if marker in text:
                return answer
        return 200, completion(f"echo: {text}")

    @property
    def bodies(self):
        return [body for _, _, body in self.requests]

    def reset(self):
        with self._lock:
            self.requests.clear()
            self.connections = 0

    def stop(self):
        self._httpd.shutdown()
        self._httpd.server_close()
