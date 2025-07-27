#!/usr/bin/env python3
"""
Simplified FastMCP server for weather forecast - Educational Demo.

This server demonstrates the basics of FastMCP HTTP integration:
- Simple tool definition with clear docstrings
- Minimal error handling for clarity
- Direct API integration without abstractions
"""

import httpx
from fastmcp import FastMCP

# Initialize server with descriptive name
server = FastMCP(name="weather-forecast")

# Simple helper to get coordinates
async def geocode(location: str) -> dict:
    """Convert location name to coordinates."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location.split(',')[0], "count": 1}
        )
        data = response.json()
        if results := data.get("results"):
            return {
                "latitude": results[0]["latitude"],
                "longitude": results[0]["longitude"],
                "name": results[0]["name"]
            }
    raise ValueError(f"Location '{location}' not found")


@server.tool
async def get_forecast(location: str, days: int = 7) -> dict:
    """
    Get weather forecast for a location.
    
    Args:
        location: City name (e.g., 'San Francisco' or 'Paris, France')
        days: Number of forecast days (1-16, default 7)
    
    Returns:
        Weather forecast data including temperature, precipitation, and wind
    """
    # Get coordinates
    try:
        coords = await geocode(location)
    except ValueError as e:
        return {"error": str(e)}
    
    # Fetch forecast from Open-Meteo
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "forecast_days": min(max(days, 1), 16),
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                "current": "temperature_2m,precipitation,wind_speed_10m",
                "timezone": "auto"
            }
        )
        
        data = response.json()
        
        # Add location info for context
        data["location"] = coords["name"]
        data["query"] = {"location": location, "days": days}
        
        return data


@server.tool  
async def get_current_weather(location: str) -> dict:
    """
    Get current weather conditions.
    
    Args:
        location: City name (e.g., 'New York' or 'Tokyo, Japan')
        
    Returns:
        Current temperature, precipitation, and wind conditions
    """
    # Get coordinates
    try:
        coords = await geocode(location)
    except ValueError as e:
        return {"error": str(e)}
    
    # Fetch current conditions
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "current": "temperature_2m,apparent_temperature,precipitation,rain,wind_speed_10m,wind_direction_10m"
            }
        )
        
        data = response.json()
        
        return {
            "location": coords["name"],
            "current": data.get("current", {}),
            "units": data.get("current_units", {})
        }


if __name__ == "__main__":
    # Start HTTP server - ready for remote deployment!
    import os
    host = os.getenv("HOST", "127.0.0.1")  # Use 0.0.0.0 for Docker
    port = int(os.getenv("PORT", "7071"))
    
    print(f"🌤️  Starting Weather Forecast Server on http://{host}:{port}/mcp")
    server.run(
        transport="streamable-http",
        host=host, 
        port=port,
        path="/mcp"
    )