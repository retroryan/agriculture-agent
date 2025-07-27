"""
Pydantic models for Stage 7 MCP server - Advanced HTTP Agent.
Supports distributed deployment with comprehensive validation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class LocationInput(BaseModel):
    """
    Advanced location input for distributed systems.
    Supports both location names and coordinates with performance hints.
    """
    location: Optional[str] = Field(
        None, 
        description="Location name (e.g., 'Chicago, IL'). Slower due to geocoding API call."
    )
    latitude: Optional[float] = Field(
        None, 
        description="Direct latitude (-90 to 90). PREFERRED - 3x faster, no geocoding needed."
    )
    longitude: Optional[float] = Field(
        None, 
        description="Direct longitude (-180 to 180). PREFERRED - 3x faster, no geocoding needed."
    )
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        """Validate latitude is within valid range."""
        if v is not None:
            if not -90 <= v <= 90:
                raise ValueError(f'Latitude must be between -90 and 90, got {v}')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude is within valid range."""
        if v is not None:
            if not -180 <= v <= 180:
                raise ValueError(f'Longitude must be between -180 and 180, got {v}')
        return v
    
    @model_validator(mode='after')
    def check_location_provided(self):
        """Ensure at least one location method is provided."""
        has_location = self.location is not None
        has_coords = self.latitude is not None and self.longitude is not None
        
        if not has_location and not has_coords:
            raise ValueError(
                'Either location name or coordinates (latitude, longitude) required. '
                'Coordinates are 3x faster!'
            )
        
        # Warn if both are provided
        if has_location and has_coords:
            # Coordinates take precedence - just note this in the model
            self._uses_coordinates = True
        elif has_coords:
            self._uses_coordinates = True
        else:
            self._uses_coordinates = False
            
        return self


class ForecastRequest(LocationInput):
    """Request model for weather forecast with HTTP transport."""
    days: int = Field(
        default=7,
        ge=1,
        le=16,
        description="Number of forecast days (1-16). More days = larger response."
    )
    include_hourly: bool = Field(
        default=False,
        description="Include hourly data (increases response size significantly)"
    )


class HistoricalRequest(LocationInput):
    """Request model for historical weather via HTTP."""
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
        """Validate date format and ensure it's a valid date."""
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            # Check if date is not in the future
            if parsed_date > date.today():
                raise ValueError(f"Date cannot be in the future: {v}")
        except ValueError as e:
            if "Invalid date" in str(e):
                raise ValueError(f"Invalid date format: {v}. Use YYYY-MM-DD.")
            raise
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range constraints."""
        if self.start_date and self.end_date:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            
            if end < start:
                raise ValueError("End date must be after or equal to start date.")
            
            # Check range isn't too large (for performance)
            days_diff = (end - start).days
            if days_diff > 365:
                raise ValueError(
                    f"Date range too large ({days_diff} days). "
                    "Maximum 365 days for performance reasons."
                )
                
        return self


class AgriculturalRequest(LocationInput):
    """Request model for agricultural conditions via HTTP."""
    days: int = Field(
        default=7,
        ge=1,
        le=7,
        description="Number of forecast days (1-7) for agricultural planning"
    )
    soil_depths: List[str] = Field(
        default_factory=lambda: ["0_to_1cm", "1_to_3cm", "3_to_9cm"],
        description="Soil moisture depth layers to include"
    )
    include_evapotranspiration: bool = Field(
        default=True,
        description="Include ET0 FAO evapotranspiration data"
    )


# Parameter configuration for comprehensive data retrieval
def get_weather_params_config() -> Dict[str, List[str]]:
    """Get comprehensive weather parameter configuration."""
    return {
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "weather_code",
            "pressure_msl",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m"
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "rain_sum",
            "showers_sum",
            "snowfall_sum",
            "precipitation_hours",
            "precipitation_probability_max",
            "weather_code",
            "sunrise",
            "sunset",
            "daylight_duration",
            "sunshine_duration",
            "uv_index_max",
            "uv_index_clear_sky_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
            "shortwave_radiation_sum",
            "et0_fao_evapotranspiration"
        ],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "snow_depth",
            "weather_code",
            "pressure_msl",
            "surface_pressure",
            "cloud_cover",
            "cloud_cover_low",
            "cloud_cover_mid",
            "cloud_cover_high",
            "visibility",
            "evapotranspiration",
            "et0_fao_evapotranspiration",
            "vapour_pressure_deficit",
            "wind_speed_10m",
            "wind_speed_80m",
            "wind_speed_120m",
            "wind_direction_10m",
            "wind_direction_80m",
            "wind_direction_120m",
            "wind_gusts_10m",
            "temperature_80m",
            "temperature_120m"
        ]
    }


def get_agricultural_params() -> List[str]:
    """Get agricultural-specific parameters."""
    return [
        "et0_fao_evapotranspiration",
        "vapour_pressure_deficit",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_temperature_54cm",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "soil_moisture_27_to_81cm"
    ]