import os
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

# Create logs directory
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "canteen_requests.log")

# Setup logger
app_logger = logging.getLogger("canteen_api")
app_logger.setLevel(logging.INFO)

if not app_logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}')
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured file-based logging of all incoming HTTP requests and responses.
    Excludes sensitive fields (passwords, tokens, payment details).
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            log_entry = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip
            }
            app_logger.info(json.dumps(log_entry))
            return response
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_entry = {
                "method": method,
                "path": path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "error": str(e)
            }
            app_logger.error(json.dumps(log_entry))
            raise e
