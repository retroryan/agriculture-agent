#!/usr/bin/env python3
"""
Unified MCP server for all weather and agricultural data - simplified demo version.
Based on strands-weather-agent best practices.
"""

import os
import logging
from typing import Optional, Union
from datetime import datetime, date, timedelta
from fastmcp import FastMCP

# Import shared utilities
from .api_utils import OpenMeteoClient
from .models import ForecastRequest, HistoricalRequest, AgriculturalRequest
from .parameters import WEATHER_DAILY_PARAMS, WEATHER_HOURLY_PARAMS, AGRICULTURAL_PARAMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = FastMCP(name="weather-mcp")
client = OpenMeteoClient()


async def get_coordinates(location: str) -> Optional[dict]:
    """Get coordinates for a location name using geocoding."""
    try:
        async with client:
            params = {"name": location, "count": 1, "language": "en"}
            response = await client._client.get(client.geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                result = data["results"][0]
                return {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "name": f"{result['name']}, {result.get('admin1', '')}, {result.get('country', '')}"
                }
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
    return None


@server.tool
async def get_weather_forecast(request: ForecastRequest) -> dict:
    """Get weather forecast with coordinate optimization.
    
    Performance tip: Providing latitude/longitude is 3x faster than location name.
    
    Args:
        request: ForecastRequest with location/coordinates and days
    
    Returns:
        Structured forecast data with location info, current conditions, and daily/hourly data
    """
    try:
        # Resolve location
        if request.latitude is not None and request.longitude is not None:
            coords = {
                "latitude": request.latitude, 
                "longitude": request.longitude, 
                "name": request.location or f"{request.latitude:.4f},{request.longitude:.4f}"
            }
        elif request.location:
            coords = await get_coordinates(request.location)
            if not coords:
                return {
                    "error": f"Could not find location: {request.location}. Please try a major city name."
                }
        else:
            return {
                "error": "Either location name or coordinates (latitude, longitude) required"
            }

        # Prepare API parameters
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "forecast_days": request.days,
            "daily": ",".join(WEATHER_DAILY_PARAMS),
            "hourly": ",".join(WEATHER_HOURLY_PARAMS),
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add location info
        data["location_info"] = {
            "name": coords.get("name", request.location),
            "coordinates": {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        }
        
        data["summary"] = f"Weather forecast for {coords.get('name', request.location)} ({request.days} days)"
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting forecast: {str(e)}"
        }


@server.tool
async def get_historical_weather(request: HistoricalRequest) -> dict:
    """Get historical weather data for analysis.
    
    Args:
        request: HistoricalRequest with location/coordinates and date range
    
    Returns:
        Historical weather data with daily aggregates
    """
    try:
        # Resolve location
        if request.latitude is not None and request.longitude is not None:
            coords = {
                "latitude": request.latitude, 
                "longitude": request.longitude, 
                "name": request.location or f"{request.latitude:.4f},{request.longitude:.4f}"
            }
        elif request.location:
            coords = await get_coordinates(request.location)
            if not coords:
                return {
                    "error": f"Could not find location: {request.location}. Please try a major city name."
                }
        else:
            return {
                "error": "Either location name or coordinates (latitude, longitude) required"
            }

        # Prepare API parameters
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "start_date": request.start_date,
            "end_date": request.end_date,
            "daily": ",".join(WEATHER_DAILY_PARAMS),
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.archive_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add location info
        data["location_info"] = {
            "name": coords.get("name", request.location),
            "coordinates": {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        }
        
        data["summary"] = f"Historical weather for {coords.get('name', request.location)} from {request.start_date} to {request.end_date}"
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting historical data: {str(e)}"
        }


@server.tool
async def get_agricultural_conditions(request: AgriculturalRequest) -> dict:
    """Get agricultural conditions including soil moisture and evapotranspiration.
    
    Args:
        request: AgriculturalRequest with location/coordinates and days
    
    Returns:
        Agricultural data with soil moisture at various depths
    """
    try:
        # Resolve location
        if request.latitude is not None and request.longitude is not None:
            coords = {
                "latitude": request.latitude, 
                "longitude": request.longitude, 
                "name": request.location or f"{request.latitude:.4f},{request.longitude:.4f}"
            }
        elif request.location:
            coords = await get_coordinates(request.location)
            if not coords:
                return {
                    "error": f"Could not find location: {request.location}. Please try a major city name."
                }
        else:
            return {
                "error": "Either location name or coordinates (latitude, longitude) required"
            }

        # Prepare API parameters
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "forecast_days": request.days,
            "hourly": ",".join(AGRICULTURAL_PARAMS),
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add location info
        data["location_info"] = {
            "name": coords.get("name", request.location),
            "coordinates": {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        }
        
        data["summary"] = f"Agricultural conditions for {coords.get('name', request.location)} ({request.days} days)"
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting agricultural data: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_SERVER_PORT", "7071"))
    uvicorn.run(server.app, host="127.0.0.1", port=port)