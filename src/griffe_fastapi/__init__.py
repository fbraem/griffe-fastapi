"""griffe-fastapi package.

Griffe extension for FastAPI.
"""

from pathlib import Path

from griffe_fastapi._extension import FastAPIExtension


def get_templates_path() -> Path:
    """Return the templates directory path."""
    return Path(__file__).parent / "templates"


__all__: list[str] = ["get_templates_path", "FastAPIExtension"]
