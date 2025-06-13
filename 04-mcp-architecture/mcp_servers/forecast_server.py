#!/usr/bin/env python3
"""
MCP server for OpenMeteo weather forecast tool.
"""

import sys
import os
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Add the mcp_servers directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use simplified API utils instead of tools
from api_utils import OpenMeteoClient


# Create server instance
app = Server("openmeteo-forecast")


@app.list_tools()
async def list_tools():
    """List available tools."""
    return [
        {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for agricultural planning",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "enum": [
                            "Grand Island, Nebraska",
                            "Scottsbluff, Nebraska",
                            "Ames, Iowa",
                            "Cedar Rapids, Iowa",
                            "Fresno, California",
                            "Salinas, California",
                            "Lubbock, Texas",
                            "Amarillo, Texas"
                        ],
                        "description": "Agricultural location to check"
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
async def call_tool(name: str, arguments: dict):
    """Execute a tool."""
    if name == "get_weather_forecast":
        # Use unified API client directly
        client = OpenMeteoClient()
        location = arguments["location"]
        days = arguments.get("days", 7)
        
        try:
            # Get coordinates (using async version)
            lat, lon = await client.get_coordinates_async(location)
            
            # Get forecast data (using async version)
            forecast_data = await client.get_forecast_async(
                latitude=lat,
                longitude=lon,
                hourly=["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
                daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                forecast_days=days
            )
            
            # Format response
            result = f"Weather forecast for {location} ({days} days):\n\n"
            
            if 'daily' in forecast_data:
                daily = forecast_data['daily']
                for i in range(min(days, len(daily['time']))):
                    date = daily['time'][i]
                    max_temp = daily['temperature_2m_max'][i]
                    min_temp = daily['temperature_2m_min'][i]
                    precip = daily['precipitation_sum'][i]
                    result += f"Day {i+1} ({date}): {min_temp:.0f}-{max_temp:.0f}°C, {precip}mm rain\n"
            
            return [{"type": "text", "text": result}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error getting forecast for {location}: {str(e)}"}]
        finally:
            # Clean up async client
            await client.close()
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="openmeteo-forecast",
                server_version="1.0.0",
                capabilities={
                    "tools": {}
                }
            )
        )


if __name__ == "__main__":
    import sys
    print("Starting OpenMeteo Forecast MCP Server...", file=sys.stderr)
    print("Available at: stdio://python 04-mcp-architecture/mcp_servers/forecast_server.py", file=sys.stderr)
    asyncio.run(main())