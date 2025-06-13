"""Open-Meteo API client for weather and climate data."""

import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta


class OpenMeteoClient:
    """Simple client for Open-Meteo weather API."""
    
    def __init__(self):
        """Initialize the Open-Meteo API client."""
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.archive_url = "https://archive-api.open-meteo.com/v1/archive"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.session = requests.Session()
    
    def check_health(self) -> bool:
        """Check if the Open-Meteo API is accessible."""
        try:
            params = {"latitude": 40.7128, "longitude": -74.0060, "current": "temperature_2m"}
            response = self.session.get(self.forecast_url, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
    
    def geocode(self, name: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Convert location name to coordinates.
        
        Args:
            name: Location name to search
            count: Number of results to return
            
        Returns:
            List of location results with lat/lon
        """
        try:
            params = {"name": name, "count": count, "language": "en", "format": "json"}
            response = self.session.get(self.geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.exceptions.RequestException as e:
            return []
    
    def get_weather_data(self, 
                        latitude: float, 
                        longitude: float,
                        parameters: List[str],
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        past_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get weather data from Open-Meteo API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude  
            parameters: List of weather parameters to fetch
            start_date: Start date (YYYY-MM-DD) for historical data
            end_date: End date (YYYY-MM-DD) for historical data
            past_days: Number of past days to include (alternative to dates)
            
        Returns:
            Weather data dictionary
        """
        # Determine which API to use
        if start_date and end_date:
            # Use archive API for historical data
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Archive API has 5-day delay
            five_days_ago = datetime.now() - timedelta(days=5)
            
            if end_dt < five_days_ago:
                url = self.archive_url
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": ",".join(parameters),  # Join parameters with comma
                    "timezone": "auto"
                }
            else:
                # Use forecast API with past_days
                url = self.forecast_url
                days_back = (datetime.now() - start_dt).days
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "past_days": min(days_back, 92),  # Max 92 days
                    "daily": ",".join(parameters),  # Join parameters with comma
                    "timezone": "auto"
                }
        else:
            # Use forecast API
            url = self.forecast_url
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": ",".join(parameters),  # Join parameters with comma
                "timezone": "auto"
            }
            
            if past_days:
                params["past_days"] = past_days
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_forecast(self,
                    latitude: float,
                    longitude: float, 
                    parameters: List[str],
                    past_days: int = 0) -> Dict[str, Any]:
        """
        Get forecast data including optional past days.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            parameters: Weather parameters to fetch
            past_days: Number of past days to include (0-92)
            
        Returns:
            Forecast data dictionary
        """
        return self.get_weather_data(latitude, longitude, parameters, past_days=past_days)
    
    def get_historical(self,
                      latitude: float,
                      longitude: float,
                      parameters: List[str], 
                      start_date: str,
                      end_date: str) -> Dict[str, Any]:
        """
        Get historical weather data.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            parameters: Weather parameters to fetch
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Historical data dictionary
        """
        return self.get_weather_data(latitude, longitude, parameters, start_date, end_date)