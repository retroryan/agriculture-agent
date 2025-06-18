"""
Input validation models for MCP tools.

These models provide comprehensive validation for tool inputs, including
smart defaults, constraint checking, and helpful error messages.
"""

from typing import Union, List, Optional, Literal, Set, Dict
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

from .weather import Coordinates, LocationInfo


class WeatherParameter(str, Enum):
    """Available weather parameters for queries."""
    # Temperature
    TEMPERATURE = "temperature"
    APPARENT_TEMPERATURE = "apparent_temperature"
    TEMPERATURE_MIN = "temperature_min"
    TEMPERATURE_MAX = "temperature_max"
    
    # Precipitation
    PRECIPITATION = "precipitation"
    RAIN = "rain"
    SNOW = "snow"
    PRECIPITATION_PROBABILITY = "precipitation_probability"
    
    # Wind
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    WIND_GUSTS = "wind_gusts"
    
    # Humidity & Pressure
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    
    # Cloud & Visibility
    CLOUD_COVER = "cloud_cover"
    VISIBILITY = "visibility"
    
    # Agricultural
    SOIL_MOISTURE = "soil_moisture"
    SOIL_TEMPERATURE = "soil_temperature"
    EVAPOTRANSPIRATION = "evapotranspiration"
    VAPOR_PRESSURE_DEFICIT = "vapor_pressure_deficit"
    GROWING_DEGREE_DAYS = "growing_degree_days"
    
    # Solar
    UV_INDEX = "uv_index"
    SOLAR_RADIATION = "solar_radiation"
    DAYLIGHT_DURATION = "daylight_duration"




def validate_date_range(start: date, end: date) -> tuple[date, date]:
    """
    Validate and potentially adjust date range.
    
    Returns:
        Tuple of (start_date, end_date) potentially adjusted
    """
    if end < start:
        raise ValueError(f"End date {end} cannot be before start date {start}")
    
    # Check if range is too large (e.g., > 1 year)
    days_diff = (end - start).days
    if days_diff > 365:
        raise ValueError(f"Date range of {days_diff} days exceeds maximum of 365 days")
    
    return start, end


class LocationInput(BaseModel):
    """Flexible location specification supporting multiple input formats."""
    name: Optional[str] = Field(None, description="Location name for geocoding")
    coordinates: Optional[Union[Coordinates, Dict[str, float]]] = Field(None, description="Direct coordinates")
    normalized_name: Optional[str] = Field(None, description="Normalized name for geocoding API")
    country: Optional[str] = Field(None, description="Country for disambiguation")
    state: Optional[str] = Field(None, description="State/province for disambiguation")
    
    @field_validator('coordinates', mode='before')
    @classmethod
    def validate_coordinates(cls, v):
        """Convert dict to Coordinates if needed."""
        if v is None:
            return None
        if isinstance(v, dict):
            return Coordinates(**v)
        return v
    
    @model_validator(mode='after')
    def validate_location_spec(self) -> 'LocationInput':
        """Ensure at least one location method is provided."""
        if not self.name and not self.coordinates:
            raise ValueError("Either location name or coordinates must be provided")
        return self
    
    def to_location_info(self) -> LocationInfo:
        """Convert to LocationInfo with geocoding if needed."""
        if self.coordinates:
            name = self.name or f"{self.coordinates.latitude:.4f}, {self.coordinates.longitude:.4f}"
            return LocationInfo(
                name=name,
                coordinates=self.coordinates,
                country=self.country,
                state=self.state
            )
        
        # Would normally geocode here
        raise ValueError(f"Location coordinates required. Location '{self.name}' needs geocoding.")


class ForecastToolInput(BaseModel):
    """Validated input for weather forecast tool."""
    location: Union[str, LocationInput, Coordinates, Dict] = Field(
        ...,
        description="Location as string, coordinates, or structured input"
    )
    days: int = Field(
        default=7,
        ge=1,
        le=16,
        description="Number of forecast days (1-16)"
    )
    include_hourly: bool = Field(
        default=False,
        description="Include hourly forecast data"
    )
    parameters: List[WeatherParameter] = Field(
        default_factory=lambda: [
            WeatherParameter.TEMPERATURE,
            WeatherParameter.PRECIPITATION,
            WeatherParameter.WIND_SPEED
        ],
        description="Weather parameters to include"
    )
    units: Literal["metric", "imperial"] = Field(
        default="metric",
        description="Unit system for output"
    )
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Union[str, LocationInput, Coordinates, Dict]) -> LocationInput:
        """Convert location to standardized format."""
        if isinstance(v, str):
            return LocationInput(name=v)
        elif isinstance(v, Coordinates):
            return LocationInput(coordinates=v)
        elif isinstance(v, dict):
            # Handle dict that might contain location data
            return LocationInput(**v)
        return v
    
    @field_validator('parameters')
    @classmethod
    def validate_parameters(cls, v: List[WeatherParameter]) -> List[WeatherParameter]:
        """Ensure unique parameters and add dependencies."""
        unique_params = list(dict.fromkeys(v))  # Remove duplicates while preserving order
        
        # Add dependent parameters
        if WeatherParameter.SOIL_MOISTURE in unique_params:
            # Soil moisture needs temperature for calculations
            if WeatherParameter.SOIL_TEMPERATURE not in unique_params:
                unique_params.append(WeatherParameter.SOIL_TEMPERATURE)
        
        return unique_params
    
    def to_api_params(self) -> dict:
        """Convert to Open-Meteo API parameters."""
        # This would map our enums to actual API parameter names
        param_mapping = {
            WeatherParameter.TEMPERATURE: "temperature_2m",
            WeatherParameter.PRECIPITATION: "precipitation",
            WeatherParameter.WIND_SPEED: "wind_speed_10m",
            # ... etc
        }
        
        hourly = []
        daily = []
        
        for param in self.parameters:
            api_param = param_mapping.get(param, param.value)
            # Determine if hourly or daily based on parameter
            if param in [WeatherParameter.SOIL_MOISTURE, WeatherParameter.SOIL_TEMPERATURE]:
                hourly.append(api_param)
            else:
                daily.append(api_param)
        
        return {
            "hourly": hourly if self.include_hourly else [],
            "daily": daily,
            "forecast_days": self.days
        }


class HistoricalToolInput(BaseModel):
    """Validated input for historical weather tool."""
    location: Union[str, LocationInput, Coordinates] = Field(
        ...,
        description="Location for historical data"
    )
    start_date: date = Field(
        ...,
        description="Start date for historical period"
    )
    end_date: date = Field(
        default_factory=lambda: date.today() - timedelta(days=1),
        description="End date for historical period"
    )
    parameters: List[WeatherParameter] = Field(
        default_factory=lambda: [
            WeatherParameter.TEMPERATURE_MIN,
            WeatherParameter.TEMPERATURE_MAX,
            WeatherParameter.PRECIPITATION
        ],
        description="Weather parameters to retrieve"
    )
    aggregation: Literal["daily", "hourly", "monthly"] = Field(
        default="daily",
        description="Temporal aggregation level"
    )
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Union[str, LocationInput, Coordinates]) -> LocationInput:
        """Convert location to standardized format."""
        if isinstance(v, str):
            return LocationInput(name=v)
        elif isinstance(v, Coordinates):
            return LocationInput(coordinates=v)
        return v
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'HistoricalToolInput':
        """Validate date range and adjust if needed."""
        self.start_date, self.end_date = validate_date_range(self.start_date, self.end_date)
        
        # Ensure dates are not in future
        today = date.today()
        if self.start_date > today:
            raise ValueError(f"Start date {self.start_date} cannot be in the future")
        if self.end_date > today:
            self.end_date = today - timedelta(days=1)
        
        # Check if dates are old enough for historical API (usually 5+ days)
        min_historical_date = today - timedelta(days=5)
        if self.end_date > min_historical_date:
            raise ValueError(
                f"End date {self.end_date} is too recent for historical data. "
                f"Use forecast API for dates after {min_historical_date}"
            )
        
        return self


class AgriculturalToolInput(BaseModel):
    """Validated input for agricultural conditions tool."""
    location: Union[str, LocationInput, Coordinates] = Field(
        ...,
        description="Agricultural location"
    )
    crop_type: Optional[str] = Field(
        None,
        description="Crop type for specific recommendations"
    )
    growth_stage: Optional[str] = Field(
        None,
        description="Current growth stage"
    )
    include_soil: bool = Field(
        default=True,
        description="Include soil moisture and temperature"
    )
    include_solar: bool = Field(
        default=True,
        description="Include solar radiation and UV data"
    )
    include_evapotranspiration: bool = Field(
        default=True,
        description="Include ET0 calculations"
    )
    forecast_days: int = Field(
        default=7,
        ge=1,
        le=14,
        description="Days to forecast"
    )
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Union[str, LocationInput, Coordinates]) -> LocationInput:
        """Convert location to standardized format."""
        if isinstance(v, str):
            return LocationInput(name=v)
        elif isinstance(v, Coordinates):
            return LocationInput(coordinates=v)
        return v
    
    @field_validator('crop_type')
    @classmethod
    def validate_crop_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize crop type."""
        if v is None:
            return v
        
        # Normalize to lowercase
        v = v.lower().strip()
        
        # Known crop types (could be extended)
        known_crops = {
            "corn", "wheat", "soybeans", "cotton", "rice",
            "potatoes", "tomatoes", "lettuce", "almonds", "grapes"
        }
        
        if v not in known_crops:
            # Try to find close match or accept as-is with warning
            pass
        
        return v
    
    def get_required_parameters(self) -> List[WeatherParameter]:
        """Determine required parameters based on options."""
        params = [
            WeatherParameter.TEMPERATURE_MIN,
            WeatherParameter.TEMPERATURE_MAX,
            WeatherParameter.PRECIPITATION,
            WeatherParameter.HUMIDITY,
        ]
        
        if self.include_soil:
            params.extend([
                WeatherParameter.SOIL_MOISTURE,
                WeatherParameter.SOIL_TEMPERATURE
            ])
        
        if self.include_solar:
            params.extend([
                WeatherParameter.UV_INDEX,
                WeatherParameter.SOLAR_RADIATION
            ])
        
        if self.include_evapotranspiration:
            params.append(WeatherParameter.EVAPOTRANSPIRATION)
        
        return params