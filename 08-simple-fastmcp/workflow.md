# Simple FastMCP + LangGraph Integration Workflow

## Overview
This example demonstrates how to integrate FastMCP servers with LangGraph agents, building on the MCP architecture from stage 04 but using FastMCP's HTTP transport instead of stdio subprocesses.

## Architecture

### Key Components

1. **FastMCP Server** (`serializer.py`)
   - Runs as an HTTP server on port 7070
   - Exposes a simple demo tool via MCP protocol
   - Uses FastMCP's streamable-http transport
   - Provides YAML-serialized responses with custom serialization

2. **LangGraph Agent** (`langgraph_agent.py`)
   - Creates a stateful agent using LangGraph
   - Connects to FastMCP server via HTTP client
   - Maintains conversation context
   - Orchestrates tool calls based on user queries

3. **FastMCP Client** (`client_serializer.py`)
   - Example client showing HTTP communication with the server
   - Demonstrates calling the `get_example_data` tool
   - Shows how to handle YAML-serialized responses

## Workflow

### 1. Server Startup
```
FastMCP Demo Server (serializer.py)
├── Start HTTP server on localhost:7070/mcp
├── Register demo tool
│   └── get_example_data
├── Configure YAML serializer
└── Wait for client connections
```

### 2. Agent Initialization
```
LangGraph Agent
├── Create ChatAnthropic LLM instance
├── Initialize FastMCP client (same approach as client_serializer.py)
│   └── Client("http://127.0.0.1:7070/mcp")
├── Connect to server via HTTP
├── Discover available tools
├── Create React agent with tools
└── Ready for queries
```

### 3. Query Processing Flow
```
User Query → LangGraph Agent
    ├── Parse query with LLM
    ├── Determine required tools
    ├── Call FastMCP client
    │   ├── Send HTTP request to server
    │   ├── Server executes tool
    │   └── Return structured response
    ├── Process tool results
    └── Generate natural language response
```

### 4. Tool Communication
```
LangGraph Tool Call
    ↓
FastMCP Client (HTTP)
    ↓
FastMCP Server (serializer.py - already implemented)
    ├── HTTP endpoint: http://127.0.0.1:7070/mcp
    ├── Tool: get_example_data
    └── Returns YAML-serialized response
    ↓
Structured Response (YAML/JSON)
    ↓
LangGraph Agent
    ↓
User Response
```

## Key Differences from Stage 04

1. **Transport Method**
   - Stage 04: stdio subprocesses with JSON-RPC
   - Stage 08: HTTP transport with FastMCP

2. **Server Management**
   - Stage 04: LangGraph spawns/manages subprocesses
   - Stage 08: Server runs independently, agent connects via HTTP

3. **Tool Definition**
   - Stage 04: MCP protocol with manual tool registration
   - Stage 08: FastMCP's @mcp.tool decorator for simpler definition

4. **Serialization**
   - Stage 04: JSON-only responses
   - Stage 08: Custom serialization (e.g., YAML) with FastMCP

## Implementation Steps

1. **FastMCP Server** (`serializer.py`)
   - Already implemented with `get_example_data` tool
   - Uses @mcp.tool decorator
   - Custom YAML serializer configured
   - Runs with HTTP transport on port 7070

2. **FastMCP Client** (`client_serializer.py`)
   - Already implemented example client
   - Shows connection to http://127.0.0.1:7070/mcp
   - Demonstrates tool invocation
   - Handles YAML response parsing

3. **LangGraph Integration** (to be implemented)
   - Adapt client_serializer.py for LangGraph tool format
   - Initialize with Claude LLM
   - Create React agent with discovered tools
   - Implement conversation management

4. **Create Demo Interface** (to be implemented)
   - Interactive chat loop
   - Simple demo scenarios
   - Error handling
   - Graceful shutdown

## Benefits of This Approach

1. **Simpler Server Development**: FastMCP's decorators reduce boilerplate
2. **Better Separation**: Server can run independently of agent
3. **Easier Testing**: Can test server and agent separately
4. **Flexible Deployment**: Server and agent can run on different machines
5. **Custom Serialization**: Support for different output formats (YAML, XML, etc.)

## Example Usage

```python
# Start the server
python serializer.py

# Test with the example client
python client_serializer.py

# Future: Run the LangGraph agent
python langgraph_agent.py
```

## Implementation Status

### ✅ Completed
1. **Dependencies** (`requirements.txt`)
   ```
   # Core dependencies
   fastmcp>=0.1.0              # Version 2.8.1 installed - HTTP-based MCP protocol
   langgraph>=0.2.0            # Version 0.4.8 installed - Stateful agent orchestration
   langchain>=0.3.0            # Version 0.3.25 installed - LLM framework
   langchain-anthropic>=0.3.0  # Version 0.3.15 installed - Claude integration
   anthropic>=0.39.0           # Version 0.53.0 installed - Direct Claude API access
   
   # Serialization support
   pyyaml>=6.0.1               # Version 6.0.2 installed - For YAML serialization demo
   
   # Async HTTP client
   httpx>=0.27.0               # Version 0.28.1 installed - Modern async HTTP
   
   # Environment management
   python-dotenv>=1.0.0        # Version 1.1.0 installed - For .env file support
   
   # Type hints and validation
   pydantic>=2.0.0             # Version 2.11.5 installed - Data validation
   ```

2. **Existing FastMCP Server** (`serializer.py`)
   ```python
   # Key implementation details:
   - Uses FastMCP's @server.tool decorator for simple tool definition
   - Custom YAML serializer function: custom_dict_serializer()
   - Single tool: get_example_data() returning {"name": "Test", "value": 123, "status": True}
   - Runs HTTP server on port 7070 at path /mcp
   - Transport: "streamable-http" for remote client connections
   ```

3. **Existing FastMCP Client** (`client_serializer.py`)
   ```python
   # Key implementation details:
   - Async client using: async with Client("http://127.0.0.1:7070/mcp")
   - Calls tool with: await client.call_tool("get_example_data", {})
   - Expects YAML-serialized response in result[0].text
   - Simple asyncio.run(main()) entry point
   ```

4. **Documentation Updates**
   - All port references updated from 8000 to 7070
   - Architecture diagrams reflect current implementation
   - Clear separation between completed and pending work

### 📋 To Do
1. **Create LangGraph Agent** (`langgraph_agent.py`)
   ```python
   # Planned implementation:
   - Import: from langchain_anthropic import ChatAnthropic
   - Import: from langgraph.prebuilt import create_react_agent
   - Import: from fastmcp import Client
   - Create async tool wrapper that:
     * Connects to FastMCP server at http://127.0.0.1:7070/mcp
     * Calls get_example_data tool
     * Returns YAML response as string
   - Initialize Claude with: ChatAnthropic(model="claude-3-5-sonnet-20241022")
   - Create React agent with the FastMCP tool
   - Implement chat loop with conversation history
   ```

2. **Integration Testing**
   - Verify FastMCP server starts correctly
   - Test tool discovery via client.list_tools()
   - Validate YAML response parsing
   - Test multi-turn conversations

3. **Documentation Updates**
   - Add complete usage instructions
   - Document architectural benefits over stdio approach
   - Create troubleshooting guide

## Implementation Details

### Current Architecture
```
┌─────────────────┐     HTTP      ┌──────────────────┐
│ LangGraph Agent │ ←──────────→  │ FastMCP Server   │
│                 │   Port 7070    │ (serializer.py)  │
│ - Claude LLM    │               │ - YAML output    │
│ - React pattern │               │ - @server.tool   │
│ - Tool wrapper  │               │ - HTTP transport │
└─────────────────┘               └──────────────────┘
```

### Key Design Decisions
1. **Port Configuration**: Using 7070 (changed from 8000 due to port conflict)
2. **Serialization**: YAML format demonstrates FastMCP's flexibility beyond JSON
3. **Tool Pattern**: Single demonstration tool returning structured data
4. **Client Pattern**: Async context manager for clean resource management

### Environment Setup Required
```bash
# Before running:
1. Ensure Python 3.12.10 via pyenv
2. Create .env file with: ANTHROPIC_API_KEY=<your-key>
3. Install deps: pip install -r requirements.txt
```

### Next Implementation Session Should Start With:
1. Start the FastMCP server: `python serializer.py`
2. Test with existing client: `python client_serializer.py`
3. Begin implementing `langgraph_agent.py` following the pattern above
4. Focus on creating a simple tool wrapper first, then add LangGraph integration