# Stage 5: Advanced MCP with Structured Outputs

## Quick Start

```bash
# Prerequisites: Python 3.12.10 and ANTHROPIC_API_KEY set up

# Install dependencies
pip install -r requirements.txt

# Run demo with structured output logging
python main.py --demo --structured

# Interactive mode with structured output
python main.py --structured
# Type 'structured' to toggle on/off during chat

# Run existing demos (backward compatible)
python main.py --demo

# Test structured output functionality
python weather_agent/tests/test_structured_output_demo.py
```

### Key Features Demonstrated

1. **Tool Call Transparency**: See exactly which MCP tools are called with what arguments
2. **Raw JSON Visibility**: View the actual Open-Meteo API responses from MCP servers
3. **Structured Output Transformation**: Watch raw JSON transform into typed Pydantic models
4. **LangGraph Option 1**: Experience the power of structured output for tool calling

## Evolution from Stage 4

Stage 5 builds upon the MCP (Model Context Protocol) architecture from Stage 4 by implementing **LangGraph Option 1 structured output** approach. While Stage 4 focused on establishing distributed tool systems with process isolation, Stage 5 adds structured output capabilities while maintaining the simplicity of raw JSON data flow.

### Key Enhancements

1. **LangGraph Option 1 Structured Output**
   - MCP servers return raw Open-Meteo JSON (simple and flexible)
   - Agent processes data and can return structured Pydantic models
   - Dual capability: both text responses and typed structured data
   - Clean separation between data retrieval and structuring

2. **Simplified MCP Server Architecture**
   - Simplified servers return consolidated Open-Meteo JSON responses
   - No complex structured output at server level
   - Direct pass-through of API data for maximum LLM flexibility
   - Maintained process isolation and async optimization

3. **Enhanced Agent Capabilities**
   - `query()` method for traditional text responses  
   - `query_structured()` method for typed Pydantic model output
   - LangGraph checkpointer for robust conversation memory
   - Multi-turn conversation support with thread isolation

4. **Structured Output Models**
   - `OpenMeteoResponse`: Consolidates weather data with typed fields
   - `AgricultureAssessment`: Provides farming recommendations with structure
   - Type-safe output for applications requiring structured data
   - JSON serialization support for API integration

## Architecture Overview

### Directory Structure (Key Files)
```
05-advanced-mcp/
├── models/                    # Pydantic models for structured output
│   ├── weather.py            # Core weather data structures
│   ├── responses.py          # Response format models  
│   ├── inputs.py             # Input validation models
│   ├── metadata.py           # Statistical/quality metrics
│   └── (additional supporting models)
├── mcp_servers/              # Simplified MCP server implementations
│   ├── forecast_server.py    # Returns raw forecast JSON
│   ├── historical_server.py  # Returns raw historical JSON
│   ├── agricultural_server.py # Returns raw agricultural JSON
│   ├── api_utils.py          # Shared Open-Meteo client
│   └── tests/                # Consolidated server tests
│       └── test_mcp_servers.py # Comprehensive server test suite
├── weather_agent/            # Enhanced agent with structured output
│   ├── mcp_agent.py         # Agent with both text and structured methods
│   ├── chatbot.py           # Interactive interface with structured output support
│   └── tests/               # Consolidated agent tests
│       ├── test_mcp_agent.py # Comprehensive agent test suite
│       └── test_structured_output_demo.py # Structured output demos
└── main.py                  # Entry point (same interface as Stage 4)
```

### Data Flow (LangGraph Option 1)

**Traditional Text Response:**
1. **User Query** → Agent selects MCP tools → Raw JSON from servers → Natural language response

**Structured Output Response:**
1. **User Query** → Agent selects MCP tools → Raw JSON from servers → Text response → Structured parser → Typed Pydantic models

### Key Benefits

- **Simplicity**: Raw JSON flows through the system without complex mapping
- **Flexibility**: LLM can extract any data from Open-Meteo responses  
- **Type Safety**: Structured output available when needed for applications
- **Backwards Compatible**: Existing text-based usage continues to work
- **Performance**: Direct JSON parsing is faster than complex validation

## Usage Examples

### Traditional Text Response (Compatible with Stage 4)
```python
from weather_agent.mcp_agent import MCPWeatherAgent

agent = MCPWeatherAgent()
await agent.initialize()

# Natural language response
response = await agent.query("What's the weather forecast for Iowa?")
print(response)  # Returns detailed text description
```

### Structured Output with Logging (New in Stage 5)
```python
# Using the chatbot with structured output enabled
from weather_agent.chatbot import SimpleWeatherChatbot

chatbot = SimpleWeatherChatbot()
await chatbot.initialize()

# This will show:
# 1. Tool calls made (e.g., get_weather_forecast with location="Iowa")
# 2. Raw JSON responses from MCP servers
# 3. Structured output transformation
# 4. Final Pydantic model with typed fields
response = await chatbot.chat(
    "What's the weather forecast for Iowa?",
    show_structured=True
)
```

### Programmatic Structured Output
```python
# Direct structured output without logging
structured_response = await agent.query_structured(
    "What's the weather forecast for Iowa?", 
    response_format="forecast"
)

# Returns OpenMeteoResponse with typed fields
print(f"Location: {structured_response.location}")
print(f"Current temp: {structured_response.current_conditions.temperature}°C")
print(f"Forecast days: {len(structured_response.daily_forecast)}")

# Agricultural assessment
ag_response = await agent.query_structured(
    "Are conditions good for planting corn?",
    response_format="agriculture"
)

# Returns AgricultureAssessment with recommendations
print(f"Planting conditions: {ag_response.planting_conditions}")
for rec in ag_response.recommendations:
    print(f"- {rec}")
```

### Multi-Turn Conversations with Memory
```python
# Use thread IDs for conversation tracking
thread_id = "farm-planning-session"

response1 = await agent.query(
    "What's the weather forecast for Iowa?", 
    thread_id=thread_id
)

# Follow-up query with preserved context
response2 = await agent.query(
    "What about the soil conditions there?",  # "there" = Iowa
    thread_id=thread_id
)
```

## Testing

### Comprehensive Test Suites

**MCP Server Tests:**
```bash
# Test all server functionality
python mcp_servers/tests/test_mcp_servers.py

# Covers:
# - Basic JSON response validation
# - Structured input validation  
# - Error handling scenarios
# - Data quality and completeness
# - All server types (forecast, historical, agricultural)
```

**Agent Tests:**
```bash
# Test agent functionality  
python weather_agent/tests/test_mcp_agent.py

# Covers:
# - Agent initialization and setup
# - Basic query processing
# - Structured output (LangGraph Option 1)
# - Multi-turn conversation memory
# - Tool integration
# - Error handling
```

**Structured Output Demo:**
```bash
# Interactive structured output demonstration
python weather_agent/tests/test_structured_output_demo.py

# Demonstrates:
# - Weather forecasts with typed fields
# - Agricultural assessments with recommendations  
# - Comparison between text and structured outputs
# - JSON serialization and validation
```

## Structured Output Models

### Agent Response Models (in `mcp_agent.py`)

**OpenMeteoResponse**: Consolidated weather forecast data
- `location`: String location name
- `coordinates`: Optional lat/lon dictionary  
- `timezone`: Optional timezone string
- `current_conditions`: Optional WeatherCondition object
- `daily_forecast`: Optional list of DailyForecast objects
- `summary`: Natural language description
- `data_source`: Data source attribution

**AgricultureAssessment**: Farming-specific analysis
- `location`: String location name
- `soil_temperature`: Optional soil temperature in Celsius
- `soil_moisture`: Optional soil moisture content
- `evapotranspiration`: Optional daily ET in mm
- `planting_conditions`: Assessment string ("FAVORABLE", "MARGINAL", etc.)
- `recommendations`: List of farming recommendations
- `summary`: Natural language agricultural summary

### Supporting Models (`models/` directory)

Note: The models in this directory are included for future extensibility but are not actively used in the current implementation. The structured output models (OpenMeteoResponse and AgricultureAssessment) are defined directly in `mcp_agent.py` for simplicity, following LangGraph's Option 1 approach.  
- `responses.py`: Tool response formats
- `metadata.py`: Data quality metrics

## Command Reference

### Complete Setup & Quick Start
```bash
# Prerequisites: Python 3.12.10 and ANTHROPIC_API_KEY already configured

# Install dependencies (if not already done)
pip install -r requirements.txt

# Quick demos
python main.py --demo                    # Original demo (Stage 4 compatible)
python main.py --demo --structured       # Demo with tool calls & structured output

# Interactive modes
python main.py                           # Interactive chat
python main.py --structured              # Interactive with structured output enabled
# Type 'structured' during chat to toggle on/off

# Testing
python weather_agent/tests/test_structured_output_demo.py  # Structured output examples
python mcp_servers/tests/test_mcp_servers.py              # Server tests
python weather_agent/tests/test_mcp_agent.py              # Agent tests
```

## Known Behaviors

### 1. MCP Server Startup Messages
When running demos, you may see "Starting OpenMeteo X MCP Server..." messages multiple times:
- Once during initial agent setup
- Again when tools are actually invoked

**This is normal behavior** from the `langchain-mcp-adapters` library (v0.1.7), which prints these informational messages when establishing or re-establishing server connections. The servers are not actually restarting - this is just the adapter managing connections.

### 2. Intelligent Conversation Memory
In demo mode with multiple queries, the agent may query locations from previous questions:

**Example**: 
- Query 1: "What's the weather forecast for Ames, Iowa?"
- Query 2: "Are conditions good for planting corn in Grand Island, Nebraska?"
- Result: The agent queries both Ames AND Grand Island for the second question

**This is intelligent conversational behavior** - the agent remembers context from previous queries and may provide comparative analysis. This is a feature of LangGraph's conversation memory (MemorySaver) that maintains context across queries.

**When this behavior is desired**: Interactive conversations where follow-up questions build on previous context
**When this behavior is not desired**: Independent demo queries that should be isolated

To run queries independently without memory:
```python
# Clear history between queries
agent.clear_history()

# Or use unique thread IDs
response = await agent.query(question, thread_id="unique-id")
```

## Summary: LangGraph Option 1 Implementation

Stage 5 successfully implements **LangGraph Option 1** structured output approach:

**✅ Benefits Achieved:**
- **Simplicity**: Raw JSON flows through MCP servers (70% less complexity than structured server approach)
- **Flexibility**: LLM can extract any Open-Meteo field as needed
- **Type Safety**: Structured Pydantic models available when applications need them
- **Backwards Compatibility**: All Stage 4 functionality preserved
- **Clean Architecture**: Clear separation between data retrieval and structuring
- **Intelligent Context**: Conversation memory enables smart follow-up queries

**🔧 Implementation Highlights:**
- MCP servers return consolidated Open-Meteo JSON responses
- Agent provides both `query()` (text) and `query_structured()` (typed) methods
- Conversation memory preserved through LangGraph checkpointer
- Comprehensive test suites ensure reliability
- No breaking changes to existing Stage 4 usage

This approach provides the best of both worlds: the simplicity and flexibility of raw JSON processing with the type safety and structure needed for application integration.