"""Data models for weather agent."""

from typing import Optional, List, Dict, Any, Literal
from datetime import date
from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    """Represents a geographic location with coordinates."""
    name: str = Field(..., description="Human-readable location name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    country: Optional[str] = Field(None, description="Country name")
    state: Optional[str] = Field(None, description="State or province")
    timezone: Optional[str] = Field(None, description="IANA timezone identifier")


class DateRange(BaseModel):
    """Represents a date range for weather queries."""
    start_date: date = Field(..., description="Start date for the query")
    end_date: date = Field(..., description="End date for the query")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v


class WeatherDataPoint(BaseModel):
    """Dynamic model for Open-Meteo data points."""
    time: Optional[str] = None
    values: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"
    
    def __init__(self, **data):
        # Separate time from other values
        time_val = data.pop('time', None)
        super().__init__(time=time_val, values=data)


class WeatherResponse(BaseModel):
    """Dynamic model for Open-Meteo API responses."""
    latitude: float
    longitude: float
    timezone: Optional[str] = None
    elevation: Optional[float] = None
    hourly: Optional[Dict[str, List[Any]]] = None
    daily: Optional[Dict[str, List[Any]]] = None
    current: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"  # Allow any additional fields from API
    
    def to_structured_data(self) -> List[WeatherDataPoint]:
        """Convert API response to structured data points."""
        data_points = []
        
        # Process daily data if available
        if self.daily and 'time' in self.daily:
            times = self.daily['time']
            for i, time in enumerate(times):
                point_data = {'time': time}
                for key, values in self.daily.items():
                    if key != 'time' and isinstance(values, list) and i < len(values):
                        point_data[key] = values[i]
                data_points.append(WeatherDataPoint(**point_data))
        
        # Process hourly data similarly if needed
        # Process current data if needed
        
        return data_points


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