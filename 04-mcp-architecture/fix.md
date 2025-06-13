# MCP Architecture - Recommended Fixes and Improvements

## Priority 1: Critical Performance Issues

### 1.1 Replace Synchronous HTTP Calls with Async
**Problem**: The current implementation uses synchronous `requests` library in an async context, causing performance bottlenecks.

**Solution**: Update `mcp_servers/api_utils.py` to use `httpx` for async HTTP calls.

```python
# Current (synchronous)
import requests

class OpenMeteoClient:
    def __init__(self):
        self.session = requests.Session()
        
    def get_forecast(self, ...):
        response = self.session.get(self.forecast_url, params=params)
        return response.json()

# Recommended (asynchronous)
import httpx
from typing import Optional
import asyncio

class OpenMeteoClient:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        
    async def _ensure_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
        
    async def get_forecast_async(self, latitude: float, longitude: float, **params):
        client = await self._ensure_client()
        response = await client.get(self.forecast_url, params={
            "latitude": latitude,
            "longitude": longitude,
            **params
        })
        response.raise_for_status()
        return response.json()
    
    # Keep sync methods for backward compatibility
    def get_forecast(self, latitude: float, longitude: float, **params):
        return asyncio.run(self.get_forecast_async(latitude, longitude, **params))
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
```

### 1.2 Update MCP Servers to Use Async Client
Each MCP server needs to be updated to properly handle async operations:

```python
# In forecast_server.py, historical_server.py, agricultural_server.py
async def call_tool(self, name: str, arguments: dict) -> list:
    if name == "get_weather_forecast":
        # Create async-aware client
        api_client = OpenMeteoClient()
        try:
            # Use async method
            data = await api_client.get_forecast_async(lat, lon, **params)
            # Process data
            return format_response(data)
        finally:
            await api_client.close()
```

## Priority 2: Documentation Fixes

### 2.1 Fix OVERVIEW.md References
**Problem**: Documentation references non-existent files.

Update the following sections in `OVERVIEW.md`:

```markdown
# Current (incorrect)
python 04-mcp-architecture/test_mcp_servers.py
python 04-mcp-architecture/quick_demo.py

# Fixed
python 04-mcp-architecture/test_mcp.py
python 04-mcp-architecture/main.py --demo
```

### 2.2 Update Architecture Description
Remove references to deleted directories:

```markdown
# Remove references to:
- agents/ subdirectory
- claude_integration.py
- mcp_integration.py
```

## Priority 3: Configuration Management

### 3.1 Create Configuration Module
**Problem**: Hardcoded values scattered throughout the codebase.

Create `mcp_servers/config.py`:

```python
"""Configuration settings for MCP weather servers."""
from typing import Dict, List
from datetime import timedelta

# API Configuration
API_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 1  # seconds

# Supported locations with coordinates for caching
SUPPORTED_LOCATIONS: Dict[str, Dict[str, float]] = {
    "Ames, Iowa": {"lat": 42.0308, "lon": -93.6319},
    "Des Moines, Iowa": {"lat": 41.5868, "lon": -93.6250},
    "Grand Island, Nebraska": {"lat": 40.9264, "lon": -98.3420},
    "Fresno, California": {"lat": 36.7378, "lon": -119.7871},
    "Salinas, California": {"lat": 36.6777, "lon": -121.6555},
    "Twin Falls, Idaho": {"lat": 42.5558, "lon": -114.4701},
    "San Angelo, Texas": {"lat": 31.4638, "lon": -100.4370},
    "Garden City, Kansas": {"lat": 37.9717, "lon": -100.8727},
}

# Weather Parameters
DEFAULT_WEATHER_PARAMS = [
    "temperature_2m",
    "precipitation",
    "wind_speed_10m",
    "relative_humidity_2m"
]

AGRICULTURAL_PARAMS = [
    "soil_temperature_0cm",
    "soil_temperature_6cm", 
    "soil_moisture_0_to_1cm",
    "et0_fao_evapotranspiration",
    "shortwave_radiation"
]

# Date Limits
MAX_FORECAST_DAYS = 16
MAX_HISTORICAL_DAYS = 365

# Response Formatting
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
```

### 3.2 Use Configuration in Servers
Update servers to use configuration:

```python
# In forecast_server.py
from .config import SUPPORTED_LOCATIONS, MAX_FORECAST_DAYS, DEFAULT_WEATHER_PARAMS

@app.call_tool()
async def call_tool(self, name: str, arguments: dict) -> list:
    if name == "get_weather_forecast":
        location = arguments.get("location")
        if location not in SUPPORTED_LOCATIONS:
            return [{"type": "text", "text": f"Unknown location: {location}"}]
        
        coords = SUPPORTED_LOCATIONS[location]
        days = min(arguments.get("days", 7), MAX_FORECAST_DAYS)
        # ...
```

## Priority 4: Enhanced Error Handling

### 4.1 Create Custom Exceptions
Create `mcp_servers/exceptions.py`:

```python
"""Custom exceptions for MCP weather servers."""

class WeatherAPIError(Exception):
    """Base exception for weather API errors."""
    pass

class LocationNotFoundError(WeatherAPIError):
    """Raised when a location cannot be geocoded."""
    def __init__(self, location: str):
        self.location = location
        super().__init__(f"Location not found: {location}")

class APIRateLimitError(WeatherAPIError):
    """Raised when API rate limit is exceeded."""
    pass

class InvalidDateRangeError(WeatherAPIError):
    """Raised when date range is invalid."""
    def __init__(self, message: str):
        super().__init__(f"Invalid date range: {message}")

class DataNotAvailableError(WeatherAPIError):
    """Raised when requested data is not available."""
    pass
```

### 4.2 Implement Proper Error Handling
Update API client and servers:

```python
# In api_utils.py
from .exceptions import LocationNotFoundError, APIRateLimitError

async def get_coordinates_detailed(self, location_name: str) -> Tuple[float, float]:
    try:
        results = await self.geocode_async(location_name, count=1)
        if not results:
            raise LocationNotFoundError(location_name)
        location = results[0]
        return location["latitude"], location["longitude"]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise APIRateLimitError("Geocoding API rate limit exceeded")
        raise WeatherAPIError(f"API error: {e}")
```

## Priority 5: Add Retry Logic

### 5.1 Install Required Dependencies
Add to `requirements.txt`:
```
httpx>=0.24.0
tenacity>=8.2.0
```

### 5.2 Implement Retry Decorator
Update `api_utils.py`:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from httpx import HTTPStatusError, ConnectError, TimeoutException

# Retry configuration
retry_config = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((HTTPStatusError, ConnectError, TimeoutException))
)

class OpenMeteoClient:
    @retry_config
    async def get_forecast_async(self, latitude: float, longitude: float, **params):
        client = await self._ensure_client()
        response = await client.get(
            self.forecast_url,
            params={"latitude": latitude, "longitude": longitude, **params}
        )
        response.raise_for_status()
        return response.json()
```

## Priority 6: Integration Tests

### 6.1 Create Test Suite
Create `test_integration.py`:

```python
"""Integration tests for MCP weather architecture."""
import pytest
import asyncio
from datetime import datetime, timedelta
from weather_agent.mcp_agent import create_mcp_weather_agent

@pytest.mark.asyncio
async def test_multi_server_coordination():
    """Test that multiple servers can work together."""
    agent = await create_mcp_weather_agent()
    
    try:
        # Query that requires both forecast and historical data
        response = await agent.arun(
            "Compare the current forecast for Ames, Iowa with the weather "
            "from the same time last year"
        )
        
        # Verify both servers were used
        assert "forecast" in response.lower()
        assert "historical" in response.lower() or "last year" in response.lower()
        
    finally:
        await agent.cleanup()

@pytest.mark.asyncio
async def test_agricultural_analysis():
    """Test agricultural condition analysis."""
    agent = await create_mcp_weather_agent()
    
    try:
        response = await agent.arun(
            "What are the soil conditions in Fresno, California?"
        )
        
        # Verify agricultural server was used
        assert any(term in response.lower() for term in 
                  ["soil", "moisture", "temperature", "agricultural"])
        
    finally:
        await agent.cleanup()

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid queries."""
    agent = await create_mcp_weather_agent()
    
    try:
        # Test invalid location
        response = await agent.arun(
            "What's the weather in Atlantis?"
        )
        assert "not found" in response.lower() or "unknown" in response.lower()
        
        # Test invalid date range
        response = await agent.arun(
            "Show me weather from 100 years ago"
        )
        assert any(term in response.lower() for term in 
                  ["not available", "cannot", "invalid"])
        
    finally:
        await agent.cleanup()

@pytest.mark.asyncio
async def test_conversation_context():
    """Test that conversation context is maintained."""
    from weather_agent.chatbot import WeatherChatbot
    
    chatbot = WeatherChatbot()
    await chatbot.start()
    
    try:
        # First query
        response1 = await chatbot.chat("What's the weather in Ames, Iowa?")
        assert "ames" in response1.lower()
        
        # Follow-up query using context
        response2 = await chatbot.chat("How does that compare to last week?")
        assert "ames" in response2.lower() or "previous" in response2.lower()
        
    finally:
        await chatbot.cleanup()

def test_sync_async_compatibility():
    """Test that sync methods still work for backward compatibility."""
    from mcp_servers.api_utils import OpenMeteoClient
    
    client = OpenMeteoClient()
    
    # Test sync method
    lat, lon = client.get_coordinates("Ames, Iowa")
    assert abs(lat - 42.0308) < 0.01
    assert abs(lon - -93.6319) < 0.01
    
    # Test sync forecast
    data = client.get_forecast(lat, lon, daily=["temperature_2m_max"])
    assert "daily" in data
    assert "temperature_2m_max" in data["daily"]
```

### 6.2 Create Test Configuration
Create `pytest.ini`:

```ini
[pytest]
testpaths = 04-mcp-architecture
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

## Additional Recommendations

### 1. Add Logging
Create `mcp_servers/logging_config.py`:

```python
import logging
import sys

def setup_logging(name: str, level: str = "INFO"):
    """Setup logging configuration for MCP servers."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### 2. Add Caching
Implement simple caching for geocoding results:

```python
from functools import lru_cache

class OpenMeteoClient:
    @lru_cache(maxsize=128)
    def get_coordinates_cached(self, location: str) -> Tuple[float, float]:
        """Cached version of coordinate lookup."""
        return self.get_coordinates(location)
```

### 3. Add Type Hints
Ensure all functions have proper type hints:

```python
from typing import Dict, List, Optional, Union, Tuple
from datetime import date, datetime

async def get_forecast_async(
    self,
    latitude: float,
    longitude: float,
    *,
    daily: Optional[List[str]] = None,
    hourly: Optional[List[str]] = None,
    current: Optional[List[str]] = None,
    days: int = 7
) -> Dict[str, Union[Dict, List, str, float]]:
    """Get weather forecast with full type hints."""
    # Implementation
```

## Implementation Order

1. **Week 1**: Fix documentation and add configuration management
2. **Week 2**: Implement async HTTP calls and retry logic
3. **Week 3**: Add error handling and logging
4. **Week 4**: Create integration tests and performance benchmarks

## Expected Improvements

- **Performance**: 50-70% reduction in response time with async calls
- **Reliability**: 90% reduction in transient failures with retry logic
- **Maintainability**: Easier to add new locations and parameters
- **Debugging**: Better error messages and logging for troubleshooting
- **Testing**: Automated validation of multi-server coordination