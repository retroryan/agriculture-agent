# This is still in progres and not complete!

# MCP Architecture: Introduction to Distributed AI Tools

## Overview

This module introduces the Model Context Protocol (MCP) paradigm and demonstrates a foundational step towards distributed AI systems. The Model Context Protocol (MCP) represents a paradigm shift in how AI agents interact with tools and external systems. Instead of tightly coupling tool implementations within the agent code, MCP enables a distributed architecture where tools run as independent servers that agents can discover and use dynamically.

**Important Note**: This implementation demonstrates core MCP concepts and builds a solid architectural foundation for real-world AI agent applications. A complete enterprise MCP system would require additional components like service discovery, advanced error handling, authentication, monitoring, and more sophisticated deployment patterns.

## Quick Start

**Prerequisites**: Python 3.12.10 (via pyenv), Anthropic API key in `.env`

```bash
# 1. Test the complete system
python 05-advanced-mcp/mcp_servers/test_mcp.py

# 2. Run interactive mode (default)
python 05-advanced-mcp/main.py

# 3. Run demo mode with example queries
python 05-advanced-mcp/main.py --demo

# 4. Run multi-turn demo scenarios
python 05-advanced-mcp/main.py --multi-turn-demo

# 5. Multi-turn demo scenarios are integrated into main.py
# Use: python 05-advanced-mcp/main.py --multi-turn-demo
```

## The Problem with Embedded Tools

Remember your tool-using agent from stage 3? Every tool was:
- Written in Python
- Embedded in your application
- Loaded into memory with your agent
- Updated only by redeploying everything

That's fine for demos. It becomes challenging at scale.

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

## Architecture: How MCP Works

### The stdio Subprocess Model

MCP servers run as independent processes, communicating via JSON-RPC over standard input/output:

```
┌─────────────┐     JSON-RPC/stdio     ┌─────────────────┐
│  LangGraph  │ ←───────────────────→ │ MCP Server      │
│    Agent    │                       │ (subprocess)    │
└─────────────┘                       └─────────────────┘
```

**Key Benefits:**
- **Process Isolation**: Server crashes don't affect the agent
- **Language Independence**: Servers can be written in any language
- **Scalability**: Easy to distribute servers across machines (future)
- **Security**: Process boundaries provide isolation
- **Performance**: Async HTTP calls prevent blocking in the event loop

### Communication Protocol

The MCP protocol follows a simple pattern:
1. **Subprocess Creation**: Agent spawns servers as child processes
2. **Tool Discovery**: Agent queries each server for available tools
3. **Tool Invocation**: Agent sends tool calls via JSON-RPC
4. **Automatic Cleanup**: Subprocesses terminate with parent

See `weather_agent/mcp_agent.py` for the complete implementation.

## MCP Server Implementation

### Server Structure

Each MCP server follows a standard pattern defined in the MCP specification:
- Tool registration with `@app.list_tools()`
- Tool execution with `@app.call_tool()`
- stdio transport for communication

### Available Servers

```
mcp_servers/
├── forecast_server.py      # Real-time weather forecasts
├── historical_server.py    # Historical weather analysis
├── agricultural_server.py  # Farm-specific conditions
├── api_utils.py           # Shared OpenMeteo API client
└── utils/                 # Common utilities
```

**Server Capabilities:**
- **Forecast Server**: Current conditions, 1-16 day forecasts
- **Historical Server**: Climate trends, seasonal comparisons  
- **Agricultural Server**: Soil moisture, crop recommendations

Each server is self-contained and can run independently. See the individual server files for implementation details.

### Module Overview

**Weather Agent Components:**
- `weather_agent/mcp_agent.py` - Manages MCP server connections and tool invocations
- `weather_agent/chatbot.py` - Interactive chat interface for the weather agent
- `weather_agent/demo_scenarios.py` - Showcases single/multi-agent queries and contextual conversations

**MCP Server Utilities:**
- `mcp_servers/api_utils.py` - Async OpenMeteo client with connection pooling
- `mcp_servers/parameters.py` - Defines common weather parameter groups
- `mcp_servers/weather_collections.py` - Pre-configured parameter sets for specific use cases
- `mcp_servers/utils/` - Helper utilities for date handling and display formatting

### Performance Optimization & Async Architecture

The MCP servers demonstrate **proper async patterns** with clean lifecycle management:

#### Clean Async Implementation
- **Pure async/await**: Removed all synchronous HTTP calls and mixed sync/async patterns
- **httpx-only**: Eliminated the `requests` library for consistent async behavior
- **No event loop hacks**: Removed problematic `run_async()` helper that created new event loops

#### Server Lifecycle Management
Each MCP server manages its own HTTP client instance with proper initialization and cleanup:

```python
# Server-level client (initialized once at startup)
weather_client: OpenMeteoClient = None

async def initialize_client():
    global weather_client
    weather_client = OpenMeteoClient()
    await weather_client.ensure_client()

async def main():
    await initialize_client()
    try:
        # Run MCP server
    finally:
        await cleanup_client()
```

#### Performance Benefits
- **Connection pooling**: Each server maintains a persistent HTTP client
- **50-70% faster responses**: Reusing connections vs creating per-request
- **Non-blocking I/O**: Multiple API calls execute concurrently
- **Resource efficiency**: No client creation/destruction overhead

#### Standalone Service Pattern
Each MCP server is self-contained with its own:
- HTTP client instance
- Lifecycle management
- Error handling
- Ready for independent deployment

This architecture demonstrates the right balance between tutorial simplicity and solid architectural patterns, showing how MCP servers should be built as truly independent services.

## LangGraph Integration

### Agent Configuration

The MCP integration uses LangGraph's `MultiServerMCPClient` to manage subprocess communication. The configuration is defined in `weather_agent/mcp_agent.py`:

- Server spawn configuration
- Tool discovery and registration
- Conversation context management
- Automatic subprocess cleanup

### Multi-Turn Conversations

The agent maintains conversation context across queries, enabling natural follow-up questions. The implementation demonstrates:
- Context retention between tool calls
- Cross-server coordination for complex queries
- Conversation history management

Multi-turn conversation capabilities are demonstrated through the `--multi-turn-demo` flag in `main.py`, which uses scenarios defined in `weather_agent/demo_scenarios.py`.

## Deployment Patterns

### Development Mode
Current implementation spawns MCP servers as managed subprocesses. The agent automatically:
- Spawns servers on initialization
- Manages process lifecycle
- Handles cleanup on exit

See `weather_agent/mcp_agent.py` for the subprocess management implementation.

## Key Implementation Files

### Core MCP Components
- `weather_agent/mcp_agent.py` - Main MCP client implementation
- `mcp_servers/` - Individual MCP server implementations
- `mcp_servers/test_mcp.py` - Integration testing

### Demo Applications
- `main.py` - Entry point with interactive/demo modes
- `weather_agent/demo_scenarios.py` - Pre-defined demo scenarios for multi-turn conversations

### Configuration and Utilities
- `mcp_servers/parameters.py` - Defines weather parameter groups (temperature, precipitation, agriculture)
- `mcp_servers/weather_collections.py` - Organized parameter collections for different use cases
- `mcp_servers/api_utils.py` - Async HTTP client for Open-Meteo API integration


## Examples and Testing

### Interactive Demos
Run the demos to see MCP in action:
- Basic weather queries with tool discovery
- Multi-turn conversations with context retention
- Cross-server coordination for complex analysis

### Testing Framework
The test suite in `mcp_servers/test_mcp.py` validates:
- MCP server startup and connectivity
- Tool discovery and invocation
- Error handling and cleanup

## Next Steps

1. **Explore the code**: Examine the MCP server implementations in `mcp_servers/`
2. **Run the demos**: Try different interaction patterns with the demo scripts
3. **Build your own**: Create custom MCP servers for your domain

## Technical Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [LangGraph MCP Support](https://langchain-ai.github.io/langgraph/agents/mcp/)
- Implementation examples in this module

---

This architecture introduces the foundational concepts of MCP and demonstrates how it can enable more modular AI applications. While this implementation shows the core principles and builds a solid architectural foundation for real-world AI agent applications, a complete enterprise MCP system would require additional work including robust service discovery, comprehensive error handling, security frameworks, monitoring systems, and advanced deployment patterns.