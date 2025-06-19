# Simple FastMCP + LangGraph Integration

A clean, minimal example demonstrating how to integrate FastMCP servers with LangGraph agents for building AI-powered applications.

## 🎯 What This Demo Shows

This example demonstrates:
- **FastMCP Server**: HTTP-based tool server with custom YAML serialization
- **LangGraph Integration**: AI agent that discovers and uses FastMCP tools using official MCP adapters
- **Simple Alternative**: Direct Claude + MCP integration without LangGraph (avoids message ordering issues)
- **Practical Tools**: Weather data and comfort index calculations
- **Clean Architecture**: Separation between tool server and AI agent

## 📁 Project Structure

```
08-simple-fastmcp/
├── serializer.py         # FastMCP server with weather tools
├── client_serializer.py  # Basic FastMCP client example
├── langgraph_agent.py    # LangGraph agent using official MCP adapters (RECOMMENDED)
├── simple_client.py      # Simple Claude + MCP integration (fallback option)
├── demo.py              # Interactive demos and examples
├── workflow.md          # Detailed architecture documentation
└── requirements.txt     # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

1. Python 3.12.10 (via pyenv)
2. Anthropic API key in `.env` file:
   ```bash
   echo 'ANTHROPIC_API_KEY=your-key-here' > .env
   ```

### Installation

```bash
pip install -r requirements.txt
```

### Running the Demo

1. **Start the FastMCP server** (in terminal 1):
   ```bash
   python serializer.py
   ```
   The server will start on `http://127.0.0.1:7070/mcp`

2. **Run the demo** (in terminal 2):
   ```bash
   python demo.py
   ```
   Choose from:
   - Option 1: Full agent demo with example queries
   - Option 2: Minimal tool usage example
   - Option 3: Interactive chat mode

### Individual Components

**Test the FastMCP client only:**
```bash
python client_serializer.py
```

**Run the LangGraph agent directly:**
```bash
python langgraph_agent.py
```

**Run the simple client (no LangGraph):**
```bash
python simple_client.py
```

## 🛠️ Available Tools

The FastMCP server exposes two tools:

1. **get_example_data**: Returns weather station data
   - Output: Weather station name, temperature, humidity, conditions, timestamp

2. **calculate_comfort_index**: Calculates comfort based on temperature and humidity
   - Input: temperature (float), humidity (float)
   - Output: Comfort score and description

## 🏗️ Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────┐
│ LangGraph Agent │ ←──────────→  │ FastMCP Server   │
│                 │   Port 7070    │                  │
│ - Claude AI     │               │ - Weather tools  │
│ - Tool discovery│               │ - YAML output    │
│ - React pattern │               │ - HTTP transport │
└─────────────────┘               └──────────────────┘
```

### Key Features

- **HTTP Transport**: No subprocess management needed
- **Tool Discovery**: Agent automatically finds available tools
- **Custom Serialization**: Demonstrates YAML output format
- **Clean Separation**: Server and agent can run independently
- **Official MCP Adapters**: Uses `langchain-mcp-adapters` for proper message handling
- **Fallback Option**: Simple client for when LangGraph has issues
- **Type Safety**: Full type hints throughout

## 💡 Example Interactions

```
You: What weather data is available?
Agent: I'll check what weather data is available from the station...
       [Shows current temperature, humidity, and conditions]

You: Is it comfortable at 25°C and 70% humidity?
Agent: I'll calculate the comfort index for those conditions...
       [Returns comfort score and description]
```

## 🔧 Extending the Demo

To add new tools:

1. Add a new `@server.tool` function in `serializer.py`
2. Restart the server
3. The agent will automatically discover and use the new tool

Example:
```python
@server.tool
def get_forecast(days: int = 3) -> dict:
    """Get weather forecast for the next N days."""
    # Your implementation here
    return {"forecast": [...]}
```

## 📚 Learn More

- See `workflow.md` for detailed architecture documentation
- Check stages 04-06 for more complex MCP implementations
- Visit the FastMCP documentation for advanced features

## 🎓 Educational Value

This demo teaches:
- How to build HTTP-based tool servers with FastMCP
- Integration patterns between LLMs and external tools
- Clean separation of concerns in AI applications
- Practical use of LangGraph for agent orchestration