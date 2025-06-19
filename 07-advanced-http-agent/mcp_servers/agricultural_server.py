#!/usr/bin/env python3
"""
FastMCP server for agricultural weather conditions.
Returns raw JSON from the Open-Meteo API for LLM interpretation.
"""

from typing import Optional
from fastmcp import FastMCP

# Import shared utilities
from api_utils import get_coordinates, OpenMeteoClient

# Initialize FastMCP server
server = FastMCP(name="openmeteo-agricultural")
client = OpenMeteoClient()


@server.tool
async def get_agricultural_conditions(
    location: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    days: int = 7
) -> dict:
    """Get agricultural weather conditions including soil moisture and evapotranspiration as JSON.
    
    Args:
        location: Farm location (e.g., 'Ames, Iowa')
        latitude: Latitude (optional, overrides location if provided)
        longitude: Longitude (optional, overrides location if provided)
        days: Number of forecast days (1-7)
    
    Returns:
        Agricultural weather conditions data as JSON
    """
    try:
        # Validate days parameter
        days = min(max(days, 1), 7)

        # Phase 2: Use coordinates if provided, else geocode
        if latitude is not None and longitude is not None:
            coords = {"latitude": latitude, "longitude": longitude, "name": location or f"{latitude},{longitude}"}
        else:
            coords = await get_coordinates(location)
            if not coords:
                return {
                    "error": f"Could not find location: {location}. Please try a major city or farm name."
                }

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
        
        # Add summary
        data["summary"] = f"Agricultural conditions for {coords.get('name', location)} ({days} days) - Focus: Soil moisture, evapotranspiration, and growing conditions"
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting agricultural conditions: {str(e)}"
        }


if __name__ == "__main__":
    # Start the server with HTTP transport
    server.run(transport="streamable-http", host="127.0.0.1", port=7073, path="/mcp")