"""Bound even chunked bodies before multipart parsing; keep responses private."""
from starlette.responses import JSONResponse


class RequestLimits:
    def __init__(self, app, max_bytes=14*1024*1024):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        try:
            length = int(dict(scope.get("headers", [])).get(b"content-length", b"0"))
        except ValueError:
            return await JSONResponse({"detail": "Invalid content length."}, status_code=400)(scope, receive, send)
        if length > self.max_bytes:
            return await self.too_large(scope, receive, send)
        messages, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > self.max_bytes:
                return await self.too_large(scope, receive, send)
            messages.append(message)
            if not message.get("more_body", False):
                break

        async def replay():
            if messages:
                return messages.pop(0)
            return await receive()

        async def private_send(message):
            if message["type"] == "http.response.start":
                overridden = {b"x-content-type-options", b"referrer-policy", b"cache-control"}
                message["headers"] = [(key, value) for key, value in message.get("headers", []) if key.lower() not in overridden]
                message["headers"] += [(b"x-content-type-options", b"nosniff"),
                                        (b"referrer-policy", b"no-referrer"),
                                        (b"cache-control", b"private, no-store")]
            await send(message)
        await self.app(scope, replay, private_send)

    async def too_large(self, scope, receive, send):
        await JSONResponse({"detail": "Request is too large. Use an image smaller than 12 MB."},
                           status_code=413, headers={"Cache-Control": "private, no-store"})(scope, receive, send)
