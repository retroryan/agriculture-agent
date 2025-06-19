#!/usr/bin/env python3
"""
FastMCP server for OpenMeteo historical weather data.
Returns raw JSON from the Open-Meteo API for LLM interpretation.
"""

from typing import Optional
from datetime import datetime, date, timedelta
from fastmcp import FastMCP

# Import shared utilities
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params, get_hourly_params

# Initialize FastMCP server
server = FastMCP(name="openmeteo-historical")
client = OpenMeteoClient()


@server.tool
async def get_historical_weather(
    start_date: str,
    end_date: str,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> dict:
    """Get historical weather data from Open-Meteo API as JSON.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        location: Location name (e.g., 'Des Moines, Iowa')
        latitude: Latitude (optional, overrides location if provided)
        longitude: Longitude (optional, overrides location if provided)
    
    Returns:
        Historical weather data as JSON
    """
    try:
        # Parse dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "error": "Invalid date format. Use YYYY-MM-DD."
            }
        
        if end < start:
            return {
                "error": "End date must be after start date."
            }
        
        min_date = date.today() - timedelta(days=5)
        if end > min_date:
            return {
                "error": f"Historical data only available before {min_date}. Use forecast API for recent dates."
            }

        # Phase 2: Use coordinates if provided, else geocode
        if latitude is not None and longitude is not None:
            coords = {"latitude": latitude, "longitude": longitude, "name": location or f"{latitude},{longitude}"}
        else:
            if not location:
                return {
                    "error": "Either location or latitude/longitude must be provided."
                }
            coords = await get_coordinates(location)
            if not coords:
                return {
                    "error": f"Could not find location: {location}. Please try a major city name."
                }

        # Get historical data
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": ",".join(get_daily_params()),
            "timezone": "auto"
        }
        
        data = await client.get("archive", params)
        
        # Add location info
        data["location_info"] = {
            "name": coords.get("name", location or f"{latitude},{longitude}"),
            "coordinates": {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        }
        
        # Add summary
        data["summary"] = f"Historical weather for {coords.get('name', location)} from {start_date} to {end_date}"
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting historical data: {str(e)}"
        }


if __name__ == "__main__":
    # Start the server with HTTP transport
    server.run(transport="streamable-http", host="127.0.0.1", port=7072, path="/mcp")