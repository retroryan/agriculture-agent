"""
Core weather data models for structured API responses.

These models represent weather data from Open-Meteo API in a type-safe,
validated structure using Pydantic.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class Coordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    
    def __str__(self) -> str:
        return f"{self.latitude:.4f}, {self.longitude:.4f}"


class LocationInfo(BaseModel):
    """Complete location information with enhanced query classification support."""
    name: str = Field(..., description="Human-readable location name")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    country: Optional[str] = Field(None, description="Country name")
    state: Optional[str] = Field(None, description="State or province")
    timezone: Optional[str] = Field(None, description="IANA timezone identifier")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    normalized_name: Optional[str] = Field(None, description="Normalized name for geocoding API")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in location identification")
    
    def display_name(self) -> str:
        """Get a formatted display name."""
        parts = [self.name]
        if self.state:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)
    
    def has_coordinates(self) -> bool:
        """Check if coordinates are available."""
        return self.coordinates is not None
    
    def get_geocoding_name(self) -> str:
        """Get the best name for geocoding."""
        return self.normalized_name or self.name


class WeatherDataPoint(BaseModel):
    """A single weather observation or forecast point."""
    timestamp: datetime
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    apparent_temperature: Optional[float] = Field(None, description="Feels-like temperature")
    precipitation: Optional[float] = Field(None, description="Precipitation in mm")
    humidity: Optional[int] = Field(None, ge=0, le=100, description="Relative humidity %")
    pressure: Optional[float] = Field(None, description="Surface pressure in hPa")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed in km/h")
    wind_direction: Optional[int] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    cloud_cover: Optional[int] = Field(None, ge=0, le=100, description="Cloud cover %")
    weather_code: Optional[int] = Field(None, description="WMO weather code")
    
    @field_validator('temperature', 'apparent_temperature')
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        """Validate temperature is within reasonable bounds."""
        if v is not None and not -100 <= v <= 100:
            raise ValueError(f"Temperature {v}°C is outside reasonable bounds")
        return v


class HourlyWeatherData(BaseModel):
    """Container for hourly weather data arrays."""
    time: List[datetime]
    temperature_2m: Optional[List[float]] = None
    apparent_temperature: Optional[List[float]] = None
    precipitation: Optional[List[float]] = None
    rain: Optional[List[float]] = None
    showers: Optional[List[float]] = None
    snowfall: Optional[List[float]] = None
    relative_humidity_2m: Optional[List[int]] = None
    surface_pressure: Optional[List[float]] = None
    wind_speed_10m: Optional[List[float]] = None
    wind_direction_10m: Optional[List[int]] = None
    cloud_cover: Optional[List[int]] = None
    weather_code: Optional[List[int]] = None
    soil_temperature_0cm: Optional[List[float]] = None
    soil_moisture_0_to_1cm: Optional[List[float]] = None
    et0_fao_evapotranspiration: Optional[List[float]] = None
    
    @model_validator(mode='after')
    def validate_array_lengths(self) -> 'HourlyWeatherData':
        """Ensure all arrays have the same length as time array."""
        time_length = len(self.time)
        for field_name, field_value in self.model_dump(exclude={'time'}).items():
            if field_value is not None and len(field_value) != time_length:
                raise ValueError(f"{field_name} array length {len(field_value)} doesn't match time array length {time_length}")
        return self
    
    def to_data_points(self) -> List[WeatherDataPoint]:
        """Convert arrays to list of WeatherDataPoint objects."""
        points = []
        for i, timestamp in enumerate(self.time):
            point_data = {"timestamp": timestamp}
            
            # Map fields to WeatherDataPoint attributes
            field_mapping = {
                "temperature_2m": "temperature",
                "apparent_temperature": "apparent_temperature",
                "precipitation": "precipitation",
                "relative_humidity_2m": "humidity",
                "surface_pressure": "pressure",
                "wind_speed_10m": "wind_speed",
                "wind_direction_10m": "wind_direction",
                "cloud_cover": "cloud_cover",
                "weather_code": "weather_code",
            }
            
            for source_field, target_field in field_mapping.items():
                value = getattr(self, source_field, None)
                if value is not None and i < len(value):
                    point_data[target_field] = value[i]
            
            points.append(WeatherDataPoint(**point_data))
        
        return points


class DailyForecast(BaseModel):
    """Daily aggregated weather forecast."""
    date: date
    temperature_min: float
    temperature_max: float
    temperature_mean: Optional[float] = None
    apparent_temperature_min: Optional[float] = None
    apparent_temperature_max: Optional[float] = None
    precipitation_sum: float = Field(default=0, description="Total precipitation in mm")
    rain_sum: Optional[float] = Field(None, description="Total rain in mm")
    snowfall_sum: Optional[float] = Field(None, description="Total snowfall in cm")
    precipitation_hours: Optional[int] = Field(None, description="Hours with precipitation")
    precipitation_probability_max: Optional[int] = Field(None, ge=0, le=100)
    wind_speed_max: Optional[float] = None
    wind_gusts_max: Optional[float] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    uv_index_max: Optional[float] = None
    et0_fao_evapotranspiration: Optional[float] = Field(None, description="Reference evapotranspiration in mm")
    
    def daylight_hours(self) -> Optional[float]:
        """Calculate daylight hours if sunrise/sunset available."""
        if self.sunrise and self.sunset:
            delta = self.sunset - self.sunrise
            return delta.total_seconds() / 3600
        return None
    
    def temperature_range(self) -> float:
        """Calculate daily temperature range."""
        return self.temperature_max - self.temperature_min


class SoilData(BaseModel):
    """Soil conditions at various depths."""
    timestamp: datetime
    moisture_0_1cm: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture % at 0-1cm")
    moisture_1_3cm: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture % at 1-3cm")
    moisture_3_9cm: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture % at 3-9cm")
    moisture_9_27cm: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture % at 9-27cm")
    moisture_27_81cm: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture % at 27-81cm")
    temperature_0cm: Optional[float] = Field(None, description="Soil temperature °C at surface")
    temperature_6cm: Optional[float] = Field(None, description="Soil temperature °C at 6cm")
    temperature_18cm: Optional[float] = Field(None, description="Soil temperature °C at 18cm")
    temperature_54cm: Optional[float] = Field(None, description="Soil temperature °C at 54cm")
    
    def average_moisture(self, max_depth_cm: Optional[int] = None) -> Optional[float]:
        """Calculate average soil moisture up to specified depth."""
        values = []
        depth_map = {
            1: self.moisture_0_1cm,
            3: self.moisture_1_3cm,
            9: self.moisture_3_9cm,
            27: self.moisture_9_27cm,
            81: self.moisture_27_81cm,
        }
        
        for depth, value in depth_map.items():
            if max_depth_cm is None or depth <= max_depth_cm:
                if value is not None:
                    values.append(value)
        
        return sum(values) / len(values) if values else None


class AgriculturalConditions(BaseModel):
    """Agricultural-specific weather conditions."""
    location: LocationInfo
    date: date
    growing_degree_days: Optional[float] = Field(None, description="GDD accumulated")
    et0_fao_evapotranspiration: Optional[float] = Field(None, description="Reference ET in mm")
    vapor_pressure_deficit: Optional[float] = Field(None, description="VPD in kPa")
    soil_data: Optional[SoilData] = None
    precipitation_7d: Optional[float] = Field(None, description="7-day precipitation total in mm")
    temperature_min_7d: Optional[float] = Field(None, description="7-day minimum temperature")
    temperature_max_7d: Optional[float] = Field(None, description="7-day maximum temperature")
    frost_risk: Optional[bool] = Field(None, description="Risk of frost in next 24-48 hours")
    planting_conditions: Optional[str] = Field(None, description="Assessment of planting conditions")
    irrigation_recommendation: Optional[str] = Field(None, description="Irrigation guidance")


class WeatherForecastResponse(BaseModel):
    """Complete weather forecast response."""
    location: LocationInfo
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    forecast_days: List[DailyForecast]
    hourly_data: Optional[HourlyWeatherData] = None
    current_conditions: Optional[WeatherDataPoint] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_summary(self) -> str:
        """Generate human-readable summary."""
        lines = [f"Weather forecast for {self.location.display_name()}:"]
        
        for i, day in enumerate(self.forecast_days[:7]):  # First week
            temp_range = f"{day.temperature_min:.0f}-{day.temperature_max:.0f}°C"
            precip = f"{day.precipitation_sum:.1f}mm" if day.precipitation_sum > 0 else "no rain"
            lines.append(f"  {day.date}: {temp_range}, {precip}")
        
        if len(self.forecast_days) > 7:
            lines.append(f"  ... and {len(self.forecast_days) - 7} more days")
        
        return "\n".join(lines)


class HistoricalWeatherResponse(BaseModel):
    """Historical weather data response."""
    location: LocationInfo
    start_date: date
    end_date: date
    daily_data: List[DailyForecast]
    hourly_data: Optional[HourlyWeatherData] = None
    statistics: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate basic statistics for the period."""
        if not self.daily_data:
            return {}
        
        temps_min = [d.temperature_min for d in self.daily_data]
        temps_max = [d.temperature_max for d in self.daily_data]
        precip = [d.precipitation_sum for d in self.daily_data]
        
        return {
            "temperature": {
                "min": min(temps_min),
                "max": max(temps_max),
                "avg_min": sum(temps_min) / len(temps_min),
                "avg_max": sum(temps_max) / len(temps_max),
            },
            "precipitation": {
                "total": sum(precip),
                "days_with_rain": len([p for p in precip if p > 0.1]),
                "max_daily": max(precip),
            },
            "period_days": len(self.daily_data),
        }