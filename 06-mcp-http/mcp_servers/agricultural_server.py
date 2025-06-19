#!/usr/bin/env python3
"""
FastMCP server for agricultural weather conditions (HTTP transport).
Exposes a single tool for agricultural conditions, returns raw JSON for LLMs.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
from api_utils import get_coordinates, OpenMeteoClient
import httpx
import sys

# Parse port from command line
port = 8002  # default
for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        port = int(sys.argv[i + 1])
        break

# Create the FastMCP application with custom port
app = FastMCP("openmeteo-agricultural", stateless_http=True)
app.settings.port = port

@app.tool()
async def get_agricultural_conditions(
    location: str, 
    days: int = 7,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Dict[str, Any]:
    """
    Get agricultural weather conditions including soil moisture and evapotranspiration as JSON.
    
    Args:
        location: Location name (e.g., 'Des Moines, Iowa')
        days: Number of forecast days (1-7)
        latitude: Latitude (optional, overrides location if provided)
        longitude: Longitude (optional, overrides location if provided)
    """
    client = OpenMeteoClient()
    try:
        days = min(max(days, 1), 7)
        
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
                return {"error": f"Could not find location: {location}", "status_code": 404}
                
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
        data["location_info"] = {
            "name": coords.get("name", location),
            "coordinates": {"latitude": coords["latitude"], "longitude": coords["longitude"]}
        }
        return data
    except httpx.HTTPStatusError as e:
        return {"error": f"Error from upstream API: {e.response.text}", "status_code": e.response.status_code}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}", "status_code": 500}

if __name__ == "__main__":
    print(f"Starting agricultural server on port {port}")
    app.run(transport="streamable-http")