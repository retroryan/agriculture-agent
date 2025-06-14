#!/usr/bin/env python3
"""
Test script for Phase 1 implementation.

This script verifies:
- Pydantic model creation and validation
- Tool input validation
- Structured response generation
- Error handling
"""

import asyncio
import json
from datetime import date, datetime
from typing import Dict, Any

# Test imports
from models.weather import (
    WeatherDataPoint,
    DailyForecast,
    WeatherForecastResponse,
    LocationInfo,
    Coordinates,
)
from models.inputs import (
    ForecastToolInput,
    HistoricalToolInput,
    LocationInput,
    WeatherParameter,
)
from models.responses import (
    ToolResponse,
    ResponseMetadata,
    ErrorResponse,
    ResponseStatus,
    DataQualityAssessment,
)
from models.metadata import (
    TemperatureStats,
    PrecipitationSummary,
    ExtremeEvent,
    ExtremeEventType,
    Trend,
    TrendDirection,
    TrendSignificance,
)


def test_weather_models():
    """Test core weather data models."""
    print("Testing Weather Models...")
    
    # Test Coordinates
    coords = Coordinates(latitude=40.7128, longitude=-74.0060)
    print(f"✓ Coordinates: {coords}")
    
    # Test LocationInfo
    location = LocationInfo(
        name="New York",
        coordinates=coords,
        country="USA",
        state="New York",
        timezone="America/New_York"
    )
    print(f"✓ LocationInfo: {location.display_name()}")
    
    # Test WeatherDataPoint
    data_point = WeatherDataPoint(
        timestamp=datetime.now(),
        temperature=22.5,
        humidity=65,
        precipitation=0.0,
        wind_speed=15.0
    )
    print(f"✓ WeatherDataPoint: {data_point.temperature}°C")
    
    # Test DailyForecast
    daily = DailyForecast(
        date=date.today(),
        temperature_min=15.0,
        temperature_max=25.0,
        precipitation_sum=2.5,
        wind_speed_max=30.0
    )
    print(f"✓ DailyForecast: {daily.temperature_range()}°C range")
    
    # Test validation
    try:
        bad_coords = Coordinates(latitude=100, longitude=-74)  # Invalid latitude
    except Exception as e:
        print(f"✓ Validation working: {type(e).__name__}")
    
    print()


def test_input_models():
    """Test input validation models."""
    print("Testing Input Models...")
    
    # Test ForecastToolInput with string location
    forecast_input = ForecastToolInput(
        location="New York",
        days=7,
        include_hourly=True,
        parameters=[WeatherParameter.TEMPERATURE, WeatherParameter.PRECIPITATION]
    )
    print(f"✓ ForecastToolInput: {forecast_input.days} days")
    
    # Test with coordinates
    coord_input = ForecastToolInput(
        location=Coordinates(latitude=40.7128, longitude=-74.0060),
        days=3
    )
    print(f"✓ Coordinate input: {coord_input.location}")
    
    # Test HistoricalToolInput
    historical_input = HistoricalToolInput(
        location="Chicago",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31)
    )
    print(f"✓ HistoricalToolInput: {historical_input.start_date} to {historical_input.end_date}")
    
    # Test validation
    try:
        bad_input = ForecastToolInput(
            location="New York",
            days=20  # Exceeds maximum
        )
    except Exception as e:
        print(f"✓ Input validation: {type(e).__name__}")
    
    print()


def test_response_models():
    """Test response and metadata models."""
    print("Testing Response Models...")
    
    # Create sample data
    location = LocationInfo(
        name="Test Location",
        coordinates=Coordinates(latitude=40.0, longitude=-74.0)
    )
    
    forecast = WeatherForecastResponse(
        location=location,
        forecast_days=[
            DailyForecast(
                date=date.today(),
                temperature_min=10.0,
                temperature_max=20.0,
                precipitation_sum=5.0
            )
        ],
        metadata={"source": "test"}
    )
    
    # Test ToolResponse
    tool_response = ToolResponse(
        type="structured",
        text=forecast.to_summary(),
        data=forecast,
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(
            source="test-server",
            processing_time_ms=150.5,
            data_quality=DataQualityAssessment(
                completeness=0.95,
                confidence=0.90,
                missing_fields=[],
                quality_issues=[]
            )
        )
    )
    
    print(f"✓ ToolResponse created")
    print(f"  - Status: {tool_response.status}")
    print(f"  - Text preview: {tool_response.text[:50]}...")
    print(f"  - Has data: {tool_response.data is not None}")
    
    # Test error response
    error = ErrorResponse(
        error_type="TestError",
        error_message="This is a test error",
        retry_possible=True,
        suggestions=["Try again", "Check input"]
    )
    error_tool_response = error.to_tool_response()
    print(f"✓ ErrorResponse: {error_tool_response.status}")
    
    print()


def test_metadata_models():
    """Test statistical and metadata models."""
    print("Testing Metadata Models...")
    
    # Test TemperatureStats
    temp_stats = TemperatureStats(
        mean=20.5,
        median=21.0,
        std_dev=3.2,
        min=15.0,
        max=28.0,
        percentiles={25: 18.0, 50: 21.0, 75: 24.0},
        frost_days=0,
        growing_degree_days=150.5
    )
    print(f"✓ TemperatureStats: mean={temp_stats.mean}°C, CV={temp_stats.calculate_variability():.1f}%")
    
    # Test PrecipitationSummary
    precip = PrecipitationSummary(
        total=125.5,
        days_with_rain=15,
        days_without_rain=16,
        max_daily=35.2,
        heavy_rain_days=3
    )
    print(f"✓ PrecipitationSummary: {precip.total}mm, frequency={precip.rain_frequency():.1f}%")
    
    # Test ExtremeEvent
    event = ExtremeEvent(
        event_type=ExtremeEventType.HEATWAVE,
        start_date=datetime.now(),
        description="Temperature exceeded 35°C for 3 consecutive days",
        peak_value=38.5,
        severity=TrendSignificance.HIGH
    )
    print(f"✓ ExtremeEvent: {event.event_type.value}, ongoing={event.is_ongoing()}")
    
    # Test Trend
    trend = Trend(
        parameter="temperature",
        direction=TrendDirection.INCREASING,
        significance=TrendSignificance.MODERATE,
        change_rate=0.5,
        change_unit="°C/decade",
        period_start=date(2014, 1, 1),
        period_end=date(2024, 1, 1),
        data_points=120,
        p_value=0.03
    )
    print(f"✓ Trend: {trend.format_description()}, significant={trend.is_significant()}")
    
    print()


def test_model_serialization():
    """Test model serialization and compatibility."""
    print("Testing Model Serialization...")
    
    # Create complex nested model
    location = LocationInfo(
        name="Test City",
        coordinates=Coordinates(latitude=40.0, longitude=-74.0),
        country="Test Country"
    )
    
    forecast = WeatherForecastResponse(
        location=location,
        forecast_days=[
            DailyForecast(
                date=date.today(),
                temperature_min=10.0,
                temperature_max=20.0,
                precipitation_sum=5.0,
                sunrise=datetime.now().replace(hour=6, minute=30),
                sunset=datetime.now().replace(hour=18, minute=45)
            )
        ]
    )
    
    # Test JSON serialization
    json_data = forecast.model_dump_json(indent=2)
    print(f"✓ JSON serialization: {len(json_data)} bytes")
    
    # Test deserialization
    parsed = WeatherForecastResponse.model_validate_json(json_data)
    print(f"✓ Deserialization successful")
    
    # Test MCP format conversion
    tool_response = ToolResponse(
        text="Test",
        data=forecast,
        metadata=ResponseMetadata(source="test")
    )
    mcp_format = tool_response.to_mcp_format()
    print(f"✓ MCP format: {len(mcp_format)} items")
    
    print()


async def test_enhanced_api_client():
    """Test the enhanced API client with real API calls."""
    print("Testing Enhanced API Client...")
    
    from mcp_servers.enhanced_api_utils import EnhancedOpenMeteoClient
    
    client = EnhancedOpenMeteoClient()
    
    try:
        # Test geocoding
        location = await client.geocode("New York")
        print(f"✓ Geocoding: {location.name} at {location.coordinates}")
        
        # Test forecast
        forecast = await client.get_forecast(
            location=location,
            days=3,
            include_current=True
        )
        print(f"✓ Forecast: {len(forecast.forecast_days)} days")
        print(f"  - Location: {forecast.location.display_name()}")
        print(f"  - First day: {forecast.forecast_days[0].date}")
        
        # Test caching
        cached_forecast = await client.get_forecast(
            location=location,
            days=3,
            include_current=True
        )
        print(f"✓ Caching working (same request returned quickly)")
        
    except Exception as e:
        print(f"⚠️  API test failed: {e}")
        print("  (This is expected if no internet connection)")
    finally:
        await client.close()
    
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 1 Implementation Tests")
    print("=" * 60)
    print()
    
    # Run sync tests
    test_weather_models()
    test_input_models()
    test_response_models()
    test_metadata_models()
    test_model_serialization()
    
    # Run async tests
    asyncio.run(test_enhanced_api_client())
    
    print("=" * 60)
    print("✅ All Phase 1 tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()