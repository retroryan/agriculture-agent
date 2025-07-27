# MCP Architecture with Unified Model Interface

## Quick Start

```bash
# Install dependencies
cd 04-mcp-architecture
pip install -r requirements.txt

# Run tests to verify setup
python test_unified_model.py

# Interactive weather assistant
python main.py

# Demo mode with example queries
python main.py --demo

# Multi-turn conversation demo
python main.py --multi-turn-demo
```

## Project Overview

This directory demonstrates the Model Context Protocol (MCP) architecture with LangChain's unified model interface for distributed AI tool systems. MCP represents a paradigm shift from embedded tools to distributed, process-isolated services that AI agents can discover and use dynamically.

## Architecture

### MCP Server (Process-Isolated Tools)
- **Unified Weather Server** (`mcp_servers/weather_server.py`): Consolidated server providing:
  - Current and future weather forecasts via Open-Meteo API
  - Historical weather analysis and climate trends
  - Agricultural conditions including soil moisture, evapotranspiration, and growing degree days

### Weather Agent (LangGraph Orchestrator)
- **MCP Client** (`weather_agent/mcp_agent.py`): Manages subprocess lifecycle and tool discovery
- **Interactive Interface** (`weather_agent/chatbot.py`): Command-line interface with conversation history
- **Demo Scenarios** (`weather_agent/demo_scenarios.py`): Multi-turn conversation examples

### Key Components
- **Async Optimization**: Non-blocking HTTP calls with httpx for better performance
- **Tool Discovery**: Dynamic discovery of available tools from MCP servers
- **Conversation Memory**: Maintains context across multiple queries
- **Process Isolation**: Each MCP server runs as an independent subprocess

## Unique LangGraph Features Demonstrated

### 1. Dynamic Tool Binding
```python
# Tools are discovered at runtime from MCP servers
tools = await self.mcp_client.get_tools()
self.agent = create_react_agent(
    self.llm.bind_tools(tools),
    tools
)
```

### 2. Stateful Conversation Management
- Full conversation history maintained across queries
- Context preservation for follow-up questions
- Clear history method for new topics

### 3. Async Agent Operations
```python
# Non-blocking agent invocation with timeout
result = await asyncio.wait_for(
    self.agent.ainvoke({"messages": self.messages}),
    timeout=120.0
)
```

### 4. Tool Call Tracking
- Automatic logging of which MCP tools were used
- Transparent visibility into agent decision-making
- Performance metrics for tool execution

### 5. MultiServerMCPClient Integration
- Seamless management of multiple MCP server subprocesses
- Automatic cleanup on exit
- Unified tool interface despite distributed backends

## MCP Architecture Benefits

1. **Process Isolation**: MCP servers crash independently without affecting the agent
2. **Language Agnostic**: Tools can be written in any language that supports stdio
3. **Dynamic Discovery**: New tools available without restarting the agent
4. **Scalability**: Distribute tools across multiple machines if needed
5. **Version Independence**: Update tools without touching agent code

## Testing

The comprehensive test suite (`test_unified_model.py`) validates:
- MCP server startup and tool discovery
- Individual tool functionality (forecast, historical, agricultural)
- Multi-turn conversation context preservation
- Concurrent request handling
- Tool composition across servers

Run tests:
```bash
python test_unified_model.py
```

## Model Configuration

The unified model interface allows runtime model switching:

```bash
# Use default model (Claude 3.5 Sonnet)
python main.py

# Use a different model via environment variable
MODEL_NAME=claude-3-haiku-20240307 python main.py
```

## Performance Considerations

- **Startup Time**: ~0.3s to initialize all MCP servers
- **Average Response Time**: ~9s for complex queries requiring multiple tools
- **Concurrent Requests**: Successfully handles parallel queries
- **Memory Usage**: Process isolation keeps memory footprint manageable

## Comparison with Stage 3

| Feature | Stage 3 (Embedded Tools) | Stage 4 (MCP Architecture) |
|---------|-------------------------|---------------------------|
| Tool Location | In-process Python functions | Subprocess servers |
| Tool Discovery | Import-time | Runtime via JSON-RPC |
| Failure Isolation | Crash affects entire app | Isolated failures |
| Language Support | Python only | Any language |
| Update Process | Redeploy application | Update individual servers |
| Scalability | Vertical only | Horizontal + Vertical |

## Next Steps

This architecture provides the foundation for:
- Adding authentication and authorization to MCP servers
- Implementing service discovery for dynamic server registration
- Creating monitoring and observability for distributed tools
- Building specialized MCP servers for your domain
- Migrating to Stage 5 with structured output support

The MCP pattern demonstrated here is production-ready for many use cases while providing a clear path to enterprise-scale distributed AI systems.