"""
Pydantic models for the advanced MCP weather system.

This module provides comprehensive data models for:
- Weather data structures (forecasts, historical, agricultural)
- Tool inputs and outputs with validation
- Response formats preserving structure
- Metadata and error handling
"""

from .weather import (
    WeatherDataPoint,
    HourlyWeatherData,
    DailyForecast,
    WeatherForecastResponse,
    HistoricalWeatherResponse,
    AgriculturalConditions,
    SoilData,
    LocationInfo,
    Coordinates,
)

from .responses import (
    ToolResponse,
    ResponseMetadata,
    ComposableToolResponse,
    ErrorResponse,
    DataQualityAssessment,
)

from .inputs import (
    ForecastToolInput,
    HistoricalToolInput,
    AgriculturalToolInput,
    WeatherParameter,
    validate_date_range,
)

from .metadata import (
    TemperatureStats,
    PrecipitationSummary,
    ExtremeEvent,
    Trend,
    WeatherAggregations,
)

from .queries import (
    EnhancedQueryClassification,
)

__all__ = [
    # Weather models
    "WeatherDataPoint",
    "HourlyWeatherData",
    "DailyForecast",
    "WeatherForecastResponse",
    "HistoricalWeatherResponse",
    "AgriculturalConditions",
    "SoilData",
    "LocationInfo",
    "Coordinates",
    # Response models
    "ToolResponse",
    "ResponseMetadata",
    "ComposableToolResponse",
    "ErrorResponse",
    "DataQualityAssessment",
    # Input models
    "ForecastToolInput",
    "HistoricalToolInput",
    "AgriculturalToolInput",
    "WeatherParameter",
    "validate_date_range",
    # Metadata models
    "TemperatureStats",
    "PrecipitationSummary",
    "ExtremeEvent",
    "Trend",
    "WeatherAggregations",
    # Query models
    "EnhancedQueryClassification",
]