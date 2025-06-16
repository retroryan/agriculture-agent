#!/usr/bin/env python3
"""
MCP server for agricultural weather conditions.
Returns raw JSON from the Open-Meteo API for LLM interpretation.
"""

import sys
import json
import asyncio
from typing import Dict, Any, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Import shared utilities
from api_utils import get_coordinates, OpenMeteoClient


async def main():
    """Run the agricultural weather MCP server."""
    app = Server("openmeteo-agricultural")
    client = OpenMeteoClient()
    
    @app.list_tools()
    async def list_tools() -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_agricultural_conditions",
                "description": "Get agricultural weather conditions including soil moisture and evapotranspiration as JSON",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Farm location (e.g., 'Ames, Iowa')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days (1-7)",
                            "default": 7,
                            "minimum": 1,
                            "maximum": 7
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[Dict[str, Any]]:
        if name != "get_agricultural_conditions":
            return [{"type": "text", "text": f"Unknown tool: {name}"}]
        
        try:
            location = arguments.get("location", "")
            days = min(max(arguments.get("days", 7), 1), 7)
            
            # Get coordinates
            coords = await get_coordinates(location)
            if not coords:
                return [{
                    "type": "text",
                    "text": f"Could not find location: {location}. Please try a major city or farm name."
                }]
            
            # Get agricultural data with soil and ET parameters
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "forecast_days": days,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration,vapor_pressure_deficit_max",
                "hourly": "temperature_2m,relative_humidity_2m,precipitation,soil_temperature_0cm,soil_temperature_6cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm",
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
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
            
            # Create agricultural summary
            summary = f"Agricultural conditions for {coords.get('name', location)} ({days} days):\n"
            summary += f"Timezone: {data.get('timezone', 'Unknown')}\n"
            summary += "Focus: Soil moisture, evapotranspiration, and growing conditions\n\n"
            
            # Return raw JSON
            return [{
                "type": "text",
                "text": summary + json.dumps(data, indent=2)
            }]
            
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error getting agricultural conditions: {str(e)}"
            }]
    
    # Run the server
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="openmeteo-agricultural",
                server_version="1.0.0",
                capabilities={"tools": {}}
            )
        )


if __name__ == "__main__":
    print("Starting OpenMeteo Agricultural MCP Server...", file=sys.stderr)
    asyncio.run(main())