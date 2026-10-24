import asyncio
import unittest
from veyo.middleware import RequestLimits


class BodyLimitTests(unittest.TestCase):
    def test_chunked_body_is_rejected_before_the_application_receives_it(self):
        reached_app = False
        async def app(scope, receive, send):
            nonlocal reached_app
            reached_app = True
        messages = [{"type": "http.request", "body": b"abc", "more_body": True},
                    {"type": "http.request", "body": b"def", "more_body": False}]
        sent = []
        async def receive():
            return messages.pop(0)
        async def send(message):
            sent.append(message)
        asyncio.run(RequestLimits(app, max_bytes=5)({"type": "http", "headers": []}, receive, send))
        self.assertFalse(reached_app)
        self.assertEqual(sent[0]["status"], 413)
