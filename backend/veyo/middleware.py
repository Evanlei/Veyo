"""Bound request size and add privacy-minded response headers."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RequestLimits(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        length = request.headers.get("content-length", "0")
        try:
            if int(length) > 14 * 1024 * 1024:
                return JSONResponse({"detail": "Request is too large. Use an image smaller than 12 MB."}, status_code=413)
        except ValueError:
            return JSONResponse({"detail": "Invalid content length."}, status_code=400)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "private, no-store"
        return response
