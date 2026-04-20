
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging



logging.basicConfig(level=logging.INFO)
class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Read and store the body for later
        body = await request.body()

        # Log the request details
        logging.info(f"Incoming request: {request.method} {request.url}")
        logging.info(f"Headers: {dict(request.headers)}")
        logging.info(f"Body: {body.decode('utf-8')}")

        # Recreate the request stream for FastAPI to use
        request._receive = lambda: {"type": "http.request", "body": body, "more_body": False}

        return await call_next(request)