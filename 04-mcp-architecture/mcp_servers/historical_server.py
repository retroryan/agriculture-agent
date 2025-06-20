#!/usr/bin/env python3
"""
MCP server for OpenMeteo historical weather tool.
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
app = Server("openmeteo-historical")

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
            "name": "get_historical_weather",
            "description": "Get historical weather data for analysis",
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
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    }
                },
                "required": ["location", "start_date", "end_date"]
            }
        }
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute a tool."""
    global weather_client
    
    if name == "get_historical_weather":
        # Ensure client is initialized
        if weather_client is None:
            await initialize_client()
            
        location = arguments["location"]
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        
        try:
            # Get coordinates
            lat, lon = await weather_client.get_coordinates(location)
            
            # Get historical data
            historical_data = await weather_client.get_historical(
                latitude=lat,
                longitude=lon,
                start_date=start_date,
                end_date=end_date,
                daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
            )
            
            # Format response
            result = f"Historical weather for {location} ({start_date} to {end_date}):\n\n"
            
            if 'daily' in historical_data:
                daily = historical_data['daily']
                for i, date in enumerate(daily['time']):
                    max_temp = daily['temperature_2m_max'][i]
                    min_temp = daily['temperature_2m_min'][i]
                    precip = daily['precipitation_sum'][i]
                    wind = daily['wind_speed_10m_max'][i]
                    result += f"{date}: {min_temp:.0f}-{max_temp:.0f}°C, {precip}mm rain, {wind:.0f}km/h wind\n"
            
            return [{"type": "text", "text": result}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error getting historical data for {location}: {str(e)}"}]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server with proper lifecycle management."""
    # Initialize the client at startup
    await initialize_client()
    
    try:
        async with stdio_server() as streams:
            await app.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="openmeteo-historical",
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
    print("Starting OpenMeteo Historical MCP Server...", file=sys.stderr)
    print("Available at: stdio://python 04-mcp-architecture/mcp_servers/historical_server.py", file=sys.stderr)
    asyncio.run(main())