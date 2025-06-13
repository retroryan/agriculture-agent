# Distributed Tools: MCP and Multi-Agent Architecture

## Your Position in the Learning Journey

**Stage 4 of 4**: Production-Ready Distributed Systems

You've built agents with embedded tools. They work great until you need to:
- Share tools across multiple projects
- Write tools in different languages
- Scale tools independently
- Update tools without redeploying agents

This final stage solves those limitations with MCP (Model Context Protocol) and multi-agent orchestration.

## The Paradigm Shift: From Monolithic to Distributed

The Model Context Protocol (MCP) represents a paradigm shift in how AI agents interact with tools and external systems. Instead of tightly coupling tool implementations within the agent code, MCP enables a distributed architecture where tools run as independent servers that agents can discover and use dynamically.

This isn't just a technical upgrade - it's a fundamental rethinking of AI architecture.

## The Problem with Embedded Tools

Remember your tool-using agent from stage 3? Every tool was:
- Written in Python
- Embedded in your application
- Loaded into memory with your agent
- Updated only by redeploying everything

That's fine for demos. It breaks in production.

I learned this the hard way when building a weather analysis system. Different teams wanted to contribute tools - the data science team used R, the infrastructure team preferred Go, and the agricultural experts had existing Java libraries. Embedding everything in one Python app? Impossible.

### The Challenge: Complex Tool Integration

Weather and agricultural applications require integration with multiple data sources:
- Real-time forecast APIs
- Historical weather databases
- Agricultural models and calculations
- Satellite imagery processing
- Soil moisture sensors
- Irrigation system controls

Traditional approaches create:
- Monolithic, hard-to-maintain codebases
- Version conflicts between dependencies
- Difficulty scaling individual components
- Complex deployment and testing scenarios

## Enter MCP: Tools as Services

MCP turns tools into independent services that communicate through a standard protocol. Think of it as microservices for AI tools.

**The transformation:**
```
Old: Agent → Embedded Tools → Response
New: Agent → MCP Protocol → Tool Servers → Response
```

### The MCP Solution

MCP solves these challenges by:
1. **Separating concerns**: Each tool runs as an independent server
2. **Standardizing communication**: All tools speak the same protocol
3. **Enabling discovery**: Agents can dynamically find and use available tools
4. **Supporting multiple languages**: Tools can be written in any language
5. **Facilitating scaling**: Each tool server can scale independently

Let's see this in action.

## Quick Start: See It Work

```bash
# Test the complete system
python 04-mcp-architecture/test_mcp_servers.py

# Run a quick demo
python 04-mcp-architecture/quick_demo.py

# Start individual MCP servers
python 04-mcp-architecture/mcp_servers/forecast_server.py
```

## The MCP Architecture

### What's an MCP Server?

An MCP server is a standalone process that:
- Exposes tools through a standard protocol
- Communicates via stdio (stdin/stdout)
- Provides tool discovery through JSON schemas
- Runs independently of your AI agent

Here's the pattern:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("weather-forecast")

@app.list_tools()
async def list_tools():
    return [{
        "name": "get_forecast",
        "description": "Get weather forecast for a location",
        "inputSchema": {...}
    }]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_forecast":
        return await get_forecast_data(arguments)
```

That's it. Your tool is now a service.

### Three Specialized Servers

The weather system implements three domain-specific servers:

**Forecast Server** (`mcp_servers/forecast_server.py`)
- Current conditions
- 1-16 day forecasts
- Weather alerts
- Focused on "what's happening now and soon"

**Historical Server** (`mcp_servers/historical_server.py`)
- Past weather patterns
- Climate trends
- Year-over-year comparisons
- Answers "how does this compare to normal?"

**Agricultural Server** (`mcp_servers/agricultural_server.py`)
- Soil moisture at multiple depths
- Evapotranspiration rates
- Growing degree days
- Specialized for "can I plant/irrigate/harvest?"

Each server is self-contained. They share a common API client but have independent lifecycles.

### The Power of Separation

Watch what happens when a tool fails:

**Embedded Tool Failure:**
```
Tool crashes → Entire agent crashes → User loses conversation
```

**MCP Tool Failure:**
```
Tool crashes → Server restarts → Agent continues → User gets retry option
```

Production systems need this resilience.

## Building MCP Servers: The Pattern

### Step 1: Start with a Regular Tool

You already have tools from stage 3:

```python
@tool
def get_soil_moisture(location: str, depth: str) -> str:
    """Get soil moisture data for agricultural decisions."""
    # Complex implementation
    return moisture_data
```

### Step 2: Wrap It as an MCP Server

Create a minimal wrapper:

```python
from mcp.server import Server

app = Server("agricultural-tools")

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_soil_moisture":
        # Reuse existing tool logic
        return await asyncio.to_thread(
            get_soil_moisture.invoke,
            arguments
        )
```

### Step 3: Define the Interface

Tell clients what your server offers:

```python
@app.list_tools()
async def list_tools():
    return [{
        "name": "get_soil_moisture",
        "description": "Get soil moisture for irrigation decisions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "depth": {"type": "string", "enum": ["surface", "root", "deep"]}
            }
        }
    }]
```

Your tool is now discoverable, versionable, and deployable independently.

## The OpenMeteo Integration

All three servers use OpenMeteo's free weather API. No authentication needed - just coordinates and parameters.

The unified API client (`mcp_servers/api_utils.py`) handles:
- Geocoding (city names to coordinates)
- Parameter selection (what data to fetch)
- Session management (connection pooling)
- Error handling (network issues, rate limits)

This separation means you can swap weather providers without touching the MCP servers.

## Transport Layers and Communication

MCP supports multiple transport mechanisms:

- **stdio**: Communication via standard input/output (most common)
- **HTTP/SSE**: RESTful APIs with Server-Sent Events
- **WebSocket**: Bidirectional real-time communication

Most MCP servers use stdio for simplicity - they read JSON from stdin and write JSON to stdout. This makes them language-agnostic and easy to deploy.

### Tool Discovery and Dynamic Schemas

Unlike embedded tools, MCP tools are discovered at runtime:

```json
{
    "name": "get_weather_forecast",
    "description": "Get weather forecast for agricultural planning",
    "inputSchema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "enum": ["Grand Island, Nebraska", "Ames, Iowa"],
                "description": "Agricultural location to check"
            },
            "days": {
                "type": "integer",
                "description": "Number of forecast days (1-16)",
                "default": 7
            }
        },
        "required": ["location"]
    }
}
```

This schema enables:
- Automatic parameter validation
- Intelligent tool selection by AI
- Dynamic UI generation
- Cross-language compatibility

## Multi-Agent Orchestration: The Final Level

Three specialized servers are powerful. Coordinating them intelligently? That's transformative.

### The Orchestrator Pattern

The weather agent (`weather_agent/chatbot.py`) acts as a conductor:

```python
class WeatherOrchestrator:
    def __init__(self):
        self.forecast_agent = ForecastAgent()
        self.historical_agent = HistoricalAgent()
        self.agricultural_agent = AgriculturalAgent()
    
    async def process_query(self, query: str):
        # Analyze what the user needs
        intent = analyze_intent(query)
        
        # Route to appropriate specialists
        if "forecast" in intent:
            forecast_data = await self.forecast_agent.process(query)
        if "compare" in intent:
            historical_data = await self.historical_agent.process(query)
        if "farming" in intent:
            ag_data = await self.agricultural_agent.process(query)
        
        # Synthesize coherent response
        return combine_insights(forecast_data, historical_data, ag_data)
```

### Real-World Query Routing

Watch how queries flow through the system:

**"What's the weather in Iowa?"**
→ Forecast Agent only
→ Current conditions and short-term forecast

**"Is it too dry to plant corn?"**
→ Agricultural Agent primarily
→ Soil moisture analysis with crop-specific thresholds

**"How does this month compare to last year?"**
→ Historical Agent for comparison
→ Forecast Agent for current data
→ Synthesis of both perspectives

**"Should I irrigate my soybeans this week?"**
→ All three agents collaborate
→ Current moisture (Agricultural)
→ Precipitation forecast (Forecast)
→ Historical patterns (Historical)
→ Unified recommendation

### Agent Specialization

Each agent has domain expertise:

**Forecast Agent**
- Optimized for time-series data
- Understands weather terminology
- Formats data for readability

**Historical Agent**
- Statistical analysis capabilities
- Trend identification
- Anomaly detection

**Agricultural Agent**
- Crop-specific knowledge
- Growth stage awareness
- Risk assessment for farming operations

This specialization enables nuanced responses that a single agent couldn't provide.

## Production Patterns

### Dynamic Tool Discovery

New MCP servers can be added without changing the orchestrator:

```python
# Orchestrator discovers available servers
available_servers = discover_mcp_servers()

# Dynamically route based on capabilities
for server in available_servers:
    if server.can_handle(query):
        results.append(await server.process(query))
```

### Scaling Strategies

**Horizontal Scaling**
- Run multiple instances of busy servers
- Load balance at the protocol level
- Scale forecast servers during severe weather

**Geographic Distribution**
- Deploy servers close to data sources
- Regional servers for local expertise
- Edge deployment for low latency

### Failure Handling

The orchestrator handles partial failures gracefully:

```python
try:
    forecast = await forecast_agent.process(query)
except ServerTimeout:
    forecast = "Forecast temporarily unavailable"

# Continue with available data
response = synthesize(historical_data, ag_data, forecast)
```

Users get the best available answer, not an error.

## Testing MCP Systems

### Testing Individual Servers

```python
# Test a server in isolation
async def test_forecast_server():
    # Start server process
    server = await start_mcp_server("forecast_server.py")
    
    # Discover tools
    tools = await server.list_tools()
    assert "get_forecast" in [t["name"] for t in tools]
    
    # Test tool execution
    result = await server.call_tool("get_forecast", {
        "location": "Iowa City",
        "days": 3
    })
    assert "temperature" in result
```

### Testing Orchestration

```python
# Test multi-agent coordination
async def test_irrigation_decision():
    query = "Should I irrigate my corn in Nebraska?"
    
    response = await orchestrator.process(query)
    
    # Verify all agents contributed
    assert "soil moisture" in response  # Agricultural
    assert "precipitation forecast" in response  # Forecast
    assert "compared to average" in response  # Historical
```

### Integration Testing

The `test_mcp_servers.py` file shows comprehensive testing:
- Server startup and shutdown
- Tool discovery and execution
- Error handling and recovery
- Multi-agent coordination

## Real Agricultural Impact

This architecture enables sophisticated agricultural decisions:

**Planting Decisions**
- Soil temperature at planting depth
- Moisture for germination
- Frost risk assessment
- Historical success rates

**Irrigation Management**
- Current soil moisture deficit
- Evapotranspiration rates
- Precipitation forecast
- Cost-benefit analysis

**Harvest Timing**
- Crop moisture levels
- Weather windows
- Equipment availability
- Market conditions

Each decision leverages multiple specialized agents working together.

## Performance Insights

### Latency Breakdown

Typical response times:
- Tool discovery: <10ms (cached)
- Geocoding: 50-200ms (cached after first call)
- Weather API: 100-500ms (depending on parameters)
- AI processing: 200-1000ms (model dependent)
- Total: <2 seconds for complex queries

### Optimization Strategies

**Caching**
- Location coordinates (geocoding is expensive)
- Recent weather data (changes slowly)
- Tool schemas (static between updates)

**Parallel Execution**
- Agents process independently
- Combine results after all complete
- Fail fast for time-sensitive queries

**Smart Prefetching**
- Predict follow-up questions
- Preload likely data
- Cache warming for popular locations

## Advanced Patterns and Best Practices

### Server Design Principles

Build robust MCP servers by following these principles:

1. **Single Responsibility**: Each server focuses on one domain
2. **Stateless Operations**: Tools should be idempotent when possible
3. **Clear Schemas**: Provide detailed input/output schemas
4. **Error Handling**: Return structured errors with actionable messages
5. **Logging**: Implement comprehensive logging for debugging

### Security Considerations

Production MCP servers need security:

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict, auth_token: str = None):
    """Execute tool with authentication."""
    if name in PROTECTED_TOOLS:
        if not await verify_auth_token(auth_token):
            raise PermissionError("Invalid authentication")
    
    # Execute tool...
```

### Performance Optimization

- **Connection Pooling**: Reuse MCP client connections
- **Caching**: Cache tool schemas and frequently used results
- **Async Operations**: Use async/await for non-blocking operations
- **Resource Limits**: Set timeouts and memory limits

### Testing MCP Servers

```python
import pytest
from mcp.testing import MCPServerTestClient

@pytest.mark.asyncio
async def test_forecast_server():
    """Test forecast server functionality."""
    async with MCPServerTestClient("forecast_server.py") as client:
        # Test tool discovery
        tools = await client.get_tools()
        assert any(t.name == "get_weather_forecast" for t in tools)
        
        # Test tool execution
        result = await client.call_tool(
            "get_weather_forecast",
            {"location": "Ames, Iowa", "days": 3}
        )
        assert "temperature" in result
```

## Migration Guide: From Embedded to MCP

### Step 1: Identify Tool Boundaries

```python
# Before: Monolithic tool file
class WeatherTools:
    def get_forecast(self, location, days):
        # API calls, parsing, formatting...
        
    def get_historical(self, location, date_range):
        # Database queries, analysis...
        
    def analyze_agriculture(self, weather_data, crop):
        # Complex calculations...
```

### Step 2: Create Focused MCP Servers

```python
# After: Separate MCP servers
# forecast_server.py - handles only forecast operations
# historical_server.py - handles only historical queries
# agricultural_server.py - handles only ag analysis
```

### Step 3: Update Agent to Use MCP

```python
# Before
tools = [get_forecast, get_historical, analyze_agriculture]
model = ChatAnthropic().bind_tools(tools)

# After
mcp_client = MultiServerMCPClient(server_configs)
tools = await mcp_client.get_tools()
model = ChatAnthropic().bind_tools(tools)
```

## Extending the System

### Server Composition

Combine specialized servers into comprehensive solutions:

```
Agricultural Intelligence System
├── Weather Servers
│   ├── forecast_server.py      # OpenMeteo integration
│   ├── historical_server.py    # Historical analysis
│   └── radar_server.py         # Real-time radar data
├── Agricultural Servers
│   ├── soil_server.py          # Soil condition analysis
│   ├── crop_server.py          # Crop-specific insights
│   └── irrigation_server.py    # Irrigation recommendations
└── Integration Servers
    ├── satellite_server.py     # Satellite imagery analysis
    └── sensor_server.py        # IoT sensor integration
```

### Dynamic Server Discovery

Implement service discovery for automatic tool availability:

```python
class MCPServiceRegistry:
    """Registry for discovering available MCP servers."""
    
    async def discover_servers(self, service_type: str = None):
        """Find available MCP servers."""
        servers = {}
        
        # Scan for local servers
        for server_file in Path("mcp_servers").glob("*_server.py"):
            server_name = server_file.stem
            servers[server_name] = {
                "command": "python",
                "args": [str(server_file)],
                "transport": "stdio"
            }
        
        return servers
```

### Tool Versioning and Compatibility

Handle tool evolution gracefully:

```python
@app.list_tools()
async def list_tools():
    """Expose tools with version information."""
    return [{
        "name": "get_weather_forecast",
        "description": "Get weather forecast (v2)",
        "version": "2.0.0",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "days": {"type": "integer"},
                "include_hourly": {"type": "boolean", "default": False}
            }
        },
        "deprecated": False,
        "migration_guide": "Add include_hourly for hourly data"
    }]
```

## Why This Architecture Wins

**For Developers**
- Language agnostic tools
- Independent deployment
- Clear testing boundaries
- Horizontal scaling

**For Operations**
- Fault isolation
- Rolling updates
- Performance monitoring
- Resource optimization

**For Users**
- Reliable responses
- Rich insights
- Fast results
- Continuous improvement

## The Journey Complete

You've traveled from basic LLM calls to a production-ready multi-agent system:

1. **Stage 1**: Validated Claude integration
2. **Stage 2**: Built domain-specific applications
3. **Stage 3**: Added dynamic tool capabilities
4. **Stage 4**: Distributed tools and orchestrated agents

Each stage solved real limitations of the previous approach.

## Real-World Implementation: Weather Intelligence Platform

### Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LangGraph     │     │   MCP Client    │     │  MCP Servers    │
│     Agent       │────▶│   Adapter       │────▶│  (Distributed)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                         │
                                │                    ┌────┴────┐
                        ┌───────┴────────┐          │ Forecast │
                        │ Tool Discovery │          │  Server  │
                        └────────────────┘          └─────────┘
                                │                         │
                                │                    ┌────┴──────┐
                        ┌───────┴────────┐          │Historical │
                        │ Tool Routing   │          │  Server   │
                        └────────────────┘          └───────────┘
                                │                         │
                                │                    ┌────┴────────┐
                        ┌───────┴────────┐          │Agricultural │
                        │ Result Merge   │          │   Server    │
                        └────────────────┘          └─────────────┘
```

### Example: Multi-Server Weather Query

When a user asks: "Compare this week's forecast to last year's weather in Ames, and tell me if it's good for planting corn"

The agent automatically:
1. Routes to forecast_server for this week's data
2. Routes to historical_server for last year's data
3. Routes to agricultural_server for planting analysis
4. Combines results into comprehensive answer

This coordination happens transparently - the user gets a unified response.

## Quick Reference

**Run Everything:**
```bash
# Test the complete system
python 04-mcp-architecture/test_mcp_servers.py

# Quick demo
python 04-mcp-architecture/quick_demo.py

# Interactive weather agent
python 04-mcp-architecture/weather_agent/chatbot.py

# Demo mode with examples
python 04-mcp-architecture/weather_agent/chatbot.py --demo

# Start individual MCP servers
python 04-mcp-architecture/mcp_servers/forecast_server.py
python 04-mcp-architecture/mcp_servers/historical_server.py
python 04-mcp-architecture/mcp_servers/agricultural_server.py
```

**Key Patterns:**
- MCP servers for tool distribution
- Specialized agents for domain expertise
- Orchestrator for coordination
- Graceful failure handling
- Dynamic tool discovery

**Architecture Benefits:**
- Language agnostic tools
- Independent scaling
- Fault isolation
- Dynamic capabilities
- Zero-downtime updates

## Debugging and Monitoring

### Enable MCP Debug Logging

```python
import logging
logging.getLogger("mcp").setLevel(logging.DEBUG)
```

### Server Instrumentation

Monitor your MCP servers in production:

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Instrumented tool execution."""
    start_time = time.time()
    
    try:
        result = await execute_tool(name, arguments)
        
        # Log success metrics
        logger.info(f"Tool {name} completed in {time.time() - start_time}s")
        metrics.increment(f"tool.{name}.success")
        
        return {"result": result}
        
    except Exception as e:
        # Log failure metrics
        logger.error(f"Tool {name} failed: {e}")
        metrics.increment(f"tool.{name}.failure")
        raise
```

## The Journey Complete

You've traveled from basic LLM calls to a production-ready distributed AI system. Each stage solved real problems:

1. **Stage 1**: Basic agents with state management
2. **Stage 2**: Domain-specific AI applications
3. **Stage 3**: Dynamic tools for flexible capabilities
4. **Stage 4**: Distributed architecture for production scale

The paradigm shift from monolithic to distributed isn't just technical - it's a new way of thinking about AI systems. Tools become services. Agents become orchestrators. Systems become ecosystems.

You now have the patterns to build production AI systems that scale, adapt, and deliver real value.

The weather was just the beginning. These patterns apply everywhere - from agricultural intelligence to financial analysis, from healthcare to logistics. Wherever you need AI that scales, MCP provides the foundation.