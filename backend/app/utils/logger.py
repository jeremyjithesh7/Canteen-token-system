import os
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

import sys

# Setup logger
app_logger = logging.getLogger("canteen_api")
app_logger.setLevel(logging.INFO)

if not app_logger.handlers:
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}')
    
    # 1. Console / Stdout handler (Required for Serverless / Vercel container logs)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    app_logger.addHandler(stream_handler)

    # 2. Rotating File handler (Enabled only on writable local environments)
    try:
        LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
        os.makedirs(LOGS_DIR, exist_ok=True)
        LOG_FILE = os.path.join(LOGS_DIR, "canteen_requests.log")
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
        file_handler.setFormatter(formatter)
        app_logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # Read-only filesystem in serverless environments (e.g. AWS Lambda / Vercel)
        pass

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
