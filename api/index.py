import sys
import os

# Comprehensive module path resolution for local dev & Vercel serverless environment (/var/task)
cwd = os.getcwd()
file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))

for path in [cwd, file_dir, parent_dir]:
    if path and path not in sys.path:
        sys.path.insert(0, path)

from backend.app.main import app
