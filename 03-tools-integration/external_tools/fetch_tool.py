"""
Fetch tool for LangGraph - retrieves and processes web content.
This is adapted from the MCP fetch server to work as a LangGraph tool.
"""

import httpx
from langchain_core.tools import tool
from typing import Optional, Dict
import logging
from markdownify import markdownify as md
from readabilipy import simple_json_from_html_string
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def fetch_webpage(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Fetch the contents of a URL and return as markdown-formatted text.
    
    This tool retrieves web content and converts it to clean markdown format,
    making it easier for LLMs to understand and process the content.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers to include in the request
        
    Returns:
        The content of the webpage converted to markdown, or an error message
    """
    logger.info(f"🔧 fetch_webpage called with URL: {url}")
    
    if headers is None:
        headers = {}
    
    # Add default User-Agent if not provided
    if "User-Agent" not in headers:
        headers["User-Agent"] = "LangGraph-Fetch-Tool/1.0"
    
    try:
        # Create HTTP client with timeout
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            logger.info(f"🚀 Sending GET request to: {url}")
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "").lower()
            logger.info(f"✅ Response received - Status: {response.status_code}, Content-Type: {content_type}")
            
            # Check if content is HTML
            if "text/html" in content_type:
                # Extract readable content using readabilipy
                try:
                    article = simple_json_from_html_string(response.text, use_readability=True)
                    
                    # Build markdown content
                    content_parts = []
                    
                    # Add title
                    if article.get('title'):
                        content_parts.append(f"# {article['title']}\n")
                    
                    # Add metadata
                    content_parts.append(f"**URL:** {url}\n")
                    
                    # Add main content
                    if article.get('plain_content'):
                        # Clean up the content
                        text = article['plain_content']
                        # Remove excessive whitespace
                        text = re.sub(r'\n\s*\n', '\n\n', text)
                        text = re.sub(r' +', ' ', text)
                        content_parts.append(text)
                    elif article.get('plain_text'):
                        # Fallback to plain_text if plain_content is not available
                        text = article['plain_text']
                        text = re.sub(r'\n\s*\n', '\n\n', text)
                        text = re.sub(r' +', ' ', text)
                        content_parts.append(text)
                    else:
                        # Final fallback - convert HTML to markdown
                        content_parts.append(md(response.text, heading_style="ATX"))
                    
                    result = '\n'.join(content_parts)
                    logger.info(f"📄 Converted HTML to markdown - length: {len(result)} chars")
                    return result
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract with readabilipy: {e}, falling back to markdownify")
                    # Fallback to simple markdown conversion
                    result = md(response.text, heading_style="ATX")
                    return f"# Content from {url}\n\n{result}"
            else:
                # For non-HTML content, return as-is
                logger.info(f"📄 Returning raw text content - length: {len(response.text)} chars")
                return f"# Content from {url}\n\n{response.text}"
    
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP error {e.response.status_code}: {e}")
        return f"Error: HTTP {e.response.status_code} when fetching {url}"
    except Exception as e:
        logger.error(f"❌ Error fetching URL: {type(e).__name__}: {e}")
        return f"Error fetching {url}: {str(e)}"


@tool 
def fetch_raw_content(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Fetch the raw contents of a URL without any processing.
    
    Use this when you need the exact content of a file or API response
    without HTML parsing or markdown conversion.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers to include in the request
        
    Returns:
        The raw text content of the URL or an error message
    """
    logger.info(f"🔧 fetch_raw_content called with URL: {url}")
    
    if headers is None:
        headers = {}
    
    # Add default User-Agent if not provided
    if "User-Agent" not in headers:
        headers["User-Agent"] = "LangGraph-Fetch-Tool/1.0"
    
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            logger.info(f"🚀 Sending GET request to: {url}")
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Response received - Status: {response.status_code}")
            logger.info(f"📄 Returning raw content - length: {len(response.text)} chars")
            
            return response.text
    
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP error {e.response.status_code}: {e}")
        return f"Error: HTTP {e.response.status_code} when fetching {url}"
    except Exception as e:
        logger.error(f"❌ Error fetching URL: {type(e).__name__}: {e}")
        return f"Error fetching {url}: {str(e)}"


# List of fetch tools for easy import
FETCH_TOOLS = [fetch_webpage, fetch_raw_content]