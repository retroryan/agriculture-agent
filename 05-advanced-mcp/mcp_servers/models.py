"""
Pydantic models for Stage 5 MCP server request validation.
Supports structured output processing while keeping server responses simple.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime, date


class LocationInput(BaseModel):
    """
    Base model for location and coordinate inputs with validation.
    Supports both location names and direct coordinates for flexibility.
    """
    location: Optional[str] = Field(
        None, 
        description="Location name (e.g., 'Chicago, IL'). Slower due to geocoding."
    )
    latitude: Optional[float] = Field(
        None, 
        description="Direct latitude (-90 to 90). PREFERRED for faster response."
    )
    longitude: Optional[float] = Field(
        None, 
        description="Direct longitude (-180 to 180). PREFERRED for faster response."
    )
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        """Validate latitude is within valid range."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError(f'Latitude must be between -90 and 90, got {v}')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude is within valid range."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError(f'Longitude must be between -180 and 180, got {v}')
        return v
    
    @model_validator(mode='after')
    def check_at_least_one_location(self):
        """Ensure at least one location method is provided."""
        has_location = self.location is not None
        has_coords = self.latitude is not None and self.longitude is not None
        if not has_location and not has_coords:
            raise ValueError('Either location name or coordinates (latitude, longitude) required')
        return self


class ForecastRequest(LocationInput):
    """Request model for weather forecast tool."""
    days: int = Field(
        default=7,
        ge=1,
        le=16,
        description="Number of forecast days (1-16)"
    )


class HistoricalRequest(LocationInput):
    """Request model for historical weather tool."""
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
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format and parse to ensure it's valid."""
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
    """Request model for agricultural conditions tool."""
    days: int = Field(
        default=7,
        ge=1,
        le=7,
        description="Number of forecast days (1-7)"
    )


# Parameter lists for Open-Meteo API requests
def get_daily_params() -> List[str]:
    """Get standard daily weather parameters."""
    return [
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "precipitation_sum",
        "rain_sum",
        "showers_sum",
        "snowfall_sum",
        "precipitation_hours",
        "weather_code",
        "sunrise",
        "sunset",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "uv_index_max",
        "et0_fao_evapotranspiration"
    ]


def get_hourly_params() -> List[str]:
    """Get standard hourly weather parameters."""
    return [
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "pressure_msl",
        "surface_pressure",
        "cloud_cover",
        "visibility",
        "wind_speed_10m",
        "wind_direction_10m"
    ]


def get_agricultural_params() -> List[str]:
    """Get agricultural-specific parameters."""
    return [
        "et0_fao_evapotranspiration",
        "vapour_pressure_deficit",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "soil_moisture_27_to_81cm",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_temperature_54cm"
    ]