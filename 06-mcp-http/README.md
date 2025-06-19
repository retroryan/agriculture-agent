# Stage 6: FastMCP HTTP Architecture with Coordinate Handling

## Overview

Stage 6 represents a **major architectural upgrade** from Stage 5's stdio-based MCP servers to modern HTTP-based FastMCP servers. This transformation provides:

1. **HTTP Architecture**: Replaces stdio/subprocess communication with clean HTTP APIs
2. **FastMCP Integration**: All servers now use FastMCP's `@app.tool()` decorator pattern
3. **Coordinate Handling**: New feature allowing LLM to provide coordinates directly for well-known locations
4. **Process Isolation**: Each server runs as an independent HTTP service on its own port
5. **Better Scalability**: HTTP servers can be deployed and scaled independently

### Key Architectural Changes from Stage 5

| Feature | Stage 5 (stdio) | Stage 6 (HTTP) |
|---------|----------------|----------------|
| Communication | stdio pipes via subprocess | HTTP requests |
| Server Framework | `mcp.server.stdio` | `fastmcp` with HTTP |
| Tool Definition | `@app.list_tools()` | `@app.tool()` decorator |
| Process Model | Subprocess management | Independent HTTP servers |
| Client | `MultiServerMCPClient` | FastMCP HTTP clients |
| Ports | N/A (stdio) | 8000, 8001, 8002 |

## Quick Start

### Prerequisites
- Python 3.12.10 (via pyenv)
- ANTHROPIC_API_KEY environment variable set
- `.env` file with your API key

### Installation
```bash
# Set Python version
pyenv local 3.12.10

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Running the Application

#### 1. Start MCP Servers
```bash
# Start all three MCP servers (runs in background)
./start_servers.sh

# Servers will run on:
# - Forecast server: http://127.0.0.1:8000
# - Historical server: http://127.0.0.1:8001
# - Agricultural server: http://127.0.0.1:8002
```

#### 2. Stop MCP Servers
```bash
# Stop all MCP servers
./stop_servers.sh

# Stop servers and clean up logs
./stop_servers.sh --clean-logs
```

#### 3. Run the Weather Agent
```bash
# Interactive mode
python main.py

# Demo mode (runs predefined scenarios)
python main.py --demo

# Multi-turn conversation demo
python main.py --multi-turn-demo

# Query mode
python main.py --query "What's the weather in Tokyo?"
```

### Running Tests

```bash
# Start servers first (if not already running)
./start_servers.sh

# Run all tests
python tests/run_all_tests.py

# Run individual tests (from project root)
python tests/test_mcp_simple.py        # Core MCP functionality
python tests/test_agent_simple.py      # Basic agent integration
python tests/test_coordinates.py       # Coordinate handling
python tests/test_diverse_cities.py    # Geographic knowledge
python tests/test_error_handling.py    # Error scenarios
```

## Key Features

### 1. Coordinate Handling
All MCP servers now accept optional `latitude` and `longitude` parameters:
- When coordinates are provided, they're used directly (bypassing geocoding)
- When only location is provided, geocoding is performed
- The LLM is encouraged to provide coordinates for well-known locations

### 2. FastMCP HTTP Architecture
- Each server runs as an independent HTTP service
- Clean RESTful API endpoints using FastMCP's `@app.tool()` decorator
- No subprocess management or stdio communication
- Async HTTP requests for better performance

### 3. Server Management
- Simple shell scripts for starting/stopping servers
- Automatic log management
- Process isolation for stability

## Architecture Details

### Server Endpoints
- **Forecast Server** (port 8000): Current and future weather (up to 16 days)
- **Historical Server** (port 8001): Past weather data (5+ days old)
- **Agricultural Server** (port 8002): Soil moisture, evapotranspiration, growing conditions

### Coordinate Handling Flow
```
User Query → LLM → Extract Location/Coordinates → MCP Server
                                                      ↓
                                          Coordinates provided?
                                               ↙         ↘
                                            Yes           No
                                             ↓            ↓
                                      Use directly    Geocode location
                                             ↘         ↙
                                           Fetch weather data
```

### FastMCP Server Pattern
```python
from fastmcp import FastMCP

app = FastMCP("weather-forecast", dependencies=["httpx"])

@app.tool()
async def get_weather_forecast(
    location: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    days: int = 7
) -> Dict[str, Any]:
    """Get weather forecast with optional coordinate override."""
    # Implementation here
```

## Project Structure
```
06-mcp-http/
├── mcp_servers/              # FastMCP HTTP servers
│   ├── forecast_server.py    # Weather forecast server
│   ├── historical_server.py  # Historical weather server
│   ├── agricultural_server.py # Agricultural conditions server
│   └── api_utils.py          # Shared Open-Meteo client
├── weather_agent/            # LangGraph agent implementation
│   ├── mcp_agent.py         # Core agent with MCP integration
│   ├── chatbot.py           # Interactive CLI interface
│   └── demo_scenarios.py    # Predefined test scenarios
├── tests/                   # Test suite
│   ├── test_mcp_simple.py   # Core MCP functionality
│   ├── test_agent_simple.py # Agent integration
│   ├── test_coordinates.py  # Coordinate handling
│   ├── test_diverse_cities.py # Geographic knowledge
│   ├── test_error_handling.py # Error scenarios
│   └── run_all_tests.py     # Test runner
├── logs/                    # Server logs (created at runtime)
├── start_servers.sh         # Start all MCP servers
├── stop_servers.sh          # Stop all MCP servers
├── main.py                  # Main entry point
└── requirements.txt         # Python dependencies
```

## Usage Examples

### Basic Weather Query
```python
from weather_agent.mcp_agent import MCPWeatherAgent

agent = MCPWeatherAgent()
await agent.initialize()

# Query with location name
response = await agent.query("What's the weather forecast for Tokyo?")
print(response)

# Query with coordinates
response = await agent.query("What's the weather at latitude 35.6762, longitude 139.6503?")
print(response)
```

### Multi-Turn Conversation
```python
# First query
response1 = await agent.query("What's the weather in Cairo?", thread_id="egypt-weather")

# Follow-up query (context preserved)
response2 = await agent.query("How about the agricultural conditions?", thread_id="egypt-weather")
```

## Troubleshooting

### Common Issues

1. **"Connection refused" errors**
   - Ensure MCP servers are running: `./start_servers.sh`
   - Check if servers are on correct ports: `ps aux | grep server.py`

2. **"All connection attempts failed" during cleanup**
   - This is a known issue that doesn't affect functionality
   - The agent operates normally despite cleanup warnings

3. **Tests timing out**
   - Some tests make multiple API calls and may take time
   - The test timeout is set to 120 seconds

### Debugging

- Server logs are stored in `logs/` directory
- Check individual server logs: `tail -f logs/forecast_server.log`
- Test direct server connection: `python tests/test_mcp_simple.py`

## Benefits of Stage 6 Architecture

1. **Production Ready**: HTTP servers can be deployed to cloud platforms
2. **Independent Scaling**: Each server can scale based on its load
3. **Better Monitoring**: Standard HTTP metrics and logging
4. **Language Agnostic**: Any HTTP client can interact with servers
5. **Simplified Deployment**: No subprocess management needed
6. **Enhanced Performance**: Coordinate handling reduces API calls

## Next Steps

- Consider implementing coordinate caching for frequently queried locations
- Add health check endpoints to servers
- Implement rate limiting for production use
- Consider containerizing servers for easier deployment