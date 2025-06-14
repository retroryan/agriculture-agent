"""
Enhanced Open-Meteo API client with Pydantic model support.

This module provides async API access with structured data models,
intelligent caching, and comprehensive error handling.
"""

import httpx
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, timedelta
import asyncio
from functools import lru_cache
import json
import hashlib

import sys
sys.path.append('..')

from models.weather import (
    Coordinates,
    LocationInfo,
    WeatherForecastResponse,
    HistoricalWeatherResponse,
    DailyForecast,
    HourlyWeatherData,
    WeatherDataPoint,
    SoilData,
    AgriculturalConditions,
)
from models.inputs import WeatherParameter
from models.responses import ResponseMetadata, DataQualityAssessment


class APIError(Exception):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """API rate limit exceeded."""
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s" if retry_after else "Rate limit exceeded")


class LocationNotFoundError(APIError):
    """Location could not be geocoded."""
    def __init__(self, location: str, suggestions: Optional[List[str]] = None):
        self.location = location
        self.suggestions = suggestions or []
        msg = f"Location not found: {location}"
        if suggestions:
            msg += f". Did you mean: {', '.join(suggestions[:3])}?"
        super().__init__(msg)


class WeatherCache:
    """Simple in-memory cache for weather data."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[Any, datetime]] = {}
    
    def _make_key(self, **kwargs) -> str:
        """Create cache key from parameters."""
        # Sort kwargs for consistent keys
        sorted_items = sorted(kwargs.items())
        key_str = json.dumps(sorted_items, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, **kwargs) -> Optional[Any]:
        """Get item from cache if not expired."""
        key = self._make_key(**kwargs)
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.utcnow() - timestamp < timedelta(seconds=self.ttl_seconds):
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, data: Any, **kwargs):
        """Store item in cache."""
        key = self._make_key(**kwargs)
        self._cache[key] = (data, datetime.utcnow())
    
    def clear(self):
        """Clear all cached items."""
        self._cache.clear()


class EnhancedOpenMeteoClient:
    """
    Enhanced Open-Meteo API client with structured response models.
    
    Features:
    - Async HTTP with connection pooling
    - Automatic retry with backoff
    - Response caching
    - Structured Pydantic models
    - Comprehensive error handling
    """
    
    BASE_URLS = {
        "forecast": "https://api.open-meteo.com/v1/forecast",
        "archive": "https://archive-api.open-meteo.com/v1/archive",
        "geocoding": "https://geocoding-api.open-meteo.com/v1/search",
    }
    
    def __init__(self, cache_ttl: int = 300, max_retries: int = 3):
        self.client: Optional[httpx.AsyncClient] = None
        self.cache = WeatherCache(ttl_seconds=cache_ttl)
        self.max_retries = max_retries
    
    async def ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=5.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def _make_request(
        self,
        url: str,
        params: Dict[str, Any],
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry and caching."""
        await self.ensure_client()
        
        # Check cache
        if cache_key:
            cached = self.cache.get(url=url, key=cache_key)
            if cached:
                return cached
        
        # Attempt request with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url, params=params)
                
                if response.status_code == 429:
                    # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError(retry_after)
                
                response.raise_for_status()
                data = response.json()
                
                # Cache successful response
                if cache_key:
                    self.cache.set(data, url=url, key=cache_key)
                
                return data
                
            except httpx.HTTPStatusError as e:
                last_error = APIError(f"HTTP {e.response.status_code}: {e.response.text}")
            except httpx.RequestError as e:
                last_error = APIError(f"Request failed: {str(e)}")
            except RateLimitError:
                raise  # Don't retry rate limit errors
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        raise last_error or APIError("Max retries exceeded")
    
    async def geocode(self, location: str) -> LocationInfo:
        """
        Geocode a location string to coordinates.
        
        Args:
            location: Location name to geocode
            
        Returns:
            LocationInfo with coordinates and metadata
            
        Raises:
            LocationNotFoundError: If location cannot be found
        """
        params = {
            "name": location,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        
        data = await self._make_request(
            self.BASE_URLS["geocoding"],
            params,
            cache_key=f"geocode_{location}"
        )
        
        if not data.get("results"):
            raise LocationNotFoundError(location)
        
        # Take the first result
        result = data["results"][0]
        
        return LocationInfo(
            name=result.get("name", location),
            coordinates=Coordinates(
                latitude=result["latitude"],
                longitude=result["longitude"]
            ),
            country=result.get("country"),
            state=result.get("admin1"),  # First-level administrative division
            timezone=result.get("timezone"),
            elevation=result.get("elevation")
        )
    
    async def get_forecast(
        self,
        location: Union[LocationInfo, Coordinates],
        days: int = 7,
        hourly_params: Optional[List[str]] = None,
        daily_params: Optional[List[str]] = None,
        include_current: bool = False
    ) -> WeatherForecastResponse:
        """
        Get weather forecast with structured response.
        
        Args:
            location: Location information or coordinates
            days: Number of forecast days (1-16)
            hourly_params: Hourly parameters to retrieve
            daily_params: Daily parameters to retrieve
            include_current: Include current conditions
            
        Returns:
            Structured forecast response
        """
        # Prepare coordinates
        if isinstance(location, Coordinates):
            coords = location
            location_info = LocationInfo(
                name=f"{coords.latitude:.4f}, {coords.longitude:.4f}",
                coordinates=coords
            )
        else:
            coords = location.coordinates
            location_info = location
        
        # Default parameters if not specified
        if daily_params is None:
            daily_params = [
                "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
                "apparent_temperature_max", "apparent_temperature_min",
                "precipitation_sum", "rain_sum", "snowfall_sum",
                "precipitation_hours", "wind_speed_10m_max",
                "sunrise", "sunset", "uv_index_max",
                "et0_fao_evapotranspiration"
            ]
        
        params = {
            "latitude": coords.latitude,
            "longitude": coords.longitude,
            "forecast_days": min(days, 16),
            "timezone": "auto",
        }
        
        if hourly_params:
            params["hourly"] = ",".join(hourly_params)
        if daily_params:
            params["daily"] = ",".join(daily_params)
        if include_current:
            params["current"] = "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code"
        
        # Make API request
        cache_key = f"forecast_{coords}_{days}_{hash(tuple(sorted(hourly_params or [])))}"
        data = await self._make_request(
            self.BASE_URLS["forecast"],
            params,
            cache_key=cache_key
        )
        
        # Parse response into structured models
        forecast_days = []
        if "daily" in data:
            daily = data["daily"]
            for i in range(len(daily.get("time", []))):
                day_data = {
                    "date": datetime.fromisoformat(daily["time"][i]).date()
                }
                
                # Map all available fields
                field_mapping = {
                    "temperature_2m_max": "temperature_max",
                    "temperature_2m_min": "temperature_min",
                    "temperature_2m_mean": "temperature_mean",
                    "apparent_temperature_max": "apparent_temperature_max",
                    "apparent_temperature_min": "apparent_temperature_min",
                    "precipitation_sum": "precipitation_sum",
                    "rain_sum": "rain_sum",
                    "snowfall_sum": "snowfall_sum",
                    "precipitation_hours": "precipitation_hours",
                    "precipitation_probability_max": "precipitation_probability_max",
                    "wind_speed_10m_max": "wind_speed_max",
                    "wind_gusts_10m_max": "wind_gusts_max",
                    "uv_index_max": "uv_index_max",
                    "et0_fao_evapotranspiration": "et0_fao_evapotranspiration",
                }
                
                for api_field, model_field in field_mapping.items():
                    if api_field in daily and i < len(daily[api_field]):
                        value = daily[api_field][i]
                        if value is not None:
                            day_data[model_field] = value
                
                # Handle datetime fields
                if "sunrise" in daily and i < len(daily["sunrise"]):
                    day_data["sunrise"] = datetime.fromisoformat(daily["sunrise"][i])
                if "sunset" in daily and i < len(daily["sunset"]):
                    day_data["sunset"] = datetime.fromisoformat(daily["sunset"][i])
                
                forecast_days.append(DailyForecast(**day_data))
        
        # Parse hourly data if present
        hourly_data = None
        if "hourly" in data and data["hourly"].get("time"):
            hourly_dict = {"time": [datetime.fromisoformat(t) for t in data["hourly"]["time"]]}
            
            # Copy all other arrays
            for key, values in data["hourly"].items():
                if key != "time":
                    hourly_dict[key] = values
            
            hourly_data = HourlyWeatherData(**hourly_dict)
        
        # Parse current conditions if present
        current_conditions = None
        if "current" in data:
            current = data["current"]
            current_conditions = WeatherDataPoint(
                timestamp=datetime.fromisoformat(current["time"]),
                temperature=current.get("temperature_2m"),
                apparent_temperature=current.get("apparent_temperature"),
                precipitation=current.get("precipitation"),
                humidity=current.get("relative_humidity_2m"),
                weather_code=current.get("weather_code"),
            )
        
        # Create response metadata
        metadata = ResponseMetadata(
            source="open-meteo-forecast",
            api_calls_made=1,
            data_quality=DataQualityAssessment(
                completeness=0.95 if len(forecast_days) == days else len(forecast_days) / days,
                missing_fields=[],
                quality_issues=[],
                confidence=0.95
            )
        )
        
        return WeatherForecastResponse(
            location=location_info,
            forecast_days=forecast_days,
            hourly_data=hourly_data,
            current_conditions=current_conditions,
            metadata=metadata.model_dump()
        )
    
    async def get_historical(
        self,
        location: Union[LocationInfo, Coordinates],
        start_date: date,
        end_date: date,
        hourly_params: Optional[List[str]] = None,
        daily_params: Optional[List[str]] = None
    ) -> HistoricalWeatherResponse:
        """
        Get historical weather data with structured response.
        
        Args:
            location: Location information or coordinates
            start_date: Start date for historical data
            end_date: End date for historical data
            hourly_params: Hourly parameters to retrieve
            daily_params: Daily parameters to retrieve
            
        Returns:
            Structured historical response
        """
        # Prepare coordinates
        if isinstance(location, Coordinates):
            coords = location
            location_info = LocationInfo(
                name=f"{coords.latitude:.4f}, {coords.longitude:.4f}",
                coordinates=coords
            )
        else:
            coords = location.coordinates
            location_info = location
        
        # Default parameters if not specified
        if daily_params is None:
            daily_params = [
                "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "rain_sum", "snowfall_sum",
                "wind_speed_10m_max", "et0_fao_evapotranspiration"
            ]
        
        params = {
            "latitude": coords.latitude,
            "longitude": coords.longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto",
        }
        
        if hourly_params:
            params["hourly"] = ",".join(hourly_params)
        if daily_params:
            params["daily"] = ",".join(daily_params)
        
        # Make API request
        cache_key = f"historical_{coords}_{start_date}_{end_date}"
        data = await self._make_request(
            self.BASE_URLS["archive"],
            params,
            cache_key=cache_key
        )
        
        # Parse daily data
        daily_data = []
        if "daily" in data:
            daily = data["daily"]
            for i in range(len(daily.get("time", []))):
                day_data = {
                    "date": datetime.fromisoformat(daily["time"][i]).date()
                }
                
                # Map fields
                field_mapping = {
                    "temperature_2m_max": "temperature_max",
                    "temperature_2m_min": "temperature_min",
                    "precipitation_sum": "precipitation_sum",
                    "rain_sum": "rain_sum",
                    "snowfall_sum": "snowfall_sum",
                    "wind_speed_10m_max": "wind_speed_max",
                    "et0_fao_evapotranspiration": "et0_fao_evapotranspiration",
                }
                
                for api_field, model_field in field_mapping.items():
                    if api_field in daily and i < len(daily[api_field]):
                        value = daily[api_field][i]
                        if value is not None:
                            day_data[model_field] = value
                
                daily_data.append(DailyForecast(**day_data))
        
        # Parse hourly data if present
        hourly_data = None
        if "hourly" in data and data["hourly"].get("time"):
            hourly_dict = {"time": [datetime.fromisoformat(t) for t in data["hourly"]["time"]]}
            
            for key, values in data["hourly"].items():
                if key != "time":
                    hourly_dict[key] = values
            
            hourly_data = HourlyWeatherData(**hourly_dict)
        
        # Create response
        response = HistoricalWeatherResponse(
            location=location_info,
            start_date=start_date,
            end_date=end_date,
            daily_data=daily_data,
            hourly_data=hourly_data,
            metadata={
                "source": "open-meteo-archive",
                "data_points": len(daily_data)
            }
        )
        
        # Calculate statistics
        response.statistics = response.calculate_statistics()
        
        return response
    
    async def get_agricultural_conditions(
        self,
        location: Union[LocationInfo, Coordinates],
        days: int = 7,
        include_soil: bool = True,
        include_solar: bool = True
    ) -> AgriculturalConditions:
        """
        Get agricultural-specific conditions.
        
        Args:
            location: Location information
            days: Forecast days for aggregations
            include_soil: Include soil data
            include_solar: Include solar/radiation data
            
        Returns:
            Agricultural conditions assessment
        """
        # Build parameter list
        hourly_params = ["temperature_2m", "relative_humidity_2m", "precipitation"]
        
        if include_soil:
            hourly_params.extend([
                "soil_temperature_0cm", "soil_temperature_6cm",
                "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
                "soil_moisture_3_to_9cm"
            ])
        
        if include_solar:
            hourly_params.extend([
                "shortwave_radiation", "et0_fao_evapotranspiration",
                "vapour_pressure_deficit"
            ])
        
        # Get forecast data
        forecast = await self.get_forecast(
            location=location,
            days=days,
            hourly_params=hourly_params,
            daily_params=[
                "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "et0_fao_evapotranspiration"
            ]
        )
        
        # Extract current soil conditions
        soil_data = None
        if include_soil and forecast.hourly_data:
            current_hour = 0  # Most recent hour
            soil_data = SoilData(
                timestamp=forecast.hourly_data.time[current_hour],
                moisture_0_1cm=forecast.hourly_data.soil_moisture_0_to_1cm[current_hour] if forecast.hourly_data.soil_moisture_0_to_1cm else None,
                moisture_1_3cm=forecast.hourly_data.soil_moisture_1_to_3cm[current_hour] if hasattr(forecast.hourly_data, 'soil_moisture_1_to_3cm') else None,
                temperature_0cm=forecast.hourly_data.soil_temperature_0cm[current_hour] if forecast.hourly_data.soil_temperature_0cm else None,
            )
        
        # Calculate 7-day aggregates
        precip_7d = sum(d.precipitation_sum for d in forecast.forecast_days[:7])
        temp_min_7d = min(d.temperature_min for d in forecast.forecast_days[:7])
        temp_max_7d = max(d.temperature_max for d in forecast.forecast_days[:7])
        
        # Assess frost risk
        frost_risk = any(d.temperature_min < 0 for d in forecast.forecast_days[:2])
        
        # Planting conditions assessment
        avg_soil_moisture = soil_data.average_moisture(max_depth_cm=10) if soil_data else None
        if avg_soil_moisture is not None:
            if avg_soil_moisture < 20:
                planting_conditions = "Too dry for planting - irrigation recommended"
            elif avg_soil_moisture > 80:
                planting_conditions = "Too wet for planting - wait for drying"
            else:
                planting_conditions = "Good planting conditions"
        else:
            planting_conditions = "Unable to assess - soil moisture data unavailable"
        
        # Irrigation recommendation
        et0_total = sum(d.et0_fao_evapotranspiration or 0 for d in forecast.forecast_days[:7])
        if et0_total > precip_7d:
            irrigation_recommendation = f"Irrigation needed: {et0_total - precip_7d:.1f}mm deficit over next 7 days"
        else:
            irrigation_recommendation = "Adequate moisture expected from precipitation"
        
        return AgriculturalConditions(
            location=forecast.location,
            date=date.today(),
            et0_fao_evapotranspiration=forecast.forecast_days[0].et0_fao_evapotranspiration if forecast.forecast_days else None,
            soil_data=soil_data,
            precipitation_7d=precip_7d,
            temperature_min_7d=temp_min_7d,
            temperature_max_7d=temp_max_7d,
            frost_risk=frost_risk,
            planting_conditions=planting_conditions,
            irrigation_recommendation=irrigation_recommendation
        )