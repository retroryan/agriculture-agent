#!/usr/bin/env python3
"""
FastMCP server for OpenMeteo weather forecast tool (HTTP transport).
Exposes a single tool for weather forecast, returns raw JSON for LLMs.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params, get_hourly_params
import httpx
import sys
import os

# Parse port from command line
port = 8000  # default
for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        port = int(sys.argv[i + 1])
        break

# Create the FastMCP application with custom port
app = FastMCP("openmeteo-forecast", stateless_http=True)
app.settings.port = port

@app.tool()
async def get_weather_forecast(
    location: str, 
    days: int = 7,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Dict[str, Any]:
    """
    Get weather forecast data from the Open-Meteo API.
    
    Args:
        location: Location name (e.g., 'Des Moines, Iowa')
        days: Number of forecast days (1-16)
        latitude: Latitude (optional, overrides location if provided)
        longitude: Longitude (optional, overrides location if provided)
    """
    client = OpenMeteoClient()
    try:
        # Use coordinates if provided, else geocode
        if latitude is not None and longitude is not None:
            coords = {
                "latitude": latitude, 
                "longitude": longitude, 
                "name": location or f"{latitude},{longitude}"
            }
        else:
            coords = await get_coordinates(location)
            if not coords:
                return {
                    "error": f"Could not find location: {location}",
                    "status_code": 404
                }
        
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "forecast_days": max(1, min(days, 16)),
            "daily": ",".join(get_daily_params()),
            "hourly": ",".join(get_hourly_params()),
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        data = await client.get("forecast", params)
        data["location_info"] = {
            "name": coords.get("name", location),
            "coordinates": {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        }
        return data
    except httpx.HTTPStatusError as e:
        return {
            "error": f"Error from upstream API: {e.response.text}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "status_code": 500
        }

if __name__ == "__main__":
    print(f"Starting forecast server on port {port}")
    app.run(transport="streamable-http")