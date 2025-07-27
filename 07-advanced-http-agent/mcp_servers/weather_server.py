#!/usr/bin/env python3
"""
Unified Weather MCP Server for Stage 7 - Advanced HTTP Agent.
Demonstrates distributed deployment capabilities with HTTP transport.
"""

import os
import logging
from typing import Optional, Union, Dict, Any, List
from datetime import datetime, date, timedelta
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, model_validator

# Import shared utilities
from .api_utils import OpenMeteoClient
from .utils.display import display_weather_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server for HTTP transport
server = FastMCP(name="weather-http-advanced")
client = OpenMeteoClient()


# Pydantic models for request validation
class LocationInput(BaseModel):
    """Advanced location input with coordinate optimization."""
    location: Optional[str] = Field(
        None, 
        description="Location name (e.g., 'Chicago, IL'). Slower due to geocoding."
    )
    latitude: Optional[float] = Field(
        None, 
        description="Direct latitude (-90 to 90). PREFERRED for 3x faster response."
    )
    longitude: Optional[float] = Field(
        None, 
        description="Direct longitude (-180 to 180). PREFERRED for 3x faster response."
    )
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        """Validate latitude range."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError(f'Latitude must be between -90 and 90, got {v}')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude range."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError(f'Longitude must be between -180 and 180, got {v}')
        return v
    
    @model_validator(mode='after')
    def check_location_provided(self):
        """Ensure at least one location method is provided."""
        has_location = self.location is not None
        has_coords = self.latitude is not None and self.longitude is not None
        if not has_location and not has_coords:
            raise ValueError('Either location name or coordinates (latitude, longitude) required')
        return self


class ForecastRequest(LocationInput):
    """Weather forecast request with structured output support."""
    days: int = Field(
        default=7,
        ge=1,
        le=16,
        description="Number of forecast days (1-16)"
    )
    structured_output: bool = Field(
        default=False,
        description="Return structured Pydantic models instead of raw JSON"
    )


class HistoricalRequest(LocationInput):
    """Historical weather request with date validation."""
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r'^\d{4}-\d{2}-\d{2}$'
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r'^\d{4}-\d{2}-\d{2}$'
    )
    structured_output: bool = Field(
        default=False,
        description="Return structured Pydantic models instead of raw JSON"
    )
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {v}. Use YYYY-MM-DD.")
        return v
    
    @model_validator(mode='after')
    def validate_date_order(self):
        """Ensure end date is after start date."""
        if self.start_date and self.end_date:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            if end < start:
                raise ValueError("End date must be after start date.")
        return self


class AgriculturalRequest(LocationInput):
    """Agricultural conditions request with soil analysis."""
    days: int = Field(
        default=7,
        ge=1,
        le=7,
        description="Number of forecast days (1-7)"
    )
    structured_output: bool = Field(
        default=False,
        description="Return structured Pydantic models instead of raw JSON"
    )


# Helper functions
async def get_coordinates(location: str) -> Optional[dict]:
    """Get coordinates with caching for performance."""
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


def get_comprehensive_params() -> Dict[str, List[str]]:
    """Get comprehensive weather parameters for detailed analysis."""
    return {
        "daily": [
            "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max",
            "apparent_temperature_min", "precipitation_sum", "rain_sum", "showers_sum",
            "snowfall_sum", "precipitation_hours", "weather_code", "sunrise", "sunset",
            "wind_speed_10m_max", "wind_gusts_10m_max", "uv_index_max",
            "et0_fao_evapotranspiration"
        ],
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
            "precipitation", "rain", "showers", "snowfall", "weather_code", "pressure_msl",
            "surface_pressure", "cloud_cover", "visibility", "wind_speed_10m", "wind_direction_10m"
        ],
        "agricultural": [
            "et0_fao_evapotranspiration", "vapour_pressure_deficit",
            "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm",
            "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm",
            "soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm"
        ]
    }


@server.tool
async def get_weather_forecast(request: ForecastRequest) -> dict:
    """Get weather forecast with HTTP transport and structured output support.
    
    This unified tool demonstrates:
    - HTTP transport for distributed deployment
    - Coordinate optimization for performance
    - Optional structured output transformation
    - Comprehensive weather data retrieval
    """
    try:
        # Resolve location with coordinate preference
        if request.latitude is not None and request.longitude is not None:
            coords = {
                "latitude": request.latitude, 
                "longitude": request.longitude, 
                "name": request.location or f"{request.latitude:.4f},{request.longitude:.4f}"
            }
            logger.info(f"Using direct coordinates: {coords['latitude']}, {coords['longitude']}")
        elif request.location:
            coords = await get_coordinates(request.location)
            if not coords:
                return {
                    "error": f"Could not find location: {request.location}",
                    "suggestion": "Try a major city name or provide coordinates directly"
                }
        else:
            return {"error": "Either location name or coordinates required"}

        # Get comprehensive parameters
        params_config = get_comprehensive_params()
        
        # Prepare API request
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "forecast_days": request.days,
            "daily": ",".join(params_config["daily"]),
            "hourly": ",".join(params_config["hourly"][:5]),  # Limit hourly for performance
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,pressure_msl",
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add metadata
        data["_metadata"] = {
            "location_info": {
                "name": coords.get("name", request.location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            },
            "request_type": "forecast",
            "transport": "HTTP",
            "server": "unified-weather-server",
            "days_requested": request.days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return {"error": f"Error getting forecast: {str(e)}"}


@server.tool
async def get_historical_weather(request: HistoricalRequest) -> dict:
    """Get historical weather data via HTTP for climate analysis."""
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
                return {"error": f"Could not find location: {request.location}"}
        else:
            return {"error": "Either location name or coordinates required"}

        # Prepare comprehensive parameters
        params_config = get_comprehensive_params()
        
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "start_date": request.start_date,
            "end_date": request.end_date,
            "daily": ",".join(params_config["daily"]),
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.archive_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add metadata
        data["_metadata"] = {
            "location_info": {
                "name": coords.get("name", request.location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            },
            "request_type": "historical",
            "transport": "HTTP",
            "date_range": {
                "start": request.start_date,
                "end": request.end_date
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Historical error: {e}")
        return {"error": f"Error getting historical data: {str(e)}"}


@server.tool
async def get_agricultural_conditions(request: AgriculturalRequest) -> dict:
    """Get agricultural conditions with soil moisture analysis via HTTP."""
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
                return {"error": f"Could not find location: {request.location}"}
        else:
            return {"error": "Either location name or coordinates required"}

        # Get agricultural parameters
        params_config = get_comprehensive_params()
        
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "forecast_days": request.days,
            "hourly": ",".join(params_config["agricultural"]),
            "daily": "et0_fao_evapotranspiration",
            "timezone": "auto"
        }
        
        # Make API request
        async with client:
            response = await client._client.get(client.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Add metadata
        data["_metadata"] = {
            "location_info": {
                "name": coords.get("name", request.location),
                "coordinates": {
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
            },
            "request_type": "agricultural",
            "transport": "HTTP",
            "days_requested": request.days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Agricultural error: {e}")
        return {"error": f"Error getting agricultural data: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("MCP_SERVER_PORT", "7074"))
    
    logger.info(f"Starting unified weather server on port {port}")
    logger.info("HTTP transport enabled for distributed deployment")
    
    # Run with uvicorn for production-ready HTTP server
    uvicorn.run(
        server.app, 
        host="0.0.0.0",  # Allow external connections for distributed deployment
        port=port,
        log_level="info"
    )