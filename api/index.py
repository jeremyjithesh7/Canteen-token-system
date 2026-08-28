import sys
import os
import traceback

# Comprehensive module path resolution for local dev & Vercel serverless environment (/var/task)
cwd = os.getcwd()
file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))

for path in [cwd, parent_dir, file_dir]:
    if path and path not in sys.path:
        sys.path.insert(0, path)

try:
    from backend.app.main import app
except Exception as e:
    tb = traceback.format_exc()
    print("FATAL STARTUP ERROR IN api/index.py:\n", tb, flush=True)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def catch_all_error(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Server startup failure",
                "detail": str(e),
                "traceback": tb.splitlines()
            }
        )
