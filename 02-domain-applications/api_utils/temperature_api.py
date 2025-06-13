"""Temperature data analyzer using Open-Meteo API."""

from typing import Dict, Any, Tuple, List
from datetime import datetime
from .collections import get_parameters_for_analysis, format_parameter_description


class TemperatureAnalyzer:
    """Analyzer for Open-Meteo temperature data."""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_parameters(self) -> List[str]:
        """Get temperature-related parameters."""
        return get_parameters_for_analysis('temperature')
    
    def analyze(self, location: Dict[str, Any], time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """
        Analyze temperature data for the specified location and time range.
        
        Args:
            location: Dictionary with 'latitude', 'longitude', and optionally 'name'
            time_range: Date range for analysis
            
        Returns:
            Analysis results including temperature data and insights
        """
        # Extract coordinates
        if 'latitude' in location and 'longitude' in location:
            lat = location['latitude']
            lon = location['longitude']
            location_name = location.get('name', f"{lat}, {lon}")
        else:
            # Handle location name
            location_name = location.get('name', 'Unknown')
            geocode_results = self.api_client.geocode(location_name)
            if not geocode_results:
                return {'error': f'Could not find location: {location_name}'}
            lat = geocode_results[0]['latitude']
            lon = geocode_results[0]['longitude']
        
        # Get temperature data
        parameters = self.get_parameters()
        start_date = time_range[0].strftime('%Y-%m-%d')
        end_date = time_range[1].strftime('%Y-%m-%d')
        
        weather_data = self.api_client.get_historical(lat, lon, parameters, start_date, end_date)
        
        if 'error' in weather_data:
            return {'error': weather_data['error']}
        
        # Process results
        results = {
            'analysis_type': 'temperature',
            'location': {
                'name': location_name,
                'latitude': lat,
                'longitude': lon
            },
            'time_range': {
                'start': start_date,
                'end': end_date
            },
            'data': self._process_temperature_data(weather_data),
            'insights': self._generate_insights(weather_data, time_range)
        }
        
        return results
    
    def _process_temperature_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw temperature data into structured format."""
        daily_data = weather_data.get('daily', {})
        dates = daily_data.get('time', [])
        
        processed = {
            'dates': dates,
            'temperature_metrics': {}
        }
        
        # Process air temperature
        temp_params = ['temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean']
        for param in temp_params:
            if param in daily_data:
                processed['temperature_metrics'][param] = daily_data[param]
        
        # Calculate statistics
        if 'temperature_2m_max' in daily_data:
            max_temps = [t for t in daily_data['temperature_2m_max'] if t is not None]
            min_temps = [t for t in daily_data['temperature_2m_min'] if t is not None]
            
            if max_temps and min_temps:
                processed['statistics'] = {
                    'max_temperature': max(max_temps),
                    'min_temperature': min(min_temps),
                    'avg_high': sum(max_temps) / len(max_temps),
                    'avg_low': sum(min_temps) / len(min_temps),
                    'total_days': len(dates)
                }
        
        return processed
    
    def _generate_insights(self, weather_data: Dict[str, Any], time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate temperature-related insights."""
        insights = []
        daily_data = weather_data.get('daily', {})
        
        # Heat stress analysis
        if 'temperature_2m_max' in daily_data:
            max_temps = [t for t in daily_data['temperature_2m_max'] if t is not None]
            heat_stress_days = sum(1 for t in max_temps if t > 32)  # Days above 32°C
            
            if heat_stress_days > 0:
                insights.append({
                    'type': 'heat_stress',
                    'message': f'{heat_stress_days} days with temperatures above 32°C detected',
                    'recommendation': 'Consider heat mitigation strategies during these periods'
                })
        
        # Frost risk analysis  
        if 'temperature_2m_min' in daily_data:
            min_temps = [t for t in daily_data['temperature_2m_min'] if t is not None]
            frost_days = sum(1 for t in min_temps if t < 0)
            
            if frost_days > 0:
                insights.append({
                    'type': 'frost_risk', 
                    'message': f'{frost_days} days with frost risk (below 0°C) detected',
                    'recommendation': 'Plan frost protection measures for sensitive crops'
                })
        
        
        return insights