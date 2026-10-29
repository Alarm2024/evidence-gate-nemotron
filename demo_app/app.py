"""Minimal demo entrypoints wiring vulnerable modules."""

from demo_app.config import get_api_secret
from demo_app.db import get_user_display_name
from demo_app.files import read_user_file

__all__ = ["get_api_secret", "get_user_display_name", "read_user_file"]
