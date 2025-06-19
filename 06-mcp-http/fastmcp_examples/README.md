# FastMCP + LangGraph Examples

This repository demonstrates integrating FastMCP (Model Context Protocol) servers with LangChain and Claude for intelligent agent workflows.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file with your Claude API key:
```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
```

### 3. Run the Examples

#### Easiest Way - Use Main Entry Point
```bash
# Run the main script for guided setup
python main.py
```

#### Manual Setup

**Basic MCP Server + Client:**
```bash
# Terminal 1: Start the serializer server
python servers/serializer.py

# Terminal 2: Run the basic client
python client/client_complex_inputs.py
```

**MCP + Claude Integration Demo:**
```bash
# Terminal 1: Start the serializer server (if not already running)
python servers/serializer.py

# Terminal 2: Run the Claude-powered demo
python client/demo.py
```

## Project Structure

```
fastmcp_examples/
├── main.py                    # Main entry point with guided setup
├── servers/                   # MCP server implementations
│   ├── serializer.py         # YAML serialization server
│   ├── complex_inputs.py     # Pydantic validation server  
│   ├── config_server.py      # CLI configuration server
│   └── screenshot.py         # System integration server
├── client/                    # Client implementations and demos
│   ├── demo.py              # Main Claude + MCP integration demo
│   └── client_complex_inputs.py # Basic MCP client example
├── requirements.txt          # Python dependencies
├── CLAUDE.md                # Detailed project documentation
└── README.md                # This file
```

## Architecture Overview

### Main Entry Point (`main.py`)
- **Recommended starting point** - orchestrates server startup and client execution
- Provides guided menu for different demo modes
- Handles server lifecycle management
- Checks requirements and environment setup

### MCP Servers (`servers/`)
- **serializer.py**: Runs on `http://127.0.0.1:8000/mcp`, exposes YAML-formatted data tools
- **complex_inputs.py**: Demonstrates Pydantic validation with complex nested models
- **config_server.py**: Shows command-line argument integration
- **screenshot.py**: System integration example using pyautogui

### Clients (`client/`)
- **demo.py**: **Main demo** - Claude + MCP integration with multiple modes:
  1. Simple single-turn demo (without LangGraph)
  2. Full agent demo (with LangGraph + official MCP adapters)  
  3. Interactive chat mode
- **client_complex_inputs.py**: Basic MCP client without AI integration

## Example Output

When running `python main.py` and selecting the demo:
```
FastMCP Examples
================================================================
Demonstrates FastMCP server-client integration patterns
----------------------------------------------------------------

Available options:
1. Run serializer server + demo client
2. Run complex inputs server + client
3. Start serializer server only
4. Start complex inputs server only
5. Run demo client only (requires running server)
6. Exit

Starting serializer server...
✅ serializer server started (PID: 12345)

Simple Single-Turn Demo (Without LangGraph)
============================================================

User: Can you fetch the data from the MCP server?
Claude: Let me fetch that data for you...

Data retrieved:
name: Test
value: 123
status: true

Claude: The data fetched from the MCP server contains three properties:
- name: "Test" 
- value: 123
- status: true
```

## Key Components

1. **FastMCP**: Framework for creating MCP servers with tool exposure
2. **LangChain**: Orchestration framework for LLM applications
3. **Claude**: Anthropic's LLM that intelligently decides when to use tools
4. **Tool Pattern**: Claude analyzes user queries and autonomously calls MCP tools when needed

## Documentation Resources

### LangGraph MCP Integration
The proper way to integrate MCP servers with LangGraph is documented at:
- **Using MCP in LangGraph agents**: https://langchain-ai.github.io/langgraph/agents/mcp/
- **LangGraph MCP concepts**: https://langchain-ai.github.io/langgraph/concepts/server-mcp/
- **LangChain MCP Adapters**: The key library that makes it work: `langchain-mcp-adapters`

These resources explain how to properly use the `MultiServerMCPClient` from `langchain_mcp_adapters.client` to integrate MCP tools with LangGraph agents.

## Troubleshooting

- Ensure the MCP server is running before starting clients
- Check that your `.env` file contains a valid Anthropic API key
- The server runs on port 8000 by default - ensure it's available
- For LangGraph integration issues, see `darn-mcp-client.md` for detailed analysis

## Testing and Running

### Option 1: Use Main Script (Recommended)
```bash
python main.py
```
This provides a guided menu to run different server-client combinations.

### Option 2: Manual Testing
```bash
# Test serializer server + demo
python servers/serializer.py &
python client/demo.py

# Test complex inputs server + client  
python servers/complex_inputs.py &
python client/client_complex_inputs.py
```

### Option 3: Individual Components
```bash
# Test individual servers
python servers/config_server.py --name MyServer --debug
python servers/screenshot.py
```

## Additional Features

The repository includes several specialized servers:
- **Complex Inputs**: Demonstrates Pydantic validation with nested models (ShrimpTank example)
- **Config Server**: Shows command-line configuration with argparse integration
- **Screenshot Server**: System integration example using pyautogui for screen capture

See `CLAUDE.md` for detailed project documentation and development guidelines.