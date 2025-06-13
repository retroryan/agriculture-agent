# 03-tools-integration: Adding AI Capabilities with Tools

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic tools example
python 03-tools-integration/basic_tools/chatbot_with_tools.py

# Try external tools example  
python 03-tools-integration/external_tools/chatbot_with_fetch.py

# See tool chaining in action
python 03-tools-integration/main.py
```

## Overview

This module demonstrates how to extend LangGraph agents with tools - functions that agents can call to perform specific tasks. Tools bridge AI reasoning with real-world actions, enabling agents to calculate, fetch data, and interact with external systems.

The tutorial progresses through three stages:
1. **Basic Tools** - Simple utilities without external dependencies
2. **External Tools** - Web fetching and API interactions  
3. **Tool Chaining** - Combining tools for complex operations

## What Are Tools?

Tools are Python functions decorated with `@tool` that agents can invoke. They enable:
- Mathematical calculations
- Text processing and analysis
- Web content fetching
- API interactions
- Domain-specific logic

Every tool follows this pattern:
```python
from langchain_core.tools import tool

@tool
def tool_name(param: type) -> return_type:
    """Description for the LLM to understand when to use this tool."""
    # Implementation
    return result
```

## Module Structure

```
03-tools-integration/
├── basic_tools/              # Stage 1: Simple utility tools
│   ├── tools.py             # Math, text, dates, simulated weather
│   └── chatbot_with_tools.py # Interactive demo
├── external_tools/           # Stage 2: Web integration tools  
│   ├── fetch_tool.py        # Web fetching capabilities
│   └── chatbot_with_fetch.py # Interactive demo
├── main.py                   # Stage 3: Tool chaining example
└── OVERVIEW.md              # This file
```

## Stage 1: Basic Tools

Start here to understand tool fundamentals without external dependencies.

### Available Basic Tools

| Tool | Purpose | Example Use |
|------|---------|------------|
| `add_numbers` | Add two integers | "What's 42 plus 17?" |
| `multiply_numbers` | Multiply two floats | "Calculate 15.5 times 3.2" |
| `get_simulated_weather` | Weather data (simulated) | "What's the weather in Paris?" |
| `count_words` | Text analysis | "How many words in this text?" |
| `get_current_time` | Current date/time | "What time is it?" |
| `calculate_days_between` | Date calculations | "Days between Jan 1 and Dec 31?" |
| `reverse_text` | Text reversal | "Reverse this message" |
| `agricultural_advice` | Farming tips | "Advice for corn in dry conditions?" |

### Running Basic Tools

```bash
python 03-tools-integration/basic_tools/chatbot_with_tools.py
```

Example interactions:
- "Add 25 and 17"
- "What's the simulated weather for Berlin?"
- "How many words are in 'The quick brown fox jumps'?"
- "Calculate days between 2024-01-01 and 2024-12-31"

**Note**: Weather data is simulated for demo purposes. Real weather API integration comes in later modules.

## Stage 2: External Tools

After mastering basic tools, explore web content fetching.

### Available External Tools

| Tool | Purpose | Example Use |
|------|---------|------------|
| `fetch_webpage` | Get web content as markdown | "Fetch content from example.com" |
| `fetch_raw_content` | Get raw API responses | "Get JSON from an API endpoint" |

### Running External Tools

```bash
python 03-tools-integration/external_tools/chatbot_with_fetch.py
```

Example interactions:
- "What information is on https://example.com?"
- "Fetch and analyze content from [URL]"
- "Get the raw JSON response from [API endpoint]"

### How Fetch Tools Work

1. **fetch_webpage**: 
   - Retrieves HTML content
   - Extracts readable text using readabilipy
   - Converts to clean markdown format
   - Handles errors gracefully

2. **fetch_raw_content**:
   - Returns exact response without processing
   - Useful for API responses, JSON, plain text
   - Preserves formatting

## Stage 3: Tool Chaining

See how tools work together in `main.py` - review basic and external tools first!

```bash
python 03-tools-integration/main.py
```

This demonstrates:
- Fetching web content
- Analyzing it with text tools  
- Combining results for insights

## Integration with LangGraph

Tools integrate seamlessly with LangGraph's architecture:

```python
# 1. Bind tools to model
model = ChatAnthropic(model="claude-3-5-sonnet").bind_tools(tools)

# 2. Create tool node
tool_node = ToolNode(tools=tools)

# 3. Add to graph
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,  # Decides if tools needed
    {"tools": "tools", END: END}
)
```

### Execution Flow

1. User sends message → 2. Agent analyzes request → 3. Decides if tools needed → 4. Calls appropriate tools → 5. Processes results → 6. Returns response

## Common Patterns

### Tool Selection
Agents automatically select tools based on:
- Query analysis
- Tool descriptions  
- Parameter matching
- Context understanding

### Error Handling
Tools return friendly error messages instead of crashing:
```python
try:
    # Tool logic
except Exception as e:
    return f"Error: {str(e)}"
```

### Tool Composition
Agents chain multiple tools:
```
User: "Analyze the weather forecast from this website"
Agent: fetch_webpage(url) → count_words(content) → get_simulated_weather()
```

## Best Practices

1. **Clear Tool Names**: Use descriptive, action-oriented names
2. **Good Descriptions**: Help the LLM understand when to use each tool
3. **Simple Returns**: Return strings or simple dictionaries
4. **Graceful Errors**: Always catch exceptions and return helpful messages
5. **Single Purpose**: Each tool should do one thing well

## Troubleshooting

**Tool Not Being Called**
- Check tool description clarity
- Verify the agent model has tools bound
- Ensure tool is in the tools list

**Import Errors**  
- Run from 03-tools-integration directory
- Check ANTHROPIC_API_KEY in .env file

**API Key Issues**
- Create .env file in project root
- Add: `ANTHROPIC_API_KEY=your-key-here`

## Relationship to MCP Servers

The tools demonstrated in this module (`@tool` decorated functions) are the foundation for understanding MCP (Model Context Protocol) servers in the next module. Here's the key relationship:

- **LangGraph Tools**: Python functions that run in-process with your agent
- **MCP Servers**: Tools exposed as separate server processes via a protocol

Think of MCP servers as "tools as a service" - they provide the same functionality but with:
- Language independence (servers can be written in any language)
- Process isolation (servers run independently)
- Dynamic discovery (agents can find tools at runtime)
- Protocol features (streaming, cancellation, standardized errors)

For a detailed comparison and migration guide, see `04-mcp-architecture/real_mcp.md`.

## Next Steps

After mastering tools here, continue to:
- `04-mcp-architecture` - Learn about distributed tool systems with MCP
- Understand how tools can be served remotely via the MCP protocol
- See how to convert LangGraph tools to MCP servers
- Explore multi-agent architectures using MCP

Remember: This module focuses on learning tool patterns. Real-world applications would include proper error handling, authentication, and production considerations.