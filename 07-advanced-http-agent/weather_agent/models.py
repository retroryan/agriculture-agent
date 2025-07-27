"""
Data models for the weather agent system.

This module contains all Pydantic models used throughout the weather agent,
including structured output models for LangGraph and query classification.
"""

from typing import Optional, List, Any, Dict, Union, Literal
from pydantic import BaseModel, Field, field_validator, validator
from enum import Enum
from datetime import date, datetime
import json


# Structured Output Models for LangGraph
class WeatherCondition(BaseModel):
    """Current weather condition."""
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    feels_like: Optional[float] = Field(None, description="Feels like temperature in Celsius")
    humidity: Optional[int] = Field(None, description="Relative humidity percentage")
    precipitation: Optional[float] = Field(None, description="Current precipitation in mm")
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")
    wind_direction: Optional[float] = Field(None, description="Wind direction in degrees")
    conditions: Optional[Union[str, int]] = Field(None, description="Weather description or code")


class DailyForecast(BaseModel):
    """Daily weather forecast."""
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    max_temperature: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    min_temperature: Optional[float] = Field(None, description="Minimum temperature in Celsius") 
    precipitation: Optional[float] = Field(None, description="Total precipitation in mm")
    conditions: Optional[str] = Field(None, description="Weather conditions summary")


class OpenMeteoResponse(BaseModel):
    """Structured response consolidating Open-Meteo data."""
    location: str = Field(..., description="Location name")
    coordinates: Optional[Any] = Field(None, description="Latitude and longitude")
    timezone: Optional[str] = Field(None, description="Timezone")
    current_conditions: Optional[WeatherCondition] = Field(None, description="Current weather")
    daily_forecast: Optional[List[DailyForecast]] = Field(None, description="Daily forecast data")
    summary: str = Field(..., description="Natural language summary")
    data_source: str = Field(default="Open-Meteo API", description="Data source")


class AgricultureAssessment(BaseModel):
    """Agricultural conditions assessment."""
    location: str = Field(..., description="Location name")
    assessment_date: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat(), description="Assessment date")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    soil_temperature: Optional[float] = Field(None, description="Soil temperature in Celsius")
    soil_moisture: Optional[float] = Field(None, description="Soil moisture content")
    precipitation: Optional[float] = Field(None, description="Precipitation amount")
    evapotranspiration: Optional[float] = Field(None, description="Daily evapotranspiration in mm")
    planting_conditions: str = Field(..., description="Assessment of planting conditions")
    frost_risk: Optional[str] = Field("low", description="Frost risk level")
    growing_degree_days: Optional[float] = Field(None, description="Growing degree days")
    recommendations: List[str] = Field(default_factory=list, description="Farming recommendations")
    data_source: str = Field(default="Open-Meteo Agricultural API", description="Data source")
    summary: str = Field(..., description="Natural language summary")


# Query Classification Models
class QueryType(str, Enum):
    """Types of weather queries."""
    FORECAST = "forecast"
    HISTORICAL = "historical"
    AGRICULTURAL = "agricultural"
    GENERAL = "general"
    COMPARISON = "comparison"
    ALERT = "alert"


class Coordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class LocationInfo(BaseModel):
    """Complete location information including coordinates."""
    raw_location: str = Field(..., description="Original location string from query")
    normalized_name: str = Field(..., description="Normalized location name")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates if determined")
    location_type: str = Field(default="city", description="Type of location (city, region, etc.)")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in location identification")


class TimeRange(BaseModel):
    """Time range for queries."""
    start_date: Optional[str] = Field(None, description="Start date in ISO format")
    end_date: Optional[str] = Field(None, description="End date in ISO format")
    relative_reference: Optional[str] = Field(None, description="Relative time reference (e.g., 'next week')")
    is_historical: bool = Field(False, description="Whether this is a historical query")


class WeatherParameter(str, Enum):
    """Available weather parameters."""
    TEMPERATURE = "temperature"
    PRECIPITATION = "precipitation"
    HUMIDITY = "humidity"
    WIND = "wind"
    PRESSURE = "pressure"
    UV_INDEX = "uv_index"
    VISIBILITY = "visibility"
    GENERAL = "general"
    SOIL_MOISTURE = "soil_moisture"
    EVAPOTRANSPIRATION = "evapotranspiration"
    GROWING_DEGREE_DAYS = "growing_degree_days"


class EnhancedQueryClassification(BaseModel):
    """Enhanced classification of user weather queries."""
    query_type: QueryType = Field(..., description="Type of weather query")
    locations: List[LocationInfo] = Field(..., description="Extracted location information")
    time_range: Optional[TimeRange] = Field(None, description="Time range for the query")
    weather_parameters: List[WeatherParameter] = Field(default_factory=list, description="Specific weather parameters requested")
    intent_summary: str = Field(..., description="Brief summary of user intent")
    requires_clarification: bool = Field(False, description="Whether the query needs clarification")
    clarification_reason: Optional[str] = Field(None, description="Reason why clarification is needed")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Overall confidence in classification")


# Legacy models for backward compatibility
class QueryClassification(BaseModel):
    """Result of Claude's query classification."""
    query_type: Literal["forecast", "historical", "agricultural", "general"] = Field(
        ...,
        description="Type of weather query"
    )
    locations: List[str] = Field(
        default_factory=list,
        description="Extracted location references"
    )
    time_references: List[str] = Field(
        default_factory=list,
        description="Extracted time references"
    )
    parameters: List[str] = Field(
        default_factory=list,
        description="Weather parameters mentioned or implied"
    )
    requires_clarification: bool = Field(
        False,
        description="Whether the query needs clarification"
    )
    clarification_message: Optional[str] = Field(
        None,
        description="Message to show user if clarification needed"
    )


# Tool Response Models
class ToolResponse(BaseModel):
    """Base model for all tool responses."""
    tool_name: str = Field(..., description="Name of the tool that generated this response")
    success: bool = Field(True, description="Whether the tool call succeeded")
    error: Optional[str] = Field(None, description="Error message if call failed")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw response data")


class WeatherForecastResponse(ToolResponse):
    """Response from get_weather_forecast tool."""
    location: Optional[Dict[str, Any]] = Field(None, description="Location information")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Lat/lon coordinates")
    timezone: Optional[str] = Field(None, description="Timezone")
    current: Optional[Dict[str, Any]] = Field(None, description="Current weather data")
    daily: Optional[Dict[str, Any]] = Field(None, description="Daily forecast data")
    
    @validator('location', pre=True)
    def normalize_location(cls, v):
        """Handle location being either a string or dict."""
        if isinstance(v, str):
            return {"name": v}
        return v


class HistoricalWeatherResponse(ToolResponse):
    """Response from get_historical_weather tool."""
    location: Optional[str] = Field(None, description="Location name")
    date_range: Optional[Dict[str, str]] = Field(None, description="Start and end dates")
    daily: Optional[Dict[str, List[Any]]] = Field(None, description="Historical daily data")


class AgriculturalConditionsResponse(ToolResponse):
    """Response from get_agricultural_conditions tool."""
    location: Optional[str] = Field(None, description="Location name")
    assessment_date: Optional[str] = Field(None, description="Date of assessment")
    temperature: Optional[float] = Field(None, description="Current temperature")
    soil_temperature_0_to_10cm: Optional[float] = Field(None, description="Soil temperature")
    soil_moisture_0_to_10cm: Optional[float] = Field(None, description="Soil moisture")
    precipitation: Optional[float] = Field(None, description="Precipitation amount")
    evapotranspiration: Optional[float] = Field(None, description="Evapotranspiration rate")
    conditions: Optional[str] = Field(None, description="Overall conditions")
    frost_risk: Optional[str] = Field(None, description="Frost risk level")
    growing_degree_days: Optional[float] = Field(None, description="Growing degree days")
    recommendations: Optional[List[str]] = Field(None, description="Agricultural recommendations")
    crop_recommendations: Optional[List[str]] = Field(None, description="Crop-specific recommendations")


class ToolCallInfo(BaseModel):
    """Information about a tool call made by the agent."""
    tool_name: str = Field(..., description="Name of the tool called")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments passed to the tool")
    call_id: Optional[str] = Field(None, description="Unique ID of the tool call")


class ConversationState(BaseModel):
    """Clean representation of conversation state with tool responses."""
    thread_id: str = Field(..., description="Conversation thread ID")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    tool_calls: List[ToolCallInfo] = Field(default_factory=list, description="Tool calls made")
    tool_responses: List[ToolResponse] = Field(default_factory=list, description="Parsed tool responses")
    
    def get_tool_response(self, tool_name: str) -> Optional[ToolResponse]:
        """Get the most recent response for a specific tool."""
        for response in reversed(self.tool_responses):
            if response.tool_name == tool_name:
                return response
        return None
    
    def get_all_tool_responses(self, tool_name: str) -> List[ToolResponse]:
        """Get all responses for a specific tool."""
        return [r for r in self.tool_responses if r.tool_name == tool_name]


# Helper functions
def parse_tool_content(content: Any) -> Dict[str, Any]:
    """
    Parse tool content from LangGraph ToolMessage.
    
    LangGraph serializes tool responses as JSON strings, so we need to handle:
    1. String content that is JSON
    2. Dict content (shouldn't happen with MCP, but handle it)
    3. Other content types
    """
    if isinstance(content, str):
        # Try to parse as JSON
        content = content.strip()
        if content.startswith('{') and content.endswith('}'):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Not valid JSON, return as raw
                return {"raw_response": content}
        else:
            # Not JSON format
            return {"raw_response": content}
    elif isinstance(content, dict):
        # Already a dict (shouldn't happen with MCP tools, but handle it)
        return content
    else:
        # Other types - convert to string
        return {"raw_response": str(content)}


def create_tool_response(tool_name: str, content: Any) -> ToolResponse:
    """
    Create an appropriate ToolResponse object based on tool name and content.
    
    Args:
        tool_name: Name of the tool that generated the response
        content: Raw content from ToolMessage (usually a JSON string)
    
    Returns:
        Appropriate ToolResponse subclass instance
    """
    # Parse the content
    try:
        data = parse_tool_content(content)
        
        # Create appropriate response model based on tool name
        if tool_name == "get_weather_forecast":
            return WeatherForecastResponse(
                tool_name=tool_name,
                raw_response=data,
                **data
            )
        elif tool_name == "get_historical_weather":
            return HistoricalWeatherResponse(
                tool_name=tool_name,
                raw_response=data,
                **data
            )
        elif tool_name == "get_agricultural_conditions":
            # Handle both possible recommendation field names
            if "crop_recommendations" in data and "recommendations" not in data:
                data["recommendations"] = data["crop_recommendations"]
            return AgriculturalConditionsResponse(
                tool_name=tool_name,
                raw_response=data,
                **data
            )
        else:
            # Unknown tool - use base class
            return ToolResponse(
                tool_name=tool_name,
                raw_response=data
            )
    
    except Exception as e:
        # Error parsing - create error response
        return ToolResponse(
            tool_name=tool_name,
            success=False,
            error=str(e),
            raw_response={"error": str(e), "original_content": str(content)}
        )