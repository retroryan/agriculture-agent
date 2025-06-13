#!/usr/bin/env python3
"""
MCP server for OpenMeteo agricultural conditions tool.
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
app = Server("openmeteo-agricultural")

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
            "name": "get_agricultural_conditions",
            "description": "Get specialized agricultural parameters for farming decisions",
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
                    "include_soil": {
                        "type": "boolean",
                        "description": "Include soil moisture and temperature data",
                        "default": True
                    },
                    "include_solar": {
                        "type": "boolean",
                        "description": "Include solar radiation and UV data",
                        "default": True
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
    
    if name == "get_agricultural_conditions":
        # Ensure client is initialized
        if weather_client is None:
            await initialize_client()
            
        location = arguments["location"]
        include_soil = arguments.get("include_soil", True)
        include_solar = arguments.get("include_solar", True)
        
        try:
            # Get coordinates
            lat, lon = await weather_client.get_coordinates(location)
            
            # Build parameter list based on options
            hourly_params = ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"]
            
            if include_soil:
                hourly_params.extend(["soil_temperature_0cm", "soil_moisture_0_to_1cm"])
            
            if include_solar:
                hourly_params.extend(["shortwave_radiation", "et0_fao_evapotranspiration"])
            
            # Get agricultural forecast data
            forecast_data = await weather_client.get_forecast(
                latitude=lat,
                longitude=lon,
                hourly=hourly_params,
                daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "et0_fao_evapotranspiration"],
                forecast_days=7
            )
            
            # Format response
            result = f"Agricultural conditions for {location}:\n\n"
            
            if 'daily' in forecast_data:
                daily = forecast_data['daily']
                for i in range(min(7, len(daily['time']))):
                    date = daily['time'][i]
                    max_temp = daily['temperature_2m_max'][i]
                    min_temp = daily['temperature_2m_min'][i]
                    precip = daily['precipitation_sum'][i]
                    et0 = daily['et0_fao_evapotranspiration'][i]
                    result += f"Day {i+1} ({date}): {min_temp:.0f}-{max_temp:.0f}°C, {precip}mm rain, {et0:.1f}mm ET0\n"
            
            # Add current soil conditions if requested
            if include_soil and 'hourly' in forecast_data:
                hourly = forecast_data['hourly']
                if 'soil_temperature_0cm' in hourly:
                    soil_temp = hourly['soil_temperature_0cm'][0]
                    soil_moisture = hourly['soil_moisture_0_to_1cm'][0] if 'soil_moisture_0_to_1cm' in hourly else 'N/A'
                    result += f"\nCurrent soil: {soil_temp:.1f}°C, {soil_moisture}% moisture"
            
            return [{"type": "text", "text": result}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error getting agricultural conditions for {location}: {str(e)}"}]
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
                    server_name="openmeteo-agricultural",
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
    print("Starting OpenMeteo Agricultural MCP Server...", file=sys.stderr)
    print("Available at: stdio://python 04-mcp-architecture/mcp_servers/agricultural_server.py", file=sys.stderr)
    asyncio.run(main())