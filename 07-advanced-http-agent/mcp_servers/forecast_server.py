#!/usr/bin/env python3
"""
FastMCP server for OpenMeteo weather forecast tool.
Returns raw JSON from the Open-Meteo API for LLM interpretation.
"""

import json
from typing import Optional
from fastmcp import FastMCP

# Import shared utilities
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params, get_hourly_params

# Initialize FastMCP server
server = FastMCP(name="openmeteo-forecast")
client = OpenMeteoClient()


@server.tool
async def get_weather_forecast(
    location: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    days: int = 7
) -> dict:
    """Get weather forecast data from Open-Meteo API as JSON.
    
    Args:
        location: Location name (e.g., 'Des Moines, Iowa')
        latitude: Latitude (optional, overrides location if provided)
        longitude: Longitude (optional, overrides location if provided)
        days: Number of forecast days (1-16)
    
    Returns:
        Weather forecast data as JSON
    """
    try:
        # Validate days parameter
        days = min(max(days, 1), 16)

        # Phase 2: Use coordinates if provided, else geocode
        if latitude is not None and longitude is not None:
            coords = {"latitude": latitude, "longitude": longitude, "name": location or f"{latitude},{longitude}"}
        else:
            coords = await get_coordinates(location)
            if not coords:
                return {
                    "error": f"Could not find location: {location}. Please try a major city name."
                }

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
        
        # Add summary
        data["summary"] = f"Weather forecast for {coords.get('name', location)} ({days} days)"
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting forecast: {str(e)}"
        }


if __name__ == "__main__":
    # Start the server with HTTP transport
    server.run(transport="streamable-http", host="127.0.0.1", port=7071, path="/mcp")