"""Precipitation data analyzer using Open-Meteo API."""

from typing import Dict, Any, Tuple, List
from datetime import datetime
from .collections import get_parameters_for_analysis


class PrecipitationAnalyzer:
    """Analyzer for Open-Meteo precipitation data."""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_parameters(self) -> List[str]:
        """Get precipitation-related parameters."""
        return get_parameters_for_analysis('precipitation')
    
    def analyze(self, location: Dict[str, Any], time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """
        Analyze precipitation data for water management.
        
        Args:
            location: Dictionary with 'latitude', 'longitude', and optionally 'name'
            time_range: Date range for analysis
            
        Returns:
            Analysis results including rainfall patterns
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
        
        # Get precipitation data
        parameters = self.get_parameters()
        start_date = time_range[0].strftime('%Y-%m-%d')
        end_date = time_range[1].strftime('%Y-%m-%d')
        
        weather_data = self.api_client.get_historical(lat, lon, parameters, start_date, end_date)
        
        if 'error' in weather_data:
            return {'error': weather_data['error']}
        
        # Process results
        results = {
            'analysis_type': 'precipitation',
            'location': {
                'name': location_name,
                'latitude': lat,
                'longitude': lon
            },
            'time_range': {
                'start': start_date,
                'end': end_date
            },
            'data': self._process_precipitation_data(weather_data),
            'insights': self._generate_insights(weather_data, time_range)
        }
        
        return results
    
    def _process_precipitation_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw precipitation data into structured format."""
        daily_data = weather_data.get('daily', {})
        dates = daily_data.get('time', [])
        
        processed = {
            'dates': dates,
            'precipitation_metrics': {}
        }
        
        # Process precipitation parameters
        precip_params = ['precipitation_sum', 'rain_sum', 'showers_sum', 'snowfall_sum']
        for param in precip_params:
            if param in daily_data:
                processed['precipitation_metrics'][param] = daily_data[param]
        
        # Calculate statistics
        if 'precipitation_sum' in daily_data:
            precip_values = [p for p in daily_data['precipitation_sum'] if p is not None]
            
            if precip_values:
                processed['statistics'] = {
                    'total_precipitation': sum(precip_values),
                    'average_daily': sum(precip_values) / len(precip_values),
                    'max_daily': max(precip_values),
                    'days_with_rain': sum(1 for p in precip_values if p > 0.1),
                    'dry_days': sum(1 for p in precip_values if p <= 0.1),
                    'total_days': len(dates)
                }
        
        return processed
    
    def _generate_insights(self, weather_data: Dict[str, Any], time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate precipitation-related insights."""
        insights = []
        daily_data = weather_data.get('daily', {})
        
        # Total precipitation analysis
        if 'precipitation_sum' in daily_data:
            precip_values = [p for p in daily_data['precipitation_sum'] if p is not None]
            total_precip = sum(precip_values)
            days_span = (time_range[1] - time_range[0]).days
            
            if total_precip < 10 and days_span > 14:
                insights.append({
                    'type': 'drought_risk',
                    'message': f'Very low precipitation ({total_precip:.1f}mm) detected',
                    'recommendation': 'Consider irrigation to maintain soil moisture'
                })
            elif total_precip > 100 and days_span <= 7:
                insights.append({
                    'type': 'flood_risk',
                    'message': f'High precipitation ({total_precip:.1f}mm) in short period',
                    'recommendation': 'Monitor field drainage and potential flooding'
                })
        
        # Dry spell analysis
        if 'precipitation_sum' in daily_data:
            precip_values = daily_data['precipitation_sum']
            max_dry_spell = 0
            current_dry_spell = 0
            
            for p in precip_values:
                if p is not None and p <= 0.1:
                    current_dry_spell += 1
                    max_dry_spell = max(max_dry_spell, current_dry_spell)
                else:
                    current_dry_spell = 0
            
            if max_dry_spell > 7:
                insights.append({
                    'type': 'dry_spell',
                    'message': f'Maximum dry spell of {max_dry_spell} days detected',
                    'recommendation': 'Schedule irrigation during extended dry periods'
                })
        
        # Snow analysis
        if 'snowfall_sum' in daily_data:
            snow_values = [s for s in daily_data['snowfall_sum'] if s is not None and s > 0]
            if snow_values:
                insights.append({
                    'type': 'snowfall',
                    'message': f'Snowfall detected on {len(snow_values)} days',
                    'recommendation': 'Account for snow melt in water availability calculations'
                })
        
        return insights