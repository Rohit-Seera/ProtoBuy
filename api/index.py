import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app as backend_app


async def app(scope, receive, send):
    """Vercel ASGI entrypoint: map /api/* to the existing FastAPI routes."""
    if scope["type"] == "http":
        path = scope.get("path", "")
        if path == "/api":
            new_path = "/"
        elif path.startswith("/api/"):
            new_path = path[4:]
        else:
            new_path = path
        scope = dict(scope)
        scope["path"] = new_path
        raw_path = scope.get("raw_path")
        if raw_path:
            raw = raw_path.decode("utf-8")
            if raw == "/api":
                scope["raw_path"] = b"/"
            elif raw.startswith("/api/"):
                scope["raw_path"] = raw[4:].encode("utf-8")
    await backend_app(scope, receive, send)
