#!/usr/bin/env python3
"""Test the API client directly."""

import asyncio
import sys
sys.path.append('04-mcp-architecture/mcp_servers')

from api_utils import OpenMeteoClient

async def test_api_client():
    """Test the OpenMeteo client directly."""
    print("Testing OpenMeteo API client...")
    
    async with OpenMeteoClient() as client:
        try:
            # Test coordinates
            print("Getting coordinates for Ames, Iowa...")
            lat, lon = await client.get_coordinates("Ames, Iowa")
            print(f"Coordinates: {lat}, {lon}")
            
            # Test forecast
            print("Getting forecast...")
            forecast = await client.get_forecast(
                latitude=lat,
                longitude=lon,
                hourly=["temperature_2m", "relative_humidity_2m"],
                daily=["temperature_2m_max", "temperature_2m_min"],
                forecast_days=3
            )
            print(f"Forecast keys: {list(forecast.keys())}")
            if 'daily' in forecast:
                print(f"Daily data: {forecast['daily']['time'][:3]}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_client())