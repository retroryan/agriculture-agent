# Building Agents: From Static Workflows to Dynamic Intelligence

## Your Position in the Learning Journey

**Stage 3 of 4**: Introduction to Agent Architecture

You've seen the limitations of hardcoded workflows in stage 2. When users ask "What about frost risk?" after discussing irrigation, or need to chain multiple analyses together, static patterns break down.

This stage transforms your application into a dynamic agent that reasons about which tools to use and when.

## The Evolution Story

Remember the agricultural advisor from stage 2? It worked great for predefined questions:
- "Is it too dry?" → Check precipitation
- "Should I irrigate?" → Check soil moisture

But real farming decisions aren't linear:
- "Can I plant corn tomorrow considering the weather and soil conditions?"
- "Analyze my field conditions and tell me the biggest risks"
- "Compare this week's weather to optimal growing conditions"

These require an agent that can plan, use multiple tools, and reason about results.

## What You'll Build

Three progressively powerful agent systems:

1. **Basic Tools** - Math, text, dates (no external dependencies)
2. **External Tools** - Web fetching and real-time data
3. **Tool Chaining** - Combining capabilities for complex analysis

## Quick Start

```bash
# Stage 1: Basic tools demonstration
python 03-tools-integration/basic_tools/chatbot_with_tools.py

# Stage 2: External data integration  
python 03-tools-integration/external_tools/chatbot_with_fetch.py

# Stage 3: See tool chaining in action
python 03-tools-integration/main.py
```

## The Fundamental Shift: Tools as Capabilities

### What Makes a Tool?

A tool is a function an AI can invoke based on context. The magic is in the docstring - it tells the AI when and why to use the tool.

```python
@tool
def get_simulated_weather(location: str) -> str:
    """Get current weather for a location. Use when users ask about weather conditions."""
    # Implementation
    return f"Weather data for {location}"
```

The AI reads that docstring and decides: "User asked about weather in Denver, I should call this tool."

### The Tool Pattern

Every tool follows this structure:
```python
from langchain_core.tools import tool

@tool
def tool_name(param: type) -> str:
    """Clear description of what this does and when to use it."""
    try:
        # Tool logic
        return "Result as string"
    except Exception as e:
        return f"Error: {str(e)}"
```

**Key principles:**
- **Single Purpose**: Each tool does one thing well
- **Clear Documentation**: The docstring is your tool's interface
- **Graceful Errors**: Always return helpful error messages
- **Simple Returns**: Strings or simple dictionaries work best

## Stage 1: Basic Tools - The Foundation

Start here to understand tool integration without external complexity.

### Available Tools

Your agent gains eight fundamental capabilities:

**Mathematical Tools:**
- `add_numbers` - Basic addition ("What's 42 plus 17?")
- `multiply_numbers` - Multiplication with floats ("Calculate 15.5 times 3.2")

**Text Analysis:**
- `count_words` - Word counting ("How many words in this description?")
- `reverse_text` - String reversal (useful for demonstrations)

**Time Operations:**
- `get_current_time` - Current timestamp ("What time is it?")
- `calculate_days_between` - Date math ("Days until harvest season?")

**Domain Tools:**
- `get_simulated_weather` - Weather data (simulated for now)
- `agricultural_advice` - Crop recommendations based on conditions

### How the Agent Decides

Watch the agent's decision process:

```
User: "What's the weather in Chicago and how many days until December 25th?"

Agent thinks:
1. User wants weather → Use get_simulated_weather("Chicago")
2. User wants date calculation → Use calculate_days_between(today, "2024-12-25")
3. Combine results into coherent response
```

### Running Basic Tools

```bash
python 03-tools-integration/basic_tools/chatbot_with_tools.py
```

Try these interactions:
- "Add 25 and 17, then tell me the weather in Paris"
- "How many words are in 'The quick brown fox' and what time is it?"
- "Give me agricultural advice for corn in dry conditions"

**Notice:** The agent automatically selects and chains tools based on your query.

## Stage 2: External Tools - Reaching Beyond

Static data limits your agent. External tools break those limits.

### The Fetch Tools

Two approaches to external data:

**fetch_webpage** - Intelligent web scraping:
```python
@tool
def fetch_webpage(url: str) -> str:
    """Fetch and convert webpage to readable markdown."""
    # Fetches HTML → Extracts text → Converts to markdown
    return clean_markdown_content
```

**fetch_raw_content** - Direct API access:
```python
@tool  
def fetch_raw_content(url: str) -> str:
    """Get raw response from URL (JSON, text, etc)."""
    # Returns exactly what the server sends
    return raw_response
```

### Real-World Applications

Now your agent can:
- "What's on the OpenMeteo documentation page?"
- "Fetch the current weather API response from this endpoint"
- "Analyze the content on this agricultural website"

### Running External Tools

```bash
python 03-tools-integration/external_tools/chatbot_with_fetch.py
```

The agent now accesses real-time information beyond its training data.

## Stage 3: Tool Chaining - Complex Operations

The real power emerges when tools work together.

### The Chaining Pattern

```bash
python 03-tools-integration/main.py
```

This demonstrates:
1. **Sequential Operations**: Fetch → Analyze → Summarize
2. **Conditional Logic**: If weather is bad → Check forecast → Suggest alternatives
3. **Data Synthesis**: Combine multiple sources into insights

### Example: Agricultural Analysis Chain

```
User: "Check the weather forecast website and tell me if it's good for planting"

Agent executes:
1. fetch_webpage(forecast_url) → Get forecast data
2. get_simulated_weather(location) → Current conditions  
3. agricultural_advice(crop, conditions) → Planting recommendation
4. calculate_days_between(today, optimal_date) → Timing advice
```

## Integration with LangGraph

### The Architecture

Tools integrate seamlessly with LangGraph's state machine:

```python
# 1. Create tools list
tools = [add_numbers, get_simulated_weather, fetch_webpage, ...]

# 2. Bind to model
model = ChatAnthropic(model="claude-3-5-sonnet").bind_tools(tools)

# 3. Create tool node
tool_node = ToolNode(tools=tools)

# 4. Add conditional routing
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,  # Decides: use tools or respond directly
    {"tools": "tools", END: END}
)
```

### Execution Flow

```
User Message
    ↓
Agent Analyzes
    ↓
Needs Tools? → Yes → Execute Tools → Process Results
    ↓ No                                  ↓
Direct Response ← ← ← ← ← ← ← ← ← ← ← ← ←
```

### Tool Selection Intelligence

The agent considers:
- **Query keywords**: "calculate" → math tools, "weather" → weather tools
- **Context**: Previous conversation influences tool choice
- **Efficiency**: Chooses minimal tools needed
- **Error recovery**: Falls back gracefully if tools fail

## Common Patterns and Best Practices

### Tool Design Patterns

**Composable Tools:**
```python
@tool
def get_temperature(location: str) -> str:
    """Get current temperature for agricultural planning."""
    # Specific, focused functionality
    
@tool
def calculate_growing_degree_days(temp: float, base: float) -> str:
    """Calculate GDD for crop development tracking."""
    # Builds on temperature data
```

**Error Handling:**
```python
@tool
def risky_operation(param: str) -> str:
    """Perform operation that might fail."""
    try:
        result = external_api_call(param)
        return f"Success: {result}"
    except ConnectionError:
        return "Error: Cannot reach external service. Try again later."
    except ValueError as e:
        return f"Error: Invalid input - {str(e)}"
```

### Anti-Patterns to Avoid

❌ **Tools doing too much:**
```python
@tool
def do_everything(query: str) -> str:
    """Analyzes weather, gives advice, makes calculations, fetches data..."""
    # Too complex - split into focused tools
```

❌ **Poor error messages:**
```python
return "Error"  # Bad - uninformative
return f"Error: Temperature API returned no data for {location}"  # Good
```

❌ **Side effects in tools:**
```python
@tool
def get_data_and_save(location: str) -> str:
    data = fetch_data(location)
    save_to_database(data)  # Bad - tools should be read-only
    return data
```

## The Power of Tool-Using Agents

### Why This Architecture Wins

1. **Extensibility**: Add new capabilities without changing core logic
2. **Modularity**: Tools are independent and testable
3. **Clarity**: Each tool has a clear, single purpose
4. **Flexibility**: Agents combine tools in ways you didn't anticipate

### Real Agricultural Scenarios

Your tool-using agent can now handle:

**Complex Planning:**
"Check the weather forecast, calculate growing degree days, and tell me if I should apply fertilizer this week"

**Risk Assessment:**
"Analyze precipitation data and soil moisture to assess drought risk for my wheat"

**Market Timing:**
"Based on weather conditions and typical growth rates, when should I expect harvest?"

## Performance Considerations

### Tool Execution

- Tools run sequentially by default
- Each tool call adds latency
- Cache external API results when possible
- Set reasonable timeouts for external tools

### Token Usage

- Each tool call consumes tokens for:
  - Tool selection reasoning
  - Parameter extraction
  - Result processing
- Optimize tool descriptions for clarity and brevity

## Next Steps: Distributed Architecture

You've built agents with integrated tools. But what if tools could be:
- Written in any language
- Shared across projects
- Scaled independently
- Versioned and deployed separately

That's MCP - the next evolution.

**04-mcp-architecture** - Distributed tool systems
```bash
python 04-mcp-architecture/quick_demo.py
```

## Key Takeaways

- **Tools are Capabilities**: Functions your AI can invoke based on context
- **Docstrings are Interfaces**: Clear descriptions enable intelligent tool selection
- **Composition over Complexity**: Many simple tools beat few complex ones
- **Errors are Information**: Graceful failure helps agents recover and retry
- **Chaining Creates Power**: Simple tools combine for complex operations

You've evolved from static workflows to dynamic agents. The agricultural advisor that once followed scripts now reasons about which tools to use and why.

Next: distributing those tools across systems with MCP.