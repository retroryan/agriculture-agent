# 03 - Tools Integration

This module demonstrates how to integrate tools with LangGraph agents, progressing from basic built-in tools to external API integration and finally to advanced tool chaining patterns.

## Overview

Tools in LangGraph allow AI agents to interact with external systems, perform calculations, fetch data, and execute specific tasks. This module shows three progressively complex examples of tool integration.

## Examples

### 1. Basic Tools Demo (`basic_tools/chatbot_with_tools.py`)

**Purpose**: Introduction to tool integration in LangGraph

**Features**:
- Mathematical operations (addition, multiplication)
- Text analysis (word counting, text reversal)
- Date/time utilities
- Simulated weather data
- Agricultural advice based on conditions
- Smart chatbot function that avoids redundant model calls

**Key Learning Points**:
- How to define tools using the `@tool` decorator
- Binding tools to language models
- Tool selection by the AI based on user queries
- Efficient message handling to avoid unnecessary API calls

**Run it**:
```bash
python 03-tools-integration/basic_tools/chatbot_with_tools.py
```

### 2. External Tools Demo (`external_tools/chatbot_with_fetch.py`)

**Purpose**: Demonstrate integration with external APIs and web content

**Features**:
- Web page fetching with HTML-to-markdown conversion
- Raw content fetching for APIs
- Combines fetch tools with text analysis tools
- Real-world API integration patterns

**Key Learning Points**:
- Creating tools that interact with external services
- Handling different content types (HTML vs raw text)
- Error handling for network requests
- Tool composition (using multiple tools together)

**Run it**:
```bash
python 03-tools-integration/external_tools/chatbot_with_fetch.py
```

### 3. Tool Chaining Demo (`tool_chaining_demo.py`)

**Purpose**: Advanced demonstration of tools working together to solve complex problems

**Features**:
- Three automated demo scenarios
- Interactive mode for experimentation
- Tools using outputs from other tools
- Complex multi-step problem solving
- Real-world scenarios combining multiple capabilities

**Demo Scenarios**:
1. **Weather + Agriculture**: Fetches weather and provides farming advice
2. **Web Content Analysis**: Fetches web pages and analyzes their content
3. **Combined Analysis**: Multiple tools working in sequence on related tasks

**Key Learning Points**:
- Tool orchestration and chaining
- Breaking complex queries into steps
- Tools building on each other's outputs
- Real-world application patterns

**Run it**:
```bash
python 03-tools-integration/tool_chaining_demo.py
```

## Project Structure

```
03-tools-integration/
├── README.md                    # This file
├── shared/                      # Shared utilities
│   ├── __init__.py
│   └── base.py                 # Common boilerplate code
├── basic_tools/                 # Basic tool implementations
│   ├── __init__.py             # Tool categories and exports
│   ├── tools.py                # Tool definitions
│   └── chatbot_with_tools.py  # Basic tools demo
├── external_tools/              # External API tools
│   ├── __init__.py
│   ├── fetch_tool.py           # Web fetching tools
│   └── chatbot_with_fetch.py  # External tools demo
└── tool_chaining_demo.py       # Advanced tool composition demo
```

## Available Tools

### Basic Tools
- **Math**: `add_numbers`, `multiply_numbers`
- **Text**: `count_words`, `reverse_text`
- **Time**: `get_current_time`, `calculate_days_between`
- **Weather**: `get_simulated_weather`, `agricultural_advice`

### External Tools
- **Web**: `fetch_webpage` (HTML to markdown), `fetch_raw_content` (raw text)

## Key Concepts

### Tool Definition
Tools are defined using the `@tool` decorator:
```python
@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

### Tool Binding
Tools are bound to the language model:
```python
model = ChatAnthropic(...).bind_tools(tools)
```

### Tool Execution
LangGraph handles tool execution through the `ToolNode`:
```python
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
```

### Tool Selection
The AI model automatically selects appropriate tools based on:
- User query content
- Tool descriptions
- Available tool capabilities

## Learning Path

1. **Start with Basic Tools**: Understand fundamental tool integration
2. **Move to External Tools**: Learn API integration patterns
3. **Master Tool Chaining**: See how tools work together for complex tasks

## Tips for Creating Your Own Tools

1. **Clear Descriptions**: Tool docstrings are used by the AI for selection
2. **Type Hints**: Always include type hints for parameters and returns
3. **Error Handling**: Handle exceptions gracefully
4. **Single Responsibility**: Each tool should do one thing well
5. **Composability**: Design tools that can work together

## Next Steps

After mastering tools integration, move on to:
- **04-mcp-architecture**: Distributed tool systems with MCP
- **05-advanced-mcp**: Structured outputs and enhanced tool patterns

## Migration to Unified Model Interface

This module has been migrated to use LangChain's unified model interface (`init_chat_model()`). Key benefits:
- Single import for all model providers
- Runtime model switching via environment variables
- Consistent API across different LLMs
- Simplified configuration management

See `config.py` for the implementation and `best-practices.md` for patterns and guidelines.