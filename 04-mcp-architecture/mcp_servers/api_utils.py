"""
Unified OpenMeteo API client for weather and agricultural data.

This client provides a comprehensive interface to Open-Meteo's free weather API,
combining the best features from multiple implementations.
No authentication required - just make requests and get data!
"""

import asyncio
import httpx
import requests
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta, date


class OpenMeteoClient:
    """Unified client for Open-Meteo API with comprehensive functionality."""
    
    def __init__(self):
        """Initialize the Open-Meteo client with session management."""
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.archive_url = "https://archive-api.open-meteo.com/v1/archive"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.session = requests.Session()
        self._async_client: Optional[httpx.AsyncClient] = None
        
    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=30.0)
        return self._async_client
        
    async def close(self):
        """Close the async HTTP client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
        
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Convert city name to coordinates (legacy method)."""
        # Extract just the city name from formats like "City, State"
        city = location.split(',')[0].strip()
        coords = self.get_coordinates_detailed(city)
        if coords:
            return coords
        raise ValueError(f"Location '{location}' not found")
    
    def get_coordinates_detailed(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a location by name with detailed error handling.
        
        Args:
            location_name: Name of the location
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        results = self.geocode(location_name, count=1)
        if results:
            location = results[0]
            return location["latitude"], location["longitude"]
        return None
    
    def geocode(self, name: str, count: int = 10) -> List[Dict]:
        """
        Search for locations by name and get their coordinates.
        
        Args:
            name: Name of the location to search for
            count: Maximum number of results to return (default: 10)
        
        Returns:
            List of matching locations with coordinates
        """
        params = {
            "name": name,
            "count": count,
            "language": "en",
            "format": "json"
        }
        
        response = self.session.get(self.geocoding_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    
    async def geocode_async(self, name: str, count: int = 10) -> List[Dict]:
        """
        Search for locations by name and get their coordinates (async version).
        
        Args:
            name: Name of the location to search for
            count: Maximum number of results to return (default: 10)
        
        Returns:
            List of matching locations with coordinates
        """
        params = {
            "name": name,
            "count": count,
            "language": "en",
            "format": "json"
        }
        
        client = await self._get_async_client()
        response = await client.get(self.geocoding_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        parameters: Optional[List[str]] = None,
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None,
        current: Optional[List[str]] = None,
        days: int = 7,
        past_days: int = 0,
        forecast_days: Optional[int] = None,
        timezone: str = "auto"
    ) -> Dict:
        """
        Get weather forecast data with flexible parameter specification.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            parameters: List of hourly parameters (legacy compatibility)
            hourly: List of hourly variables to retrieve
            daily: List of daily variables to retrieve
            current: List of current weather variables to retrieve
            days: Number of forecast days (legacy compatibility)
            past_days: Number of past days to include (max 92)
            forecast_days: Number of forecast days (max 16)
            timezone: Timezone for the data (default: "auto")
        
        Returns:
            Dictionary containing the weather data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }
        
        # Handle legacy parameters parameter
        if parameters:
            hourly = parameters
            
        # Handle legacy days parameter
        if forecast_days is None:
            forecast_days = days
        
        if hourly:
            params["hourly"] = ",".join(hourly)
        if daily:
            params["daily"] = ",".join(daily)
        if current:
            params["current"] = ",".join(current)
        if past_days > 0:
            params["past_days"] = past_days
        if forecast_days > 0:
            params["forecast_days"] = forecast_days
        
        response = self.session.get(self.forecast_url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_forecast_async(
        self,
        latitude: float,
        longitude: float,
        parameters: Optional[List[str]] = None,
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None,
        current: Optional[List[str]] = None,
        days: int = 7,
        past_days: int = 0,
        forecast_days: Optional[int] = None,
        timezone: str = "auto"
    ) -> Dict:
        """
        Get weather forecast data with flexible parameter specification (async version).
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            parameters: List of hourly parameters (legacy compatibility)
            hourly: List of hourly variables to retrieve
            daily: List of daily variables to retrieve
            current: List of current weather variables to retrieve
            days: Number of forecast days (legacy compatibility)
            past_days: Number of past days to include (max 92)
            forecast_days: Number of forecast days (max 16)
            timezone: Timezone for the data (default: "auto")
        
        Returns:
            Dictionary containing the weather data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }
        
        # Handle legacy parameters parameter
        if parameters:
            hourly = parameters
            
        # Handle legacy days parameter
        if forecast_days is None:
            forecast_days = days
        
        if hourly:
            params["hourly"] = ",".join(hourly)
        if daily:
            params["daily"] = ",".join(daily)
        if current:
            params["current"] = ",".join(current)
        if past_days > 0:
            params["past_days"] = past_days
        if forecast_days > 0:
            params["forecast_days"] = forecast_days
        
        client = await self._get_async_client()
        response = await client.get(self.forecast_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, date],
        end_date: Union[str, date],
        parameters: Optional[List[str]] = None,
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None,
        timezone: str = "auto"
    ) -> Dict:
        """
        Get historical weather data with flexible parameter specification.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_date: Start date for the historical data
            end_date: End date for the historical data
            parameters: List of hourly parameters (legacy compatibility)
            hourly: List of hourly variables to retrieve
            daily: List of daily variables to retrieve
            timezone: Timezone for the data (default: "auto")
        
        Returns:
            Dictionary containing the historical weather data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "timezone": timezone
        }
        
        # Handle legacy parameters parameter
        if parameters:
            hourly = parameters
        
        if hourly:
            params["hourly"] = ",".join(hourly)
        if daily:
            params["daily"] = ",".join(daily)
        
        response = self.session.get(self.archive_url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_historical_async(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, date],
        end_date: Union[str, date],
        parameters: Optional[List[str]] = None,
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None,
        timezone: str = "auto"
    ) -> Dict:
        """
        Get historical weather data with flexible parameter specification (async version).
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_date: Start date for the historical data
            end_date: End date for the historical data
            parameters: List of hourly parameters (legacy compatibility)
            hourly: List of hourly variables to retrieve
            daily: List of daily variables to retrieve
            timezone: Timezone for the data (default: "auto")
        
        Returns:
            Dictionary containing the historical weather data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "timezone": timezone
        }
        
        # Handle legacy parameters parameter
        if parameters:
            hourly = parameters
        
        if hourly:
            params["hourly"] = ",".join(hourly)
        if daily:
            params["daily"] = ",".join(daily)
        
        client = await self._get_async_client()
        response = await client.get(self.archive_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_archive(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, date],
        end_date: Union[str, date],
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None,
        timezone: str = "auto"
    ) -> Dict:
        """
        Get historical weather data (alias for get_historical).
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_date: Start date for the historical data
            end_date: End date for the historical data
            hourly: List of hourly variables to retrieve
            daily: List of daily variables to retrieve
            timezone: Timezone for the data (default: "auto")
        
        Returns:
            Dictionary containing the historical weather data
        """
        return self.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=hourly,
            daily=daily,
            timezone=timezone
        )
    
    async def get_archive_async(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, date],
        end_date: Union[str, date],
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None,
        timezone: str = "auto"
    ) -> Dict:
        """
        Get historical weather data (async alias for get_historical_async).
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_date: Start date for the historical data
            end_date: End date for the historical data
            hourly: List of hourly variables to retrieve
            daily: List of daily variables to retrieve
            timezone: Timezone for the data (default: "auto")
        
        Returns:
            Dictionary containing the historical weather data
        """
        return await self.get_historical_async(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            hourly=hourly,
            daily=daily,
            timezone=timezone
        )
    
    # Async-aware coordinate methods
    async def get_coordinates_async(self, location: str) -> Tuple[float, float]:
        """Convert city name to coordinates (async version)."""
        # Extract just the city name from formats like "City, State"
        city = location.split(',')[0].strip()
        coords = await self.get_coordinates_detailed_async(city)
        if coords:
            return coords
        raise ValueError(f"Location '{location}' not found")
    
    async def get_coordinates_detailed_async(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a location by name with detailed error handling (async version).
        
        Args:
            location_name: Name of the location
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        results = await self.geocode_async(location_name, count=1)
        if results:
            location = results[0]
            return location["latitude"], location["longitude"]
        return None
    
    # Utility methods for sync/async compatibility
    def run_async(self, coro):
        """Run an async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new event loop
                import threading
                result = None
                exception = None
                
                def run_in_thread():
                    nonlocal result, exception
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result = new_loop.run_until_complete(coro)
                        new_loop.close()
                    except Exception as e:
                        exception = e
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                
                if exception:
                    raise exception
                return result
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(coro)