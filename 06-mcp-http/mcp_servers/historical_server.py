#!/usr/bin/env python3
"""
FastMCP server for OpenMeteo historical weather data (HTTP transport).
Exposes a single tool for historical weather, returns raw JSON for LLMs.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
from api_utils import get_coordinates, OpenMeteoClient, get_daily_params
import httpx
from datetime import datetime, date, timedelta

app = FastMCP("openmeteo-historical", stateless_http=True)

@app.tool()
async def get_historical_weather(location: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Get historical weather data from the Open-Meteo API.
    """
    client = OpenMeteoClient()
    try:
        # Parse dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD.", "status_code": 400}
        if end < start:
            return {"error": "End date must be after start date.", "status_code": 400}
        min_date = date.today() - timedelta(days=5)
        if end > min_date:
            return {"error": f"Historical data only available before {min_date}. Use forecast API for recent dates.", "status_code": 400}
        coords = await get_coordinates(location)
        if not coords:
            return {"error": f"Could not find location: {location}", "status_code": 404}
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": ",".join(get_daily_params()),
            "timezone": "auto"
        }
        data = await client.get("archive", params)
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
    app.run(transport="streamable-http")