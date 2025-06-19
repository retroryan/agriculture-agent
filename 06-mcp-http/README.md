# FastMCP + LangGraph Integration Tutorial

## Brief Overview

This step was an entirely new sample to learn how to work with LangGraph and LangGraph MCP Integration and shows how to build FastMCP Servers and call them from LangGraph with the LangGraph Adapter. Unlike stages 02-05 which progressively built the weather demo, this stage explores the critical integration patterns needed to properly connect MCP servers with LangGraph agents.

## Quick Start

Assumes you already have Python 3.12.10 and `.env` file with your Anthropic API key configured.

```bash
# Terminal 1: Start the FastMCP server
python serializer.py

# Terminal 2: Run the unified demo
python demo.py
```

The demo provides three modes:
1. Full agent demo with example queries
2. Minimal tool usage example  
3. Interactive chat mode

## Architecture Overview

### Core Components

**FastMCP Server** (`serializer.py`):
```python
# Creates HTTP server with custom YAML serialization
server = Server("fastmcp-demo-server", custom_serializer=custom_dict_serializer)

@server.tool
def get_example_data() -> dict:
    """Fetch example data from the weather station."""
    return {
        "name": "Downtown Weather Station",
        "temperature": 22.5,
        "humidity": 65,
        "conditions": "Partly Cloudy",
        "timestamp": datetime.now().isoformat()
    }
```
Runs on `http://127.0.0.1:7070/mcp` with streamable HTTP transport.

**LangGraph Agent** (`langgraph_agent.py`):
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# The critical pattern - using official MCP adapters
self.mcp_client = MultiServerMCPClient({
    "fastmcp": {
        "url": "http://127.0.0.1:7070/mcp",
        "transport": "streamable_http"
    }
})
tools = await self.mcp_client.get_tools()
self.agent = create_react_agent(self.llm, tools)
```

**Simple Alternative** (`simple_client.py`):
For cases where LangGraph complexity isn't needed, demonstrates direct Claude + MCP integration with manual tool wrapping.

### Communication Flow
```
User Query → LangGraph Agent
    ├── Parse with Claude AI
    ├── Discover tools via MultiServerMCPClient
    ├── Execute tools through MCP protocol
    │   └── HTTP Request → FastMCP Server → YAML Response
    ├── Process results
    └── Generate natural language response
```

## Best Practices for Working with LangGraph and MCP Integration

### 1. Use Official Adapters
Always use `langchain-mcp-adapters` instead of manually wrapping MCP calls:
```python
# ✅ CORRECT - Use official adapters
from langchain_mcp_adapters.client import MultiServerMCPClient

# ❌ WRONG - Manual tool wrapping
@tool
async def my_mcp_tool():
    async with Client(...) as client:
        return await client.call_tool(...)
```

### 2. Let LangGraph Handle Message Flow
Use pre-built components that manage Claude's strict message ordering:
```python
# ✅ CORRECT - Pre-built agent handles message flow
agent = create_react_agent(llm, tools)

# ❌ WRONG - Custom graph with manual state management
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
```

### 3. Proper Error Handling
See `langgraph_agent.py:73-84` for connection validation:
```python
async def _test_connection(self):
    """Test connection to MCP server"""
    try:
        await self.mcp_client.__aenter__()
        await self.mcp_client.__aexit__(None, None, None)
        return True
    except Exception as e:
        print(f"\n❌ Failed to connect to MCP server: {e}")
        return False
```

### 4. Clean Resource Management
Always use context managers or proper cleanup (see `langgraph_agent.py:86-93`):
```python
async def __aexit__(self, exc_type, exc_val, exc_tb):
    if self.mcp_client:
        await self.mcp_client.__aexit__(exc_type, exc_val, exc_tb)
```

### 5. Tool Discovery Pattern
Let the framework discover tools dynamically rather than hardcoding (see `langgraph_agent.py:58-66`):
```python
tools = await self.mcp_client.get_tools()
if not tools:
    print("⚠️  No tools discovered from MCP server")
```

## Links to Official Documentation

- **Using MCP in LangGraph agents**: https://langchain-ai.github.io/langgraph/agents/mcp/
- **LangGraph MCP server concepts**: https://langchain-ai.github.io/langgraph/concepts/server-mcp/
- **Exposing agents as MCP tools**: https://langchain-ai.github.io/langgraph/concepts/server-mcp/#exposing-an-agent-as-mcp-tool
- **FastMCP Documentation**: Check the FastMCP repository for server implementation details

## The Real Problem Discovered and How To Properly Integrate with LangGraph

### What We Initially Tried (And Why It Failed)

The first implementation attempt manually wrapped MCP calls as LangChain tools and built a custom StateGraph. This approach failed because:

1. **Manual Tool Wrapping Created Disconnect**: 
   ```python
   # ❌ WRONG - From initial broken attempt
   @tool
   async def get_example_data():
       async with Client("http://127.0.0.1:7070/mcp") as client:
           result = await client.call_tool("get_example_data", {})
           return result[0].text
   ```
   This creates a layer between LangGraph and the actual MCP protocol, breaking tool management.

2. **Custom Graph Construction Required Manual Message Flow**:
   ```python
   # ❌ WRONG - Manual state management
   workflow = StateGraph(AgentState)
   workflow.add_node("agent", agent_node)
   workflow.add_node("tools", tool_node)
   ```
   This required managing message accumulation and ordering manually.

3. **Message Ordering Violations**: Claude requires tool calls to immediately precede tool results. Manual management led to invalid sequences where ToolMessages appeared without corresponding AIMessage tool calls.

### The Correct Solution

As documented in `workflow.md:276-314`, the proper approach uses the official MCP adapters:

```python
# ✅ CORRECT - From langgraph_agent.py:48-52
from langchain_mcp_adapters.client import MultiServerMCPClient

self.mcp_client = MultiServerMCPClient({
    "fastmcp": {
        "url": "http://127.0.0.1:7070/mcp",
        "transport": "streamable_http"
    }
})
```

This solution works because:
- The adapter handles all protocol-level communication
- Pre-built agents manage message flow correctly
- Tool discovery happens automatically
- Claude's message ordering requirements are respected

## Key Differences and Why the Original Approach Broke

### 1. Import Path Confusion
The correct import was not obvious:
```python
# ✅ CORRECT - Note the specific module path
from langchain_mcp_adapters.client import MultiServerMCPClient

# ❌ WRONG - These imports don't exist
from langchain_mcp_adapters import MultiServerMCPClient  # No!
from langchain_mcp import MultiServerMCPClient  # Also no!
```

### 2. Protocol Layer Abstraction
- **Original Approach**: Direct MCP client calls wrapped in tools → Manual message handling → State conflicts
- **Correct Approach**: MCP Server → MCP Adapters → LangChain Tools → LangGraph Agent

Each layer properly abstracts the complexity below it.

### 3. Message Flow Management
As shown in `simple_client.py:91-112`, even the simple approach requires careful message management:
```python
# Create fresh message list for each query to avoid context issues
messages = [
    SystemMessage(content="You are a helpful assistant..."),
    HumanMessage(content=query)
]
```

The LangGraph adapter handles this automatically, preventing the accumulation issues that broke the manual approach.

### 4. Debugging Insights
From `workflow.md:395-429`, the key lessons learned:
- Start with the simplest implementation (`client_serializer.py`)
- Verify each component independently
- Use official examples as reference
- Check for existing adapters before building custom integrations

### 5. Why It Matters
The journey from broken to working implementation demonstrates:
- **Complexity of Protocol Integration**: MCP, LangChain, and Claude each have specific requirements
- **Value of Official Libraries**: They encapsulate edge cases and best practices
- **Importance of Documentation**: The solution was clearly documented but required careful reading

## Summary

This tutorial demonstrates the critical importance of using official integration libraries when building LangGraph + MCP applications. The `langchain-mcp-adapters` library exists specifically to handle the complex interaction between MCP servers and LangGraph agents, managing message flow, tool discovery, and protocol translation that would be error-prone to implement manually.

The final implementation in `langgraph_agent.py` is not just simpler than manual attempts, but also more robust because it leverages the collective knowledge embedded in the official libraries. When building AI applications with multiple protocol layers, always check for official adapters before attempting custom integrations.