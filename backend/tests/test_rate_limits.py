import unittest
from fastapi import HTTPException
from veyo.rate_limits import WriteLimiter


class RateLimitTests(unittest.TestCase):
    def test_limits_are_per_client_and_expire(self):
        current = [0]
        limiter = WriteLimiter(limit=2, interval=10, clock=lambda: current[0])
        limiter.check("one"); limiter.check("one"); limiter.check("two")
        with self.assertRaises(HTTPException) as error:
            limiter.check("one")
        self.assertEqual(error.exception.status_code, 429)
        current[0] = 11
        limiter.check("one")
        self.assertEqual(len(limiter.events["one"]), 1)
