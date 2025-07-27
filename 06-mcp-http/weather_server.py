#!/usr/bin/env python3
"""
Unified Weather MCP Server for Stage 6 - HTTP Transport Demo.
Shows FastMCP with HTTP transport instead of stdio.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from mcp import Server
import httpx
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server with HTTP transport
server = Server("weather-http-server")


# Pydantic models for request validation
class LocationInput(BaseModel):
    """Location input with coordinate support."""
    location: Optional[str] = Field(None, description="Location name")
    latitude: Optional[float] = Field(None, description="Latitude (-90 to 90)")
    longitude: Optional[float] = Field(None, description="Longitude (-180 to 180)")


class ForecastRequest(LocationInput):
    """Weather forecast request."""
    days: int = Field(default=7, ge=1, le=16, description="Forecast days (1-16)")


class HistoricalRequest(LocationInput):
    """Historical weather request."""
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')


class AgriculturalRequest(LocationInput):
    """Agricultural conditions request."""
    days: int = Field(default=7, ge=1, le=7, description="Forecast days (1-7)")


# Simplified API client
class WeatherAPIClient:
    """Simple async client for Open-Meteo API."""
    
    def __init__(self):
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.archive_url = "https://archive-api.open-meteo.com/v1/archive"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    
    async def get_coordinates(self, location: str) -> Optional[Dict[str, Any]]:
        """Get coordinates for location."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.geocoding_url,
                params={"name": location, "count": 1}
            )
            data = response.json()
            if data.get("results"):
                result = data["results"][0]
                return {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "name": f"{result['name']}, {result.get('country', '')}"
                }
        return None
    
    async def get_forecast(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        """Get weather forecast."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "timezone": "auto"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.forecast_url, params=params)
            return response.json()
    
    async def get_historical(self, lat: float, lon: float, start: str, end: str) -> Dict[str, Any]:
        """Get historical weather."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.archive_url, params=params)
            return response.json()
    
    async def get_agricultural(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        """Get agricultural conditions."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "hourly": "soil_moisture_0_to_1cm,soil_temperature_0cm,et0_fao_evapotranspiration",
            "daily": "et0_fao_evapotranspiration",
            "timezone": "auto"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.forecast_url, params=params)
            return response.json()


# Initialize API client
api_client = WeatherAPIClient()


@server.tool
async def get_weather_forecast(request: ForecastRequest) -> dict:
    """Get weather forecast data.
    
    HTTP transport demo: This tool is exposed via HTTP instead of stdio.
    """
    try:
        # Resolve coordinates
        if request.latitude and request.longitude:
            lat, lon = request.latitude, request.longitude
            location_name = request.location or f"{lat:.2f},{lon:.2f}"
        elif request.location:
            coords = await api_client.get_coordinates(request.location)
            if not coords:
                return {"error": f"Location not found: {request.location}"}
            lat, lon = coords["latitude"], coords["longitude"]
            location_name = coords["name"]
        else:
            return {"error": "Location or coordinates required"}
        
        # Get forecast
        data = await api_client.get_forecast(lat, lon, request.days)
        
        # Add metadata
        data["location_name"] = location_name
        data["request_type"] = "forecast"
        data["transport"] = "HTTP"
        
        return data
        
    except Exception as e:
        return {"error": f"Forecast error: {str(e)}"}


@server.tool
async def get_historical_weather(request: HistoricalRequest) -> dict:
    """Get historical weather data via HTTP transport."""
    try:
        # Resolve coordinates
        if request.latitude and request.longitude:
            lat, lon = request.latitude, request.longitude
            location_name = request.location or f"{lat:.2f},{lon:.2f}"
        elif request.location:
            coords = await api_client.get_coordinates(request.location)
            if not coords:
                return {"error": f"Location not found: {request.location}"}
            lat, lon = coords["latitude"], coords["longitude"]
            location_name = coords["name"]
        else:
            return {"error": "Location or coordinates required"}
        
        # Get historical data
        data = await api_client.get_historical(lat, lon, request.start_date, request.end_date)
        
        # Add metadata
        data["location_name"] = location_name
        data["request_type"] = "historical"
        data["transport"] = "HTTP"
        
        return data
        
    except Exception as e:
        return {"error": f"Historical error: {str(e)}"}


@server.tool
async def get_agricultural_conditions(request: AgriculturalRequest) -> dict:
    """Get agricultural conditions via HTTP transport."""
    try:
        # Resolve coordinates
        if request.latitude and request.longitude:
            lat, lon = request.latitude, request.longitude
            location_name = request.location or f"{lat:.2f},{lon:.2f}"
        elif request.location:
            coords = await api_client.get_coordinates(request.location)
            if not coords:
                return {"error": f"Location not found: {request.location}"}
            lat, lon = coords["latitude"], coords["longitude"]
            location_name = coords["name"]
        else:
            return {"error": "Location or coordinates required"}
        
        # Get agricultural data
        data = await api_client.get_agricultural(lat, lon, request.days)
        
        # Add metadata
        data["location_name"] = location_name
        data["request_type"] = "agricultural"
        data["transport"] = "HTTP"
        
        return data
        
    except Exception as e:
        return {"error": f"Agricultural error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    from mcp.asgi import create_asgi_app
    
    # Create ASGI app for HTTP transport
    app = create_asgi_app(server)
    
    # Run with uvicorn
    port = int(os.getenv("MCP_SERVER_PORT", "7073"))
    uvicorn.run(app, host="127.0.0.1", port=port)