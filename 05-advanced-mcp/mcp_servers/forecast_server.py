#!/usr/bin/env python3
"""
MCP server for OpenMeteo weather forecast tool.
Returns raw JSON from the Open-Meteo API for LLM interpretation.
"""

import sys
import json
import asyncio
from typing import Dict, Any, List
import httpx
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Import shared utilities
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params, get_hourly_params


async def main():
    """Run the weather forecast MCP server."""
    app = Server("openmeteo-forecast")
    client = OpenMeteoClient()
    
    @app.list_tools()
    async def list_tools() -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast data from Open-Meteo API as JSON",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location name (e.g., 'Des Moines, Iowa')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days (1-16)",
                            "default": 7,
                            "minimum": 1,
                            "maximum": 16
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[Dict[str, Any]]:
        if name != "get_weather_forecast":
            return [{"type": "text", "text": f"Unknown tool: {name}"}]
        
        try:
            location = arguments.get("location", "")
            days = min(max(arguments.get("days", 7), 1), 16)
            
            # Get coordinates
            coords = await get_coordinates(location)
            if not coords:
                return [{
                    "type": "text",
                    "text": f"Could not find location: {location}. Please try a major city name."
                }]
            
            # Get forecast data
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "forecast_days": days,
                "daily": ",".join(get_daily_params()),
                "hourly": ",".join(get_hourly_params()),
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            
            data = await client.get("forecast", params)
            
            # Add location info
            data["location_info"] = {
                "name": coords.get("name", location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            }
            
            # Create summary
            summary = f"Weather forecast for {coords.get('name', location)} ({days} days):\n"
            summary += f"Timezone: {data.get('timezone', 'Unknown')}\n\n"
            
            # Return raw JSON
            return [{
                "type": "text",
                "text": summary + json.dumps(data, indent=2)
            }]
            
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error getting forecast: {str(e)}"
            }]
    
    # Run the server
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="openmeteo-forecast",
                server_version="1.0.0",
                capabilities={"tools": {}}
            )
        )


if __name__ == "__main__":
    print("Starting OpenMeteo Forecast MCP Server...", file=sys.stderr)
    asyncio.run(main())