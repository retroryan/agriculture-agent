#!/usr/bin/env python3
"""
MCP server for OpenMeteo historical weather data.
Returns raw JSON from the Open-Meteo API for LLM interpretation.
"""

import sys
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime, date, timedelta

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Import shared utilities
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params, get_hourly_params


async def main():
    """Run the historical weather MCP server."""
    app = Server("openmeteo-historical")
    client = OpenMeteoClient()
    
    @app.list_tools()
    async def list_tools() -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_historical_weather",
                "description": "Get historical weather data from Open-Meteo API as JSON",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location name (e.g., 'Des Moines, Iowa')"
                        },
                        "latitude": {
                            "type": "number",
                            "description": "Latitude (optional, overrides location if provided)"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude (optional, overrides location if provided)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date (YYYY-MM-DD)"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            }
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[Dict[str, Any]]:
        if name != "get_historical_weather":
            return [{"type": "text", "text": f"Unknown tool: {name}"}]
        
        try:
            location = arguments.get("location", "")
            lat = arguments.get("latitude")
            lon = arguments.get("longitude")
            start_date = arguments.get("start_date", "")
            end_date = arguments.get("end_date", "")

            # Parse dates
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return [{
                    "type": "text",
                    "text": "Invalid date format. Use YYYY-MM-DD."
                }]
            if end < start:
                return [{
                    "type": "text",
                    "text": "End date must be after start date."
                }]
            min_date = date.today() - timedelta(days=5)
            if end > min_date:
                return [{
                    "type": "text",
                    "text": f"Historical data only available before {min_date}. Use forecast API for recent dates."
                }]

            # Phase 2: Use coordinates if provided, else geocode
            if lat is not None and lon is not None:
                coords = {"latitude": lat, "longitude": lon, "name": location or f"{lat},{lon}"}
            else:
                coords = await get_coordinates(location)
                if not coords:
                    return [{
                        "type": "text",
                        "text": f"Could not find location: {location}. Please try a major city name."
                    }]

            # Get historical data
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": ",".join(get_daily_params()),
                "timezone": "auto"
            }
            data = await client.get("archive", params)
            data["location_info"] = {
                "name": coords.get("name", location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            }
            summary = f"Historical weather for {coords.get('name', location)}\n"
            summary += f"Period: {start_date} to {end_date}\n"
            summary += f"Timezone: {data.get('timezone', 'Unknown')}\n\n"
            return [{
                "type": "text",
                "text": summary + json.dumps(data, indent=2)
            }]
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error getting historical data: {str(e)}"
            }]
    
    # Run the server
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="openmeteo-historical",
                server_version="1.0.0",
                capabilities={"tools": {}}
            )
        )


if __name__ == "__main__":
    print("Starting OpenMeteo Historical MCP Server...", file=sys.stderr)
    asyncio.run(main())