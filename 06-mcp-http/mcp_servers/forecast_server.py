#!/usr/bin/env python3
"""
FastMCP server for OpenMeteo weather forecast tool (HTTP transport).
Exposes a single tool for weather forecast, returns raw JSON for LLMs.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params, get_hourly_params
import httpx

# Create the FastMCP application
app = FastMCP("openmeteo-forecast", stateless_http=True)

@app.tool()
async def get_weather_forecast(location: str, days: int = 7) -> Dict[str, Any]:
    """
    Get weather forecast data from the Open-Meteo API.
    """
    client = OpenMeteoClient()
    try:
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
    app.run(transport="streamable-http")