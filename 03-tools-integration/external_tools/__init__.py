"""
External tools module - tools for web and API interactions.

Available tools:
- fetch_webpage: Fetches and converts web content to markdown
- fetch_raw_content: Fetches raw content without processing
"""

from .fetch_tool import (
    fetch_webpage,
    fetch_raw_content,
    FETCH_TOOLS
)

__all__ = [
    "fetch_webpage",
    "fetch_raw_content",
    "FETCH_TOOLS"
]