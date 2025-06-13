# Stage 05: Advanced MCP - Production-Ready Weather Agents

## Tutorial Overview

Welcome to Stage 05 of our weather data tutorial series! In Stage 04, we built a basic MCP (Model Context Protocol) architecture with specialized weather agents. While functional, that implementation had several limitations that prevent it from being production-ready.

In this tutorial, we'll transform our weather agents into a robust, flexible system that can handle real-world requirements. You'll learn:

- How to identify and fix architectural limitations
- Dynamic location handling without hard-coded restrictions
- Leveraging Claude's native tool-calling capabilities
- Building production-ready error handling and validation
- Creating reusable patterns for MCP servers

## Prerequisites

- Completed Stage 04: MCP Multi-Agent Architecture
- Understanding of MCP servers and LangGraph agents
- Basic knowledge of Pydantic and type hints
- Familiarity with Claude's capabilities

## Part 1: Analyzing Stage 04's Limitations

Let's start by examining the current implementation to understand what needs improvement.

### Problem 1: Hard-Coded Location Restrictions

Open `04-mcp-architecture/mcp_servers/forecast_server.py` and look at the tool definition:

```python
"location": {
    "type": "string",
    "enum": [
        "Grand Island, Nebraska",
        "Scottsbluff, Nebraska",
        "Ames, Iowa",
        "Cedar Rapids, Iowa",
        "Fresno, California",
        "Salinas, California",
        "Lubbock, Texas",
        "Amarillo, Texas"
    ],
    "description": "Agricultural location to check"
}
```

**Why is this a problem?**
- Users can only query weather for 8 pre-defined locations
- Adding new locations requires code changes and redeployment
- The system has a geocoding API but doesn't use it effectively
- Real users want weather for their specific locations

### Problem 2: Fragile JSON Parsing

Look at `04-mcp-architecture/weather_agent/claude_integration.py`:

```python
prompt = f"""...
Return ONLY valid JSON."""

try:
    message = self.client.messages.create(...)
    result = json.loads(message.content[0].text)  # Fragile!
```

**Why is this a problem?**
- JSON parsing can fail if Claude's response format varies slightly
- No schema validation or type safety
- Error handling is all-or-nothing
- Doesn't leverage Claude's native tool-calling capabilities

### Problem 3: Redundant Location Management

Locations are managed in multiple places:
- Hard-coded in each MCP server
- Duplicated in `claude_integration.py` as KNOWN_LOCATIONS
- The geocoding API exists but is underutilized

**Why is this a problem?**
- Violates DRY (Don't Repeat Yourself) principle
- Maintenance nightmare when adding/updating locations
- Inconsistencies between different parts of the system

### Problem 4: Limited Error Handling

The current system has basic try-catch blocks but lacks:
- Graceful degradation for partial failures
- Helpful error messages for users
- Retry logic for transient failures
- Proper logging for debugging

## Part 2: Building Stage 05 - Advanced MCP

Let's create a new, improved architecture that addresses all these issues.

### Step 1: Project Structure

First, create the new directory structure:

```bash
mkdir -p 05-advanced-mcp/{mcp_servers,agents,tools,services,tests}
cd 05-advanced-mcp
```

Our improved structure:
```
05-advanced-mcp/
├── mcp_servers/           # Enhanced MCP servers
│   ├── base.py           # Base class for all servers
│   ├── forecast.py        # Dynamic forecast server
│   ├── historical.py      # Dynamic historical server
│   └── agricultural.py    # Dynamic agricultural server
├── agents/                # Improved agents
│   ├── orchestrator.py    # Main orchestrator
│   └── weather_analyst.py # Claude-powered analyst
├── tools/                 # Pydantic tool definitions
│   ├── location_tools.py  # Location extraction tools
│   └── query_tools.py     # Query analysis tools
├── services/              # Shared services
│   ├── location.py        # Centralized location service
│   └── cache.py           # Caching service
├── tests/                 # Comprehensive tests
└── main.py               # Entry point
```

### Step 2: Building a Robust Location Service

Create `services/location.py`:

```python
"""
Centralized location service for weather queries.

This service handles all location-related operations:
- Geocoding (location name to coordinates)
- Reverse geocoding (coordinates to location name)
- Location validation and normalization
- Caching for performance
"""

from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
import re
from functools import lru_cache

# Import from the existing project
import sys
sys.path.append('..')
from mcp_servers.api_utils import OpenMeteoClient


@dataclass
class Location:
    """Represents a resolved location with metadata."""
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    state: Optional[str] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API calls."""
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country,
            "state": self.state
        }


class LocationService:
    """
    Centralized service for all location operations.
    
    Features:
    - Smart geocoding with fallbacks
    - Coordinate validation
    - Format normalization
    - Performance caching
    """
    
    def __init__(self):
        self.client = OpenMeteoClient()
        
    @lru_cache(maxsize=1000)
    def resolve_location(self, location_input: str) -> Location:
        """
        Resolve any location string to coordinates.
        
        Supports:
        - City names: "New York", "London"
        - City, State: "Austin, Texas", "Paris, France"
        - Landmarks: "Eiffel Tower", "Central Park"
        - Coordinates: "40.7128, -74.0060"
        - ZIP codes: "10001" (US only for now)
        """
        
        # First, check if it's coordinates
        coords = self._parse_coordinates(location_input)
        if coords:
            return self.resolve_coordinates(*coords)
        
        # Try geocoding with the API
        try:
            results = self.client.geocode(location_input, count=3)
            if results:
                # Use the first result but validate it makes sense
                best_result = self._select_best_result(results, location_input)
                return Location(
                    name=self._format_location_name(best_result),
                    latitude=best_result["latitude"],
                    longitude=best_result["longitude"],
                    country=best_result.get("country"),
                    state=best_result.get("admin1"),
                    confidence=self._calculate_confidence(best_result, location_input)
                )
        except Exception as e:
            # Log the error but don't fail yet
            print(f"Geocoding error for '{location_input}': {e}")
        
        # If all else fails, try fuzzy matching against known locations
        # This provides a fallback for common misspellings
        known_location = self._fuzzy_match_known_location(location_input)
        if known_location:
            return known_location
        
        raise ValueError(
            f"Could not resolve location '{location_input}'. "
            f"Try being more specific (e.g., 'Paris, France' instead of 'Paris')"
        )
    
    def resolve_coordinates(self, lat: float, lon: float) -> Location:
        """
        Reverse geocode coordinates to a location.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            
        Returns:
            Location object with resolved name
        """
        # Validate coordinates
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude: {lon}")
        
        # For now, return a formatted coordinate location
        # In production, you'd use a reverse geocoding API
        return Location(
            name=f"{lat:.2f}°{'N' if lat >= 0 else 'S'}, "
                 f"{abs(lon):.2f}°{'E' if lon >= 0 else 'W'}",
            latitude=lat,
            longitude=lon,
            confidence=1.0
        )
    
    def _parse_coordinates(self, input_str: str) -> Optional[Tuple[float, float]]:
        """Parse coordinate strings like '40.7, -74.0' or '40.7,-74.0'."""
        # Match patterns like: 40.7, -74.0 or 40.7,-74.0 or 40.7 -74.0
        coord_pattern = r'^\s*(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)\s*$'
        match = re.match(coord_pattern, input_str.strip())
        
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except ValueError:
                pass
        
        return None
    
    def _select_best_result(self, results: List[Dict], query: str) -> Dict:
        """Select the most relevant result from geocoding results."""
        # Simple heuristic: prefer results that match more of the query
        query_lower = query.lower()
        best_score = -1
        best_result = results[0]
        
        for result in results:
            score = 0
            name = result.get("name", "").lower()
            country = result.get("country", "").lower()
            admin1 = result.get("admin1", "").lower()
            
            # Score based on matches
            if name in query_lower or query_lower in name:
                score += 3
            if country and (country in query_lower or query_lower in country):
                score += 2
            if admin1 and (admin1 in query_lower or query_lower in admin1):
                score += 1
            
            if score > best_score:
                best_score = score
                best_result = result
        
        return best_result
    
    def _format_location_name(self, result: Dict) -> str:
        """Format a geocoding result into a readable name."""
        parts = []
        
        if result.get("name"):
            parts.append(result["name"])
        
        if result.get("admin1") and result["admin1"] != result.get("name"):
            parts.append(result["admin1"])
        
        if result.get("country"):
            parts.append(result["country"])
        
        return ", ".join(parts) or "Unknown Location"
    
    def _calculate_confidence(self, result: Dict, query: str) -> float:
        """Calculate confidence score for a geocoding result."""
        # Simple confidence based on how well the result matches the query
        query_lower = query.lower()
        result_str = f"{result.get('name', '')} {result.get('admin1', '')} {result.get('country', '')}".lower()
        
        # Calculate word overlap
        query_words = set(query_lower.split())
        result_words = set(result_str.split())
        
        if not query_words:
            return 0.5
        
        overlap = len(query_words & result_words) / len(query_words)
        return min(0.95, 0.5 + overlap * 0.45)
    
    def _fuzzy_match_known_location(self, query: str) -> Optional[Location]:
        """Fallback to known locations for common queries."""
        # This could be expanded with a proper fuzzy matching library
        known_locations = {
            "nyc": Location("New York City, NY", 40.7128, -74.0060),
            "sf": Location("San Francisco, CA", 37.7749, -122.4194),
            "la": Location("Los Angeles, CA", 34.0522, -118.2437),
            "london": Location("London, UK", 51.5074, -0.1278),
            "paris": Location("Paris, France", 48.8566, 2.3522),
            "tokyo": Location("Tokyo, Japan", 35.6762, 139.6503),
        }
        
        query_lower = query.lower().strip()
        return known_locations.get(query_lower)
```

### Step 3: Claude Tool Integration

Create `tools/location_tools.py`:

```python
"""
Pydantic models for Claude's tool use.

These models define structured inputs/outputs that Claude can use
to extract information from queries in a type-safe way.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class LocationExtraction(BaseModel):
    """Extract location information from a user query."""
    
    location_mentioned: bool = Field(
        description="Whether any location is mentioned in the query"
    )
    
    location_text: Optional[str] = Field(
        default=None,
        description="The location as mentioned in the query (e.g., 'New York', 'Paris, France')"
    )
    
    has_coordinates: bool = Field(
        default=False,
        description="Whether the query contains latitude/longitude coordinates"
    )
    
    latitude: Optional[float] = Field(
        default=None,
        description="Latitude if coordinates are provided"
    )
    
    longitude: Optional[float] = Field(
        default=None,
        description="Longitude if coordinates are provided"
    )
    
    location_type: Optional[Literal["city", "region", "coordinates", "landmark"]] = Field(
        default=None,
        description="Type of location reference"
    )


class TimeRangeExtraction(BaseModel):
    """Extract time range information from a query."""
    
    has_time_reference: bool = Field(
        description="Whether any time reference is mentioned"
    )
    
    time_type: Optional[Literal["specific_date", "date_range", "relative", "none"]] = Field(
        default="none",
        description="Type of time reference"
    )
    
    start_date: Optional[str] = Field(
        default=None,
        description="Start date in YYYY-MM-DD format or relative description"
    )
    
    end_date: Optional[str] = Field(
        default=None,
        description="End date in YYYY-MM-DD format or relative description"
    )
    
    relative_description: Optional[str] = Field(
        default=None,
        description="Relative time description (e.g., 'next week', 'last month')"
    )


class QueryAnalysis(BaseModel):
    """Complete analysis of a weather query."""
    
    query_intent: List[Literal["forecast", "historical", "agricultural", "comparison"]] = Field(
        description="The types of weather information requested"
    )
    
    weather_parameters: List[str] = Field(
        default_factory=list,
        description="Weather parameters mentioned (temperature, precipitation, wind, etc.)"
    )
    
    agricultural_focus: Optional[List[str]] = Field(
        default=None,
        description="Agricultural aspects mentioned (crops, irrigation, planting, etc.)"
    )
    
    requires_detailed_analysis: bool = Field(
        default=False,
        description="Whether the query requires in-depth analysis or simple data"
    )
    
    urgency_level: Literal["immediate", "planning", "research"] = Field(
        default="planning",
        description="How time-sensitive the information need is"
    )
```

Create `tools/query_tools.py`:

```python
"""
Tools for query analysis using Claude's native capabilities.
"""

from langchain_core.tools import tool
from typing import Dict, Any
from .location_tools import LocationExtraction, TimeRangeExtraction, QueryAnalysis


@tool
def extract_location_from_query(query: str) -> LocationExtraction:
    """
    Extract location information from a weather query.
    
    Examples:
    - "What's the weather in Paris?" -> location_text="Paris"
    - "Temperature at 40.7, -74.0" -> has_coordinates=True, latitude=40.7, longitude=-74.0
    - "Will it rain tomorrow?" -> location_mentioned=False
    """
    # This is a tool signature that Claude will implement
    pass


@tool
def extract_time_range_from_query(query: str) -> TimeRangeExtraction:
    """
    Extract time range information from a weather query.
    
    Examples:
    - "Weather next week" -> time_type="relative", relative_description="next week"
    - "Temperature on March 15" -> time_type="specific_date", start_date="2024-03-15"
    - "Historical data from Jan to Mar" -> time_type="date_range"
    """
    pass


@tool
def analyze_weather_query(query: str, location: LocationExtraction, time_range: TimeRangeExtraction) -> QueryAnalysis:
    """
    Perform comprehensive analysis of a weather query.
    
    Consider the query intent, required parameters, and any special requirements.
    """
    pass
```

### Step 4: Enhanced MCP Server Base Class

Create `mcp_servers/base.py`:

```python
"""
Base class for all MCP weather servers.

Provides common functionality:
- Dynamic location handling
- Error handling and validation
- Consistent response formatting
- Performance monitoring
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
import time
import logging
from datetime import datetime

# Import our enhanced services
import sys
sys.path.append('..')
from services.location import LocationService, Location
from mcp_servers.api_utils import OpenMeteoClient


class WeatherMCPServer(ABC):
    """
    Base class for weather MCP servers with production-ready features.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.app = Server(name)
        self.location_service = LocationService()
        self.weather_client = OpenMeteoClient()
        self.logger = self._setup_logging()
        
        # Setup MCP handlers
        self._setup_handlers()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for this server."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Add handler if not already present
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.name}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers."""
        
        @self.app.list_tools()
        async def list_tools():
            """List available tools for this server."""
            return self.get_tools()
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Execute a tool with comprehensive error handling."""
            start_time = time.time()
            
            try:
                # Validate tool exists
                tool_names = [tool["name"] for tool in self.get_tools()]
                if name not in tool_names:
                    raise ValueError(f"Unknown tool: {name}")
                
                # Resolve location if present in arguments
                location = await self._resolve_location(arguments)
                
                # Log the request
                self.logger.info(
                    f"Tool: {name}, "
                    f"Location: {location.name if location else 'None'}, "
                    f"Args: {arguments}"
                )
                
                # Execute the specific tool
                result = await self.execute_tool(name, arguments, location)
                
                # Add metadata to response
                duration = time.time() - start_time
                response = {
                    "result": result,
                    "metadata": {
                        "duration_ms": round(duration * 1000, 2),
                        "timestamp": datetime.utcnow().isoformat(),
                        "location": location.to_dict() if location else None
                    }
                }
                
                self.logger.info(f"Tool {name} completed in {duration:.2f}s")
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(f"Tool {name} failed: {str(e)}")
                
                # Return structured error response
                return {
                    "error": {
                        "message": str(e),
                        "tool": name,
                        "duration_ms": round(duration * 1000, 2)
                    }
                }
    
    async def _resolve_location(self, arguments: dict) -> Optional[Location]:
        """
        Resolve location from arguments with multiple strategies.
        """
        # Strategy 1: Explicit coordinates
        if "latitude" in arguments and "longitude" in arguments:
            try:
                return self.location_service.resolve_coordinates(
                    arguments["latitude"],
                    arguments["longitude"]
                )
            except ValueError as e:
                self.logger.warning(f"Invalid coordinates: {e}")
        
        # Strategy 2: Location name
        if "location" in arguments and arguments["location"]:
            try:
                return self.location_service.resolve_location(arguments["location"])
            except ValueError as e:
                self.logger.warning(f"Could not resolve location: {e}")
        
        # Strategy 3: Return None (let specific tool decide on default)
        return None
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define the tools available in this server.
        
        Must return a list of tool definitions with:
        - name: Tool identifier
        - description: What the tool does
        - inputSchema: JSON Schema for parameters
        """
        pass
    
    @abstractmethod
    async def execute_tool(self, name: str, arguments: dict, location: Optional[Location]) -> Any:
        """
        Execute a specific tool.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            location: Resolved location (if applicable)
            
        Returns:
            Tool result (will be wrapped in response metadata)
        """
        pass
    
    def create_location_schema(self, required: bool = True) -> Dict[str, Any]:
        """
        Create a reusable location schema for tool inputs.
        
        This provides a consistent way to specify location across all tools.
        """
        schema = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location name (e.g., 'New York, NY', 'London, UK', 'Tokyo')"
                },
                "latitude": {
                    "type": "number",
                    "description": "Latitude (-90 to 90)",
                    "minimum": -90,
                    "maximum": 90
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude (-180 to 180)",
                    "minimum": -180,
                    "maximum": 180
                }
            }
        }
        
        if required:
            # Require either location name OR coordinates
            schema["oneOf"] = [
                {"required": ["location"]},
                {"required": ["latitude", "longitude"]}
            ]
        
        return schema
```

### Step 5: Enhanced Forecast Server

Create `mcp_servers/forecast.py`:

```python
#!/usr/bin/env python3
"""
Enhanced forecast MCP server with dynamic location support.
"""

import sys
sys.path.append('..')

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from mcp.server.stdio import stdio_server
from .base import WeatherMCPServer
from services.location import Location


class ForecastServer(WeatherMCPServer):
    """
    MCP server for weather forecasts with production features:
    - Dynamic location support (any location worldwide)
    - Multiple forecast ranges
    - Detailed agricultural parameters
    - Smart defaults and error handling
    """
    
    def __init__(self):
        super().__init__(
            name="advanced-forecast-server",
            description="Advanced weather forecast server with global coverage"
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Define available forecast tools."""
        
        # Create base location schema
        location_schema = self.create_location_schema(required=False)
        
        return [
            {
                "name": "get_forecast",
                "description": "Get weather forecast for any location worldwide",
                "inputSchema": {
                    **location_schema,
                    "properties": {
                        **location_schema["properties"],
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
                            "description": "Specific parameters to include",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "temperature", "precipitation", "wind", 
                                    "humidity", "pressure", "cloudcover",
                                    "solar_radiation", "uv_index", "visibility"
                                ]
                            }
                        }
                    }
                }
            },
            {
                "name": "get_agricultural_forecast",
                "description": "Get specialized agricultural forecast with crop-relevant data",
                "inputSchema": {
                    **location_schema,
                    "properties": {
                        **location_schema["properties"],
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (corn, wheat, soybeans, etc.)",
                            "default": "general"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Forecast days (1-16)",
                            "default": 7,
                            "minimum": 1,
                            "maximum": 16
                        },
                        "include_soil": {
                            "type": "boolean",
                            "description": "Include soil temperature and moisture",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "get_alerts",
                "description": "Get weather alerts and warnings for a location",
                "inputSchema": location_schema
            }
        ]
    
    async def execute_tool(self, name: str, arguments: dict, location: Optional[Location]) -> Any:
        """Execute forecast tools with enhanced functionality."""
        
        # Default to a central location if none provided
        if not location:
            self.logger.info("No location provided, using default (Des Moines, IA)")
            location = Location(
                name="Des Moines, IA",
                latitude=41.5868,
                longitude=-93.6250
            )
        
        if name == "get_forecast":
            return await self._get_forecast(arguments, location)
        elif name == "get_agricultural_forecast":
            return await self._get_agricultural_forecast(arguments, location)
        elif name == "get_alerts":
            return await self._get_alerts(location)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _get_forecast(self, arguments: dict, location: Location) -> str:
        """Get standard weather forecast."""
        days = arguments.get("days", 7)
        include_hourly = arguments.get("include_hourly", False)
        parameters = arguments.get("parameters", ["temperature", "precipitation"])
        
        # Build parameter list based on request
        daily_params = []
        hourly_params = []
        
        param_mapping = {
            "temperature": {
                "daily": ["temperature_2m_max", "temperature_2m_min"],
                "hourly": ["temperature_2m"]
            },
            "precipitation": {
                "daily": ["precipitation_sum", "precipitation_probability_max"],
                "hourly": ["precipitation", "precipitation_probability"]
            },
            "wind": {
                "daily": ["wind_speed_10m_max", "wind_direction_10m_dominant"],
                "hourly": ["wind_speed_10m", "wind_direction_10m"]
            },
            "humidity": {
                "daily": ["relative_humidity_2m_mean"],
                "hourly": ["relative_humidity_2m"]
            },
            "pressure": {
                "daily": ["surface_pressure_mean"],
                "hourly": ["surface_pressure"]
            }
        }
        
        # Build parameter lists
        for param in parameters:
            if param in param_mapping:
                daily_params.extend(param_mapping[param]["daily"])
                if include_hourly:
                    hourly_params.extend(param_mapping[param]["hourly"])
        
        # Always include time
        daily_params.append("time")
        if include_hourly:
            hourly_params.append("time")
        
        try:
            # Get forecast data
            forecast_data = self.weather_client.get_forecast(
                latitude=location.latitude,
                longitude=location.longitude,
                daily=daily_params,
                hourly=hourly_params if include_hourly else None,
                forecast_days=days,
                timezone="auto"
            )
            
            # Format response
            result = self._format_forecast_response(
                forecast_data, 
                location, 
                days,
                include_hourly
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Forecast API error: {e}")
            return f"Error getting forecast for {location.name}: Weather service temporarily unavailable"
    
    async def _get_agricultural_forecast(self, arguments: dict, location: Location) -> str:
        """Get agricultural-specific forecast."""
        crop_type = arguments.get("crop_type", "general")
        days = arguments.get("days", 7)
        include_soil = arguments.get("include_soil", True)
        
        # Agricultural parameters
        params = {
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min", 
                "precipitation_sum",
                "et0_fao_evapotranspiration",
                "vapor_pressure_deficit_max",
                "daylight_duration",
                "sunshine_duration",
                "precipitation_hours",
                "wind_speed_10m_max"
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "dew_point_2m",
                "precipitation",
                "soil_temperature_0cm",
                "soil_moisture_0_to_1cm"
            ] if include_soil else []
        }
        
        try:
            forecast_data = self.weather_client.get_forecast(
                latitude=location.latitude,
                longitude=location.longitude,
                daily=params["daily"],
                hourly=params["hourly"] if params["hourly"] else None,
                forecast_days=days,
                timezone="auto"
            )
            
            # Format with agricultural focus
            result = self._format_agricultural_response(
                forecast_data,
                location,
                crop_type,
                days
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Agricultural forecast error: {e}")
            return f"Error getting agricultural forecast: {str(e)}"
    
    async def _get_alerts(self, location: Location) -> str:
        """Get weather alerts for a location."""
        # In a real implementation, this would query a weather alerts API
        # For now, we'll provide a mock implementation
        
        return f"""Weather Alerts for {location.name}:

No active weather alerts at this time.

Monitor conditions for:
- Temperature: Normal range expected
- Precipitation: No significant events forecast
- Wind: Light to moderate conditions
- Severe Weather: No warnings issued

Last checked: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
    
    def _format_forecast_response(self, data: dict, location: Location, days: int, include_hourly: bool) -> str:
        """Format forecast data into readable response."""
        result = f"Weather Forecast for {location.name}\n"
        result += f"Coordinates: {location.latitude:.3f}°N, {location.longitude:.3f}°E\n"
        result += "=" * 50 + "\n\n"
        
        # Daily forecast
        if "daily" in data and data["daily"]:
            result += "Daily Forecast:\n"
            daily = data["daily"]
            
            for i in range(min(days, len(daily.get("time", [])))):
                date = daily["time"][i]
                result += f"\n{date}:\n"
                
                # Temperature
                if "temperature_2m_max" in daily:
                    max_temp = daily["temperature_2m_max"][i]
                    min_temp = daily.get("temperature_2m_min", [None])[i]
                    result += f"  Temperature: {min_temp:.1f}°C - {max_temp:.1f}°C\n"
                
                # Precipitation
                if "precipitation_sum" in daily:
                    precip = daily["precipitation_sum"][i]
                    prob = daily.get("precipitation_probability_max", [None])[i]
                    result += f"  Precipitation: {precip:.1f}mm"
                    if prob is not None:
                        result += f" ({prob}% chance)"
                    result += "\n"
                
                # Wind
                if "wind_speed_10m_max" in daily:
                    wind = daily["wind_speed_10m_max"][i]
                    direction = daily.get("wind_direction_10m_dominant", [None])[i]
                    result += f"  Wind: {wind:.1f} km/h"
                    if direction is not None:
                        result += f" from {direction}°"
                    result += "\n"
        
        # Hourly forecast (abbreviated)
        if include_hourly and "hourly" in data and data["hourly"]:
            result += "\n\nHourly Highlights (next 24 hours):\n"
            hourly = data["hourly"]
            
            # Show every 3 hours for the first 24 hours
            for i in range(0, min(24, len(hourly.get("time", []))), 3):
                time = hourly["time"][i]
                # Extract just the time portion
                time_str = time.split("T")[1] if "T" in time else time
                
                result += f"\n{time_str}:"
                
                if "temperature_2m" in hourly:
                    temp = hourly["temperature_2m"][i]
                    result += f" {temp:.1f}°C"
                
                if "precipitation" in hourly:
                    precip = hourly["precipitation"][i]
                    if precip > 0:
                        result += f", {precip:.1f}mm rain"
                
                if "wind_speed_10m" in hourly:
                    wind = hourly["wind_speed_10m"][i]
                    result += f", {wind:.1f}km/h wind"
        
        return result
    
    def _format_agricultural_response(self, data: dict, location: Location, crop_type: str, days: int) -> str:
        """Format agricultural forecast with crop-specific insights."""
        result = f"Agricultural Forecast for {location.name}\n"
        result += f"Crop Focus: {crop_type.title()}\n"
        result += "=" * 50 + "\n\n"
        
        if "daily" in data and data["daily"]:
            daily = data["daily"]
            
            # Summary section
            result += "Growing Conditions Summary:\n"
            
            # Calculate aggregates
            total_precip = sum(daily.get("precipitation_sum", [0] * days)[:days])
            avg_max_temp = sum(daily.get("temperature_2m_max", [0] * days)[:days]) / days
            avg_min_temp = sum(daily.get("temperature_2m_min", [0] * days)[:days]) / days
            total_sunshine = sum(daily.get("sunshine_duration", [0] * days)[:days]) / 3600  # Convert to hours
            
            result += f"  • Total Precipitation: {total_precip:.1f}mm\n"
            result += f"  • Average Temperature: {avg_min_temp:.1f}°C - {avg_max_temp:.1f}°C\n"
            result += f"  • Total Sunshine: {total_sunshine:.1f} hours\n"
            
            # Crop-specific insights
            result += f"\n{crop_type.title()} Specific Insights:\n"
            
            if crop_type.lower() in ["corn", "maize"]:
                # Corn-specific analysis
                gdd_base = 10  # Base temperature for corn
                gdd_total = 0
                
                for i in range(min(days, len(daily["time"]))):
                    max_t = daily["temperature_2m_max"][i]
                    min_t = daily["temperature_2m_min"][i]
                    avg_t = (max_t + min_t) / 2
                    gdd = max(0, avg_t - gdd_base)
                    gdd_total += gdd
                
                result += f"  • Growing Degree Days (base {gdd_base}°C): {gdd_total:.0f}\n"
                result += f"  • Moisture Status: "
                
                if total_precip < 25 * days / 7:  # Less than 25mm per week
                    result += "Consider irrigation\n"
                elif total_precip > 50 * days / 7:  # More than 50mm per week
                    result += "Monitor for excess moisture\n"
                else:
                    result += "Adequate\n"
            
            elif crop_type.lower() in ["wheat", "barley"]:
                # Small grains analysis
                result += f"  • Frost Risk: "
                frost_days = sum(1 for t in daily.get("temperature_2m_min", [])[:days] if t < 0)
                if frost_days > 0:
                    result += f"Warning - {frost_days} days with potential frost\n"
                else:
                    result += "Low\n"
            
            # Daily details
            result += "\nDaily Agricultural Details:\n"
            
            for i in range(min(days, len(daily["time"]))):
                date = daily["time"][i]
                result += f"\n{date}:\n"
                
                # Growing conditions
                max_t = daily.get("temperature_2m_max", [None])[i]
                min_t = daily.get("temperature_2m_min", [None])[i]
                precip = daily.get("precipitation_sum", [0])[i]
                et0 = daily.get("et0_fao_evapotranspiration", [None])[i]
                
                if max_t is not None and min_t is not None:
                    result += f"  Temperature: {min_t:.1f}°C - {max_t:.1f}°C"
                    
                    # Add temperature warnings
                    if max_t > 35:
                        result += " ⚠️ Heat stress risk"
                    elif min_t < 0:
                        result += " ❄️ Frost risk"
                    result += "\n"
                
                result += f"  Precipitation: {precip:.1f}mm\n"
                
                if et0 is not None:
                    result += f"  Evapotranspiration: {et0:.1f}mm\n"
                    water_balance = precip - et0
                    result += f"  Water Balance: {water_balance:+.1f}mm\n"
        
        # Add soil conditions if available
        if "hourly" in data and data["hourly"] and "soil_temperature_0cm" in data["hourly"]:
            result += "\nSoil Conditions (Latest):\n"
            latest_soil_temp = data["hourly"]["soil_temperature_0cm"][-1]
            latest_soil_moisture = data["hourly"].get("soil_moisture_0_to_1cm", [None])[-1]
            
            result += f"  Surface Temperature: {latest_soil_temp:.1f}°C\n"
            if latest_soil_moisture is not None:
                result += f"  Surface Moisture: {latest_soil_moisture:.3f} m³/m³\n"
        
        return result


async def main():
    """Run the enhanced forecast MCP server."""
    server = ForecastServer()
    
    async with stdio_server() as streams:
        await server.app.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name=server.name,
                server_version="2.0.0",
                capabilities={
                    "tools": {},
                    "resources": {}
                }
            )
        )


if __name__ == "__main__":
    print("Starting Advanced Forecast MCP Server...", file=sys.stderr)
    print("Available at: stdio://python 05-advanced-mcp/mcp_servers/forecast.py", file=sys.stderr)
    asyncio.run(main())
```

### Step 6: Improved Weather Agent Orchestrator

Create `agents/weather_analyst.py`:

```python
"""
Advanced weather analyst using Claude's native tool calling.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

# Import our tools
import sys
sys.path.append('..')
from tools.location_tools import LocationExtraction, TimeRangeExtraction, QueryAnalysis
from tools.query_tools import (
    extract_location_from_query,
    extract_time_range_from_query,
    analyze_weather_query
)
from services.location import LocationService


class AdvancedWeatherAnalyst:
    """
    Claude-powered weather analyst with native tool calling.
    
    Features:
    - Natural language understanding
    - Dynamic location extraction
    - Intelligent query routing
    - Context-aware responses
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=2000
        )
        
        self.location_service = LocationService()
        
        # Create agent with tools
        self.analysis_agent = create_react_agent(
            model=self.llm,
            tools=[
                extract_location_from_query,
                extract_time_range_from_query,
                analyze_weather_query
            ],
            state_modifier=self._get_analysis_prompt()
        )
    
    def _get_analysis_prompt(self) -> str:
        """Get the system prompt for query analysis."""
        return """You are an expert weather query analyst. Your role is to:

1. Extract location information from queries (city names, coordinates, or regions)
2. Identify time references (dates, ranges, or relative times like "next week")
3. Determine the query intent (forecast, historical, agricultural, or comparison)
4. Identify specific weather parameters needed

Always use the provided tools to structure your analysis. Be thorough but efficient.

For locations:
- Extract exactly as mentioned by the user
- Note if coordinates are provided
- If no location is mentioned, note that clearly

For time:
- Convert relative references to approximate dates
- Note if the query is about current/future (forecast) or past (historical)

For intent:
- Forecast: Current conditions or future predictions
- Historical: Past weather data or trends
- Agricultural: Farming, crops, irrigation, or growing conditions
- Comparison: Comparing different times or locations"""
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a weather query using Claude's tool calling.
        
        Returns a structured analysis with location, time, and intent.
        """
        # Use the agent to analyze the query
        result = await self.analysis_agent.ainvoke({
            "messages": [HumanMessage(content=f"Analyze this weather query: {query}")]
        })
        
        # Extract tool results
        analysis = {
            "original_query": query,
            "location": None,
            "time_range": None,
            "query_analysis": None,
            "confidence": 0.9
        }
        
        # Process the agent's tool calls
        for message in result["messages"]:
            if hasattr(message, "tool_calls"):
                for tool_call in message.tool_calls:
                    if tool_call["name"] == "extract_location_from_query":
                        location_data = LocationExtraction(**tool_call["args"])
                        if location_data.location_mentioned:
                            # Resolve the location
                            try:
                                if location_data.has_coordinates:
                                    location = self.location_service.resolve_coordinates(
                                        location_data.latitude,
                                        location_data.longitude
                                    )
                                else:
                                    location = self.location_service.resolve_location(
                                        location_data.location_text
                                    )
                                
                                analysis["location"] = location.to_dict()
                                
                            except Exception as e:
                                # Log error but don't fail
                                analysis["location"] = {
                                    "name": location_data.location_text,
                                    "error": str(e)
                                }
                    
                    elif tool_call["name"] == "extract_time_range_from_query":
                        analysis["time_range"] = tool_call["args"]
                    
                    elif tool_call["name"] == "analyze_weather_query":
                        analysis["query_analysis"] = tool_call["args"]
        
        return analysis
    
    async def synthesize_response(
        self,
        query: str,
        analysis: Dict[str, Any],
        agent_responses: Dict[str, str]
    ) -> str:
        """
        Synthesize a natural language response from agent data.
        """
        # Build context for Claude
        context = f"""User Query: {query}

Location: {json.dumps(analysis.get('location', {}), indent=2)}
Time Range: {json.dumps(analysis.get('time_range', {}), indent=2)}
Query Type: {json.dumps(analysis.get('query_analysis', {}), indent=2)}

Agent Responses:
"""
        
        for agent_name, response in agent_responses.items():
            context += f"\n{agent_name.title()} Agent:\n{response}\n"
        
        # Create synthesis prompt
        system_prompt = """You are a helpful weather assistant. Synthesize the provided weather data into a clear, 
conversational response that directly addresses the user's query. 

Guidelines:
- Be concise but comprehensive
- Highlight the most important information first
- Use natural language, not technical jargon
- Include specific numbers and dates
- Add practical advice when relevant
- If data is missing or unclear, acknowledge it gracefully"""
        
        # Get Claude's response
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=context)
        ])
        
        return response.content
```

### Step 7: Testing Framework

Create `tests/test_location_service.py`:

```python
"""
Tests for the enhanced location service.
"""

import pytest
from services.location import LocationService, Location


class TestLocationService:
    """Test the location service functionality."""
    
    @pytest.fixture
    def service(self):
        """Create a location service instance."""
        return LocationService()
    
    def test_city_resolution(self, service):
        """Test resolving city names."""
        # Major cities
        location = service.resolve_location("New York")
        assert location.latitude is not None
        assert location.longitude is not None
        assert "New York" in location.name
        
        # With country
        location = service.resolve_location("Paris, France")
        assert location.latitude is not None
        assert location.longitude is not None
        assert "Paris" in location.name
    
    def test_coordinate_parsing(self, service):
        """Test parsing coordinate strings."""
        # Various formats
        test_cases = [
            ("40.7128, -74.0060", (40.7128, -74.0060)),
            ("40.7128,-74.0060", (40.7128, -74.0060)),
            ("40.7128 -74.0060", (40.7128, -74.0060)),
            ("-33.8688, 151.2093", (-33.8688, 151.2093)),  # Sydney
        ]
        
        for coord_str, expected in test_cases:
            location = service.resolve_location(coord_str)
            assert abs(location.latitude - expected[0]) < 0.0001
            assert abs(location.longitude - expected[1]) < 0.0001
    
    def test_coordinate_validation(self, service):
        """Test coordinate validation."""
        # Valid coordinates
        location = service.resolve_coordinates(40.7128, -74.0060)
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060
        
        # Invalid coordinates
        with pytest.raises(ValueError):
            service.resolve_coordinates(91, 0)  # Invalid latitude
        
        with pytest.raises(ValueError):
            service.resolve_coordinates(0, 181)  # Invalid longitude
    
    def test_fuzzy_matching(self, service):
        """Test fuzzy matching for common abbreviations."""
        # Common abbreviations
        location = service.resolve_location("NYC")
        assert location is not None
        assert "New York" in location.name
        
        location = service.resolve_location("SF")
        assert location is not None
        assert "San Francisco" in location.name
    
    def test_error_handling(self, service):
        """Test error handling for invalid locations."""
        with pytest.raises(ValueError) as exc_info:
            service.resolve_location("ThisIsNotARealLocationName123456")
        
        assert "Could not resolve location" in str(exc_info.value)
    
    def test_caching(self, service):
        """Test that location resolution is cached."""
        import time
        
        # First call
        start = time.time()
        location1 = service.resolve_location("London")
        first_duration = time.time() - start
        
        # Second call (should be cached)
        start = time.time()
        location2 = service.resolve_location("London")
        second_duration = time.time() - start
        
        # Cached call should be much faster
        assert second_duration < first_duration / 2
        
        # Results should be identical
        assert location1.latitude == location2.latitude
        assert location1.longitude == location2.longitude
```

### Step 8: Main Entry Point

Create `main.py`:

```python
#!/usr/bin/env python3
"""
Advanced MCP Weather System - Main Entry Point

This demonstrates the improved architecture with:
- Dynamic location support
- Claude tool integration
- Production-ready error handling
"""

import asyncio
import sys
from typing import Optional

from agents.weather_analyst import AdvancedWeatherAnalyst
from agents.orchestrator import WeatherOrchestrator


async def interactive_demo():
    """Run an interactive weather query demo."""
    print("Advanced Weather Query System")
    print("=" * 50)
    print("Enter weather queries naturally. Examples:")
    print("- What's the weather in Tokyo next week?")
    print("- How was the temperature in Paris last month?")
    print("- Will it rain in Sydney tomorrow?")
    print("- Agricultural forecast for corn in Iowa")
    print("- Compare this week's weather to last year in London")
    print("\nType 'quit' to exit\n")
    
    # Initialize components
    analyst = AdvancedWeatherAnalyst()
    orchestrator = WeatherOrchestrator()
    
    while True:
        try:
            query = input("\n> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            # Analyze the query
            print("\nAnalyzing query...")
            analysis = await analyst.analyze_query(query)
            
            # Show what we understood
            if analysis.get("location"):
                print(f"Location: {analysis['location']['name']}")
            else:
                print("Location: Not specified (using default)")
            
            if analysis.get("query_analysis"):
                intents = analysis["query_analysis"].get("query_intent", [])
                print(f"Intent: {', '.join(intents)}")
            
            # Get responses from appropriate agents
            print("\nQuerying weather agents...")
            agent_responses = await orchestrator.route_query(analysis)
            
            # Synthesize final response
            print("\nGenerating response...")
            response = await analyst.synthesize_response(
                query,
                analysis,
                agent_responses
            )
            
            print("\n" + "=" * 50)
            print(response)
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try rephrasing your query.")


async def batch_demo():
    """Demonstrate batch processing of queries."""
    queries = [
        "What's the weather in Tokyo?",
        "Temperature in Paris, France next week",
        "Will it rain in 40.7128, -74.0060 tomorrow?",
        "Agricultural forecast for corn in Des Moines",
        "Compare weather in London vs New York",
        "Historical weather for Sydney last month",
        "Frost risk for wheat in Kansas next week"
    ]
    
    analyst = AdvancedWeatherAnalyst()
    
    print("Batch Query Analysis Demo")
    print("=" * 50)
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        try:
            analysis = await analyst.analyze_query(query)
            
            # Display results
            if analysis.get("location"):
                loc = analysis["location"]
                print(f"  Location: {loc.get('name', 'Unknown')}")
                if "latitude" in loc:
                    print(f"  Coordinates: {loc['latitude']:.3f}, {loc['longitude']:.3f}")
            
            if analysis.get("query_analysis"):
                qa = analysis["query_analysis"]
                print(f"  Intent: {', '.join(qa.get('query_intent', []))}")
                if qa.get('weather_parameters'):
                    print(f"  Parameters: {', '.join(qa['weather_parameters'])}")
            
        except Exception as e:
            print(f"  Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        asyncio.run(batch_demo())
    else:
        asyncio.run(interactive_demo())


if __name__ == "__main__":
    main()
```

## Part 3: Key Improvements Explained

### 1. Dynamic Location Support

The new architecture completely removes location restrictions:

```python
# Before: Only 8 hard-coded locations
"enum": ["Grand Island, Nebraska", "Scottsbluff, Nebraska", ...]

# After: Any location worldwide
"location": {
    "type": "string",
    "description": "Location name (e.g., 'New York, NY', 'London, UK', 'Tokyo')"
}
```

**Benefits:**
- Users can query weather for any location
- Supports city names, coordinates, and landmarks
- Automatic geocoding with intelligent fallbacks
- No code changes needed for new locations

### 2. Claude Tool Integration

Instead of parsing JSON strings, we use Claude's native tool-calling:

```python
# Before: Fragile JSON parsing
result = json.loads(message.content[0].text)

# After: Type-safe tool calling
@tool
def extract_location_from_query(query: str) -> LocationExtraction:
    """Extract location information from a weather query."""
    pass

# Claude calls this tool directly with structured output
```

**Benefits:**
- Type safety with Pydantic models
- Automatic validation
- Better error messages
- More reliable parsing

### 3. Production-Ready Architecture

The new base class provides consistent patterns:

```python
class WeatherMCPServer(ABC):
    """Base class with production features."""
    
    async def call_tool(self, name: str, arguments: dict):
        # Automatic location resolution
        # Comprehensive error handling
        # Performance monitoring
        # Structured responses with metadata
```

**Benefits:**
- Consistent error handling across all servers
- Built-in performance monitoring
- Automatic location resolution
- Extensible for new features

### 4. Enhanced User Experience

The improvements enable natural queries:

```python
# All of these now work:
"Weather in Paris"                    # ✓ City name
"Temperature at 40.7, -74.0"          # ✓ Coordinates
"Will it rain in Tokyo tomorrow?"     # ✓ Natural language
"Frost risk for my farm near Denver"  # ✓ Fuzzy location
"Weather forecast for 10001"          # ✓ ZIP code
```

## Part 4: Running the Enhanced System

### Setup

1. Install dependencies:
```bash
cd 05-advanced-mcp
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Running MCP Servers

Start the enhanced forecast server:
```bash
python mcp_servers/forecast.py
```

### Testing

Run the test suite:
```bash
pytest tests/ -v
```

### Interactive Demo

Try the interactive demo:
```bash
python main.py
```

Or batch processing demo:
```bash
python main.py batch
```

## Part 5: Exercise - Implement Historical Server

Now it's your turn! Using the patterns from this tutorial, implement an enhanced historical weather server.

### Requirements

1. Create `mcp_servers/historical.py` that:
   - Extends `WeatherMCPServer`
   - Supports any location (not hard-coded)
   - Provides tools for historical queries
   - Includes climate comparison features

2. Add these tools:
   - `get_historical_data`: Get past weather for any date range
   - `compare_periods`: Compare two time periods
   - `get_climate_normals`: Get average conditions for a location

3. Include smart features:
   - Automatic date parsing ("last month", "summer 2023")
   - Climate anomaly detection
   - Seasonal summaries

### Hints

- Use the forecast server as a template
- The base class handles location resolution
- Focus on the unique historical features
- Remember to format responses clearly

## Conclusion

In this tutorial, we've transformed a basic MCP architecture into a production-ready system. The key lessons:

1. **Don't Hard-Code Limitations**: Use dynamic schemas and services
2. **Leverage Native Capabilities**: Use Claude's tool-calling instead of JSON parsing
3. **Build Reusable Patterns**: Create base classes and shared services
4. **Think Production**: Add proper error handling, logging, and monitoring
5. **Focus on User Experience**: Support natural language and flexible inputs

The techniques shown here can be applied to any MCP-based system, not just weather applications. Use these patterns to build robust, scalable AI agent systems.

## Next Steps

- Implement the remaining servers (historical, agricultural)
- Add more sophisticated caching
- Integrate with real weather alert APIs
- Build a web interface for the system
- Add multi-language support

Happy coding! 🚀