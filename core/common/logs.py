
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging


logging.basicConfig(level=logging.INFO)

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}


def _sanitize_headers(headers: dict) -> dict:
    return {
        key: ("<redacted>" if key.lower() in SENSITIVE_HEADERS else value)
        for key, value in headers.items()
    }


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"Incoming request: {request.method} {request.url}")
        logging.info(f"Headers: {_sanitize_headers(dict(request.headers))}")
        return await call_next(request)
