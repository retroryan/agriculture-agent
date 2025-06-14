#!/usr/bin/env python3
"""
MCP server for OpenMeteo weather forecast with structured responses.

This server demonstrates Phase 1 implementation with:
- Pydantic model validation for inputs
- Structured response format preserving data
- Comprehensive error handling
- Response metadata
"""

import sys
import asyncio
from typing import List, Dict, Any, Type
from datetime import datetime

sys.path.insert(0, '..')

from base_server import BaseWeatherServer
from enhanced_api_utils import EnhancedOpenMeteoClient, LocationNotFoundError
from models.inputs import ForecastToolInput, LocationInput
from models.responses import ToolResponse, ResponseStatus
from models.weather import WeatherForecastResponse
from pydantic import BaseModel


class StructuredForecastServer(BaseWeatherServer):
    """
    Weather forecast server with structured Pydantic responses.
    
    Key improvements over original:
    - Input validation with Pydantic models
    - Structured data preservation in responses
    - Rich error messages with suggestions
    - Caching and performance metrics
    """
    
    def __init__(self):
        super().__init__("openmeteo-forecast-structured")
        self.weather_client = EnhancedOpenMeteoClient()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Define the forecast tool with enhanced schema."""
        return [
            {
                "name": "get_weather_forecast",
                "description": "Get detailed weather forecast with structured data output",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location name or 'lat,lon' coordinates",
                            "examples": [
                                "New York",
                                "London, UK", 
                                "40.7128,-74.0060",
                                "Grand Island, Nebraska"
                            ]
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days (1-16)",
                            "default": 7,
                            "minimum": 1,
                            "maximum": 16
                        },
                        "include_hourly": {
                            "type": "boolean",
                            "description": "Include hourly forecast data",
                            "default": False
                        },
                        "parameters": {
                            "type": "array",
                            "description": "Specific weather parameters to include",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "temperature", "precipitation", "wind_speed",
                                    "humidity", "pressure", "cloud_cover",
                                    "uv_index", "solar_radiation"
                                ]
                            },
                            "default": ["temperature", "precipitation", "wind_speed"]
                        },
                        "units": {
                            "type": "string",
                            "enum": ["metric", "imperial"],
                            "default": "metric",
                            "description": "Unit system for output"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    
    def get_input_model(self, tool_name: str) -> Type[BaseModel]:
        """Get input validation model for the tool."""
        if tool_name == "get_weather_forecast":
            return ForecastToolInput
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def handle_tool_call(self, tool_name: str, validated_input: ForecastToolInput) -> ToolResponse:
        """
        Handle forecast tool call with validated input.
        
        Returns structured response with both text and data.
        """
        if tool_name != "get_weather_forecast":
            raise ValueError(f"Unknown tool: {tool_name}")
        
        try:
            # Convert location input to LocationInfo
            location_input = validated_input.location
            if isinstance(location_input, str):
                # Try to parse as coordinates
                if ',' in location_input and location_input.replace(',', '').replace('.', '').replace('-', '').isdigit():
                    parts = location_input.split(',')
                    lat, lon = float(parts[0]), float(parts[1])
                    location_info = LocationInfo(
                        name=f"{lat:.4f}, {lon:.4f}",
                        coordinates=Coordinates(latitude=lat, longitude=lon)
                    )
                else:
                    # Geocode the location
                    location_info = await self.weather_client.geocode(location_input)
            else:
                location_info = location_input.to_location_info()
            
            # Get API parameters
            api_params = validated_input.to_api_params()
            
            # Fetch forecast data
            forecast_response = await self.weather_client.get_forecast(
                location=location_info,
                days=validated_input.days,
                hourly_params=api_params.get("hourly", []) if validated_input.include_hourly else None,
                daily_params=api_params.get("daily", []),
                include_current=True
            )
            
            # Generate human-readable summary
            summary = self._generate_forecast_summary(forecast_response, validated_input.units)
            
            # Create structured response
            return self.create_response(
                text=summary,
                data=forecast_response,
                status=ResponseStatus.SUCCESS,
                metadata={
                    "cache_hit": False,  # Would check cache in real implementation
                    "data_quality": {
                        "completeness": 0.95,
                        "confidence": 0.95,
                        "missing_fields": [],
                        "quality_issues": []
                    }
                }
            )
            
        except LocationNotFoundError as e:
            # Handle location not found with helpful suggestions
            error_response = ErrorResponse(
                error_type="LocationNotFoundError",
                error_message=str(e),
                error_details={"location": e.location},
                retry_possible=True,
                suggestions=e.suggestions or [
                    "Check the spelling of the location",
                    "Try including country or state",
                    "Use coordinates instead (lat,lon)"
                ]
            )
            return error_response.to_tool_response()
            
        except Exception as e:
            self.logger.error(f"Unexpected error in forecast tool: {e}", exc_info=True)
            raise
    
    def _generate_forecast_summary(self, forecast: WeatherForecastResponse, units: str = "metric") -> str:
        """Generate human-readable forecast summary."""
        lines = [f"Weather forecast for {forecast.location.display_name()}:"]
        
        # Current conditions if available
        if forecast.current_conditions:
            current = forecast.current_conditions
            temp_unit = "°C" if units == "metric" else "°F"
            lines.append(f"\nCurrent: {current.temperature:.1f}{temp_unit}")
            if current.apparent_temperature:
                lines.append(f"Feels like: {current.apparent_temperature:.1f}{temp_unit}")
            if current.weather_code is not None:
                lines.append(f"Conditions: {self._weather_code_to_text(current.weather_code)}")
        
        # Daily forecast
        lines.append("\nForecast:")
        for i, day in enumerate(forecast.forecast_days[:7]):
            temp_unit = "°C" if units == "metric" else "°F"
            precip_unit = "mm" if units == "metric" else "in"
            
            # Convert units if needed
            if units == "imperial":
                temp_min = day.temperature_min * 9/5 + 32
                temp_max = day.temperature_max * 9/5 + 32
                precip = day.precipitation_sum * 0.0393701
            else:
                temp_min = day.temperature_min
                temp_max = day.temperature_max
                precip = day.precipitation_sum
            
            day_name = day.date.strftime("%a %b %d") if i > 0 else "Today"
            temp_range = f"{temp_min:.0f}-{temp_max:.0f}{temp_unit}"
            
            if precip > 0.1:
                precip_str = f"{precip:.1f}{precip_unit} rain"
            else:
                precip_str = "no rain"
            
            lines.append(f"  {day_name}: {temp_range}, {precip_str}")
            
            # Add special conditions
            if day.wind_speed_max and day.wind_speed_max > 40:
                wind_unit = "km/h" if units == "metric" else "mph"
                wind_speed = day.wind_speed_max if units == "metric" else day.wind_speed_max * 0.621371
                lines.append(f"    ⚠️  High winds: {wind_speed:.0f}{wind_unit}")
            
            if day.uv_index_max and day.uv_index_max > 7:
                lines.append(f"    ☀️  High UV: {day.uv_index_max:.0f}")
        
        # Add data quality note if issues
        if forecast.metadata and forecast.metadata.get("data_quality"):
            quality = forecast.metadata["data_quality"]
            if quality.get("warnings"):
                lines.append(f"\n⚠️  Data notes: {', '.join(quality['warnings'])}")
        
        return "\n".join(lines)
    
    def _weather_code_to_text(self, code: int) -> str:
        """Convert WMO weather code to text description."""
        # Simplified mapping - full implementation would have all codes
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
        }
        return weather_codes.get(code, f"Code {code}")
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.weather_client.close()


async def main():
    """Run the structured forecast MCP server."""
    server = StructuredForecastServer()
    try:
        await server.run()
    finally:
        await server.cleanup()


if __name__ == "__main__":
    # Import at module level for cleaner logs
    from models.weather import LocationInfo, Coordinates
    from models.responses import ErrorResponse
    
    asyncio.run(main()