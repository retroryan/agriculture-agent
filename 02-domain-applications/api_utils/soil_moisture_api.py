"""Soil moisture data analyzer using Open-Meteo API."""

from typing import Dict, Any, Tuple, List
from datetime import datetime
from .collections import get_parameters_for_analysis


class SoilMoistureAnalyzer:
    """Analyzer for Open-Meteo soil moisture data."""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_parameters(self) -> List[str]:
        """Get soil moisture-related parameters."""
        return get_parameters_for_analysis('soil_moisture')
    
    def analyze(self, location: Dict[str, Any], time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """
        Analyze soil moisture data for irrigation management.
        
        Args:
            location: Dictionary with 'latitude', 'longitude', and optionally 'name'
            time_range: Date range for analysis
            
        Returns:
            Analysis results including moisture levels and insights
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
        
        # Get soil moisture data
        parameters = self.get_parameters()
        start_date = time_range[0].strftime('%Y-%m-%d')
        end_date = time_range[1].strftime('%Y-%m-%d')
        
        weather_data = self.api_client.get_historical(lat, lon, parameters, start_date, end_date)
        
        if 'error' in weather_data:
            return {'error': weather_data['error']}
        
        # Process results
        results = {
            'analysis_type': 'soil_moisture',
            'location': {
                'name': location_name,
                'latitude': lat,
                'longitude': lon
            },
            'time_range': {
                'start': start_date,
                'end': end_date
            },
            'data': self._process_soil_moisture_data(weather_data),
            'insights': self._generate_insights(weather_data, time_range)
        }
        
        return results
    
    def _process_soil_moisture_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw soil moisture data into structured format."""
        daily_data = weather_data.get('daily', {})
        dates = daily_data.get('time', [])
        
        processed = {
            'dates': dates,
            'soil_moisture_layers': {}
        }
        
        # Define soil moisture layers with depth ranges
        layer_definitions = {
            'soil_moisture_0_to_1cm': 'Surface (0-1cm)',
            'soil_moisture_1_to_3cm': 'Near surface (1-3cm)',
            'soil_moisture_3_to_9cm': 'Shallow root (3-9cm)',
            'soil_moisture_9_to_27cm': 'Root zone (9-27cm)',
            'soil_moisture_27_to_81cm': 'Deep root (27-81cm)'
        }
        
        # Process each soil moisture layer
        for param, description in layer_definitions.items():
            if param in daily_data:
                values = daily_data[param]
                non_null_values = [v for v in values if v is not None]
                
                if non_null_values:
                    processed['soil_moisture_layers'][param] = {
                        'description': description,
                        'values': values,
                        'average': sum(non_null_values) / len(non_null_values),
                        'min': min(non_null_values),
                        'max': max(non_null_values)
                    }
        
        # Calculate overall statistics
        if processed['soil_moisture_layers']:
            processed['statistics'] = {
                'total_days': len(dates),
                'layers_available': len(processed['soil_moisture_layers'])
            }
        
        return processed
    
    def _generate_insights(self, weather_data: Dict[str, Any], time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate soil moisture-related insights."""
        insights = []
        daily_data = weather_data.get('daily', {})
        
        # Surface moisture for germination
        if 'soil_moisture_0_to_1cm' in daily_data:
            surface_values = [v for v in daily_data['soil_moisture_0_to_1cm'] if v is not None]
            if surface_values:
                avg_surface = sum(surface_values) / len(surface_values)
                
                if avg_surface < 0.15:
                    insights.append({
                        'type': 'germination_risk',
                        'message': f'Low surface moisture ({avg_surface:.2f} m³/m³) may affect germination',
                        'recommendation': 'Consider irrigation before planting'
                    })
                elif avg_surface > 0.35:
                    insights.append({
                        'type': 'saturation_risk',
                        'message': f'High surface moisture ({avg_surface:.2f} m³/m³) detected',
                        'recommendation': 'Delay field operations to avoid compaction'
                    })
        
        # Root zone moisture
        if 'soil_moisture_9_to_27cm' in daily_data:
            root_values = [v for v in daily_data['soil_moisture_9_to_27cm'] if v is not None]
            if root_values:
                avg_root = sum(root_values) / len(root_values)
                
                if avg_root < 0.20:
                    insights.append({
                        'type': 'irrigation_needed',
                        'message': f'Root zone moisture below optimal ({avg_root:.2f} m³/m³)',
                        'recommendation': 'Schedule irrigation to maintain crop health'
                    })
        
        # Deep moisture reserves
        if 'soil_moisture_27_to_81cm' in daily_data:
            deep_values = [v for v in daily_data['soil_moisture_27_to_81cm'] if v is not None]
            if deep_values:
                avg_deep = sum(deep_values) / len(deep_values)
                
                insights.append({
                    'type': 'water_reserves',
                    'message': f'Deep soil moisture at {avg_deep:.2f} m³/m³',
                    'recommendation': 'Monitor deep reserves for drought resilience'
                })
        
        # Layer comparison
        if len(daily_data) > 3:
            insights.append({
                'type': 'multi_layer',
                'message': 'Soil moisture data available at multiple depths',
                'recommendation': 'Use profile data to optimize irrigation depth and timing'
            })
        
        return insights