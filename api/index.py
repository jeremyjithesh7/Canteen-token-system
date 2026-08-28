"""
Vercel Serverless Function entrypoint for CanteenOS FastAPI Backend.
Vercel automatically detects the 'app' ASGI instance exported here.
"""

import sys
import os

# Ensure the root project directory is in the Python path for module resolution
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app
