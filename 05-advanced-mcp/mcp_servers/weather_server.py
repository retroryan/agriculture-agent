#!/usr/bin/env python3
"""
Unified MCP server for Stage 5 - Advanced MCP with Structured Outputs.
Returns raw Open-Meteo JSON for agent-side structuring (LangGraph Option 1).
"""

import os
import logging
from typing import Optional, Union
from datetime import datetime, date, timedelta
from fastmcp import FastMCP

# Import shared utilities
from .api_utils import OpenMeteoClient
from .models import ForecastRequest, HistoricalRequest, AgriculturalRequest, get_daily_params, get_hourly_params, get_agricultural_params

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = FastMCP(name="weather-mcp-advanced")
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
    """Get weather forecast returning raw Open-Meteo JSON for structured processing.
    
    This tool returns the complete API response, allowing the agent to:
    - Process and structure the data as needed
    - Extract specific fields for structured output
    - Maintain full data fidelity
    
    Performance tip: Providing latitude/longitude is 3x faster than location name.
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

        # Prepare API parameters for comprehensive data
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "forecast_days": request.days,
            "daily": ",".join(get_daily_params()),
            "hourly": ",".join(get_hourly_params()),
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,pressure_msl",
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add metadata for structured processing
        data["_metadata"] = {
            "location_info": {
                "name": coords.get("name", request.location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            },
            "request_type": "forecast",
            "days_requested": request.days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting forecast: {str(e)}"
        }


@server.tool
async def get_historical_weather(request: HistoricalRequest) -> dict:
    """Get historical weather data returning raw Open-Meteo JSON.
    
    Returns complete historical data for agent-side analysis and structuring.
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
            "daily": ",".join(get_daily_params()),
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.archive_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add metadata for structured processing
        data["_metadata"] = {
            "location_info": {
                "name": coords.get("name", request.location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            },
            "request_type": "historical",
            "date_range": {
                "start": request.start_date,
                "end": request.end_date
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting historical data: {str(e)}"
        }


@server.tool
async def get_agricultural_conditions(request: AgriculturalRequest) -> dict:
    """Get agricultural conditions returning raw Open-Meteo JSON.
    
    Returns comprehensive agricultural data including soil moisture at various depths.
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
            "hourly": ",".join(get_agricultural_params()),
            "daily": "et0_fao_evapotranspiration",
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add metadata for structured processing
        data["_metadata"] = {
            "location_info": {
                "name": coords.get("name", request.location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            },
            "request_type": "agricultural",
            "days_requested": request.days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return data
        
    except Exception as e:
        return {
            "error": f"Error getting agricultural data: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_SERVER_PORT", "7072"))
    uvicorn.run(server.app, host="127.0.0.1", port=port)