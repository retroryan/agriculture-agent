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

# Server-owned client instance
weather_client: OpenMeteoClient = None


async def initialize_client():
    """Initialize the weather client at server startup."""
    global weather_client
    weather_client = OpenMeteoClient()
    # Ensure the client is ready
    await weather_client.ensure_client()
    return weather_client


async def cleanup_client():
    """Cleanup the weather client at server shutdown."""
    global weather_client
    if weather_client:
        await weather_client.close()
        weather_client = None


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
    global weather_client
    
    if name == "get_weather_forecast":
        # Ensure client is initialized
        if weather_client is None:
            await initialize_client()
            
        location = arguments["location"]
        days = arguments.get("days", 7)
        
        try:
            # Get coordinates
            lat, lon = await weather_client.get_coordinates(location)
            
            # Get forecast data
            forecast_data = await weather_client.get_forecast(
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
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server with proper lifecycle management."""
    try:
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
    finally:
        # Cleanup on shutdown
        await cleanup_client()


if __name__ == "__main__":
    import sys
    print("Starting OpenMeteo Forecast MCP Server...", file=sys.stderr)
    print("Available at: stdio://python 05-advanced-mcp/mcp_servers/forecast_server.py", file=sys.stderr)
    asyncio.run(main())