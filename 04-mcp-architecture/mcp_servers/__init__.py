"""
MCP Servers for OpenMeteo Weather Data

This package provides Model Context Protocol (MCP) servers for accessing
OpenMeteo weather data with specialized functionality for different domains:

- weather_server: Unified server handling all weather operations (forecast, historical, and agricultural data)

Each server operates independently and can be used with MCP-compatible clients.
"""

from .api_utils import OpenMeteoClient

__all__ = ["OpenMeteoClient"]