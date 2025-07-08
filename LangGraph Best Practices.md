# LangChain & LangGraph Best Practices for Demo Applications

This document outlines best practices for building educational demo applications using LangChain's unified model interface and LangGraph, based on official documentation and practical patterns.

## Core Principles

### 1. Simplicity First
For educational demos, prioritize clarity over sophistication:
- Use straightforward initialization patterns
- Avoid complex error handling that obscures the main concepts
- Keep configuration minimal
- Focus on demonstrating one concept well

### 2. Unified Model Interface

The `init_chat_model()` function provides a clean abstraction for model initialization:

```python
from langchain.chat_models import init_chat_model

# Simple initialization
model = init_chat_model("claude-3-5-sonnet-20241022", temperature=0)

# With explicit provider
model = init_chat_model(
    "claude-3-5-sonnet-20241022",
    model_provider="anthropic",
    temperature=0
)
```

**Benefits:**
- Single import for all models
- Runtime model switching
- Consistent interface across providers
- Future-proof for new models

## LangGraph Patterns

### 1. State Management

Use TypedDict for simple, clear state definitions:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

For demos, avoid complex state schemas unless demonstrating state management specifically.

### 2. Graph Construction

Follow the standard pattern:

```python
from langgraph.graph import StateGraph, START, END

# Create graph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("agent", agent_function)
graph_builder.add_node("tools", tool_node)

# Add edges
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    condition_function,
    {"tools": "tools", END: END}
)

# Compile
graph = graph_builder.compile()
```

### 3. Tool Integration

Keep tool definitions simple and focused:

```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Clear description of what this tool does."""
    return result
```

**Best Practices:**
- Use descriptive tool names
- Write clear docstrings (LLMs use these)
- Return simple types (str, dict)
- Handle errors gracefully

## Configuration Management

### 1. Environment Variables

For demos, use simple .env files:

```python
from dotenv import load_dotenv
import os

# Load from parent directory
load_dotenv("../.env")

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Please set ANTHROPIC_API_KEY in .env file")
```

### 2. Model Configuration

Create a simple config module:

```python
def get_model(model_name=None, **kwargs):
    """Get a configured model instance."""
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    return init_chat_model(model_name, **kwargs)
```

## Error Handling for Demos

Keep error handling educational but not overwhelming:

```python
try:
    result = tool.invoke(params)
except Exception as e:
    # For demos: show what went wrong clearly
    return f"Error: {str(e)}"
```

## Code Organization

### 1. Module Structure
```
03-tools-integration/
├── config.py           # Model configuration
├── shared/            # Shared utilities
│   └── base.py       # Common patterns
├── basic_tools/       # Basic examples
├── external_tools/    # External API examples
└── examples/          # Advanced demonstrations
```

### 2. Import Patterns

For self-contained modules:
```python
# Avoid sys.path manipulation
# Use relative imports within the package
from .tools import my_tool
from ..config import get_model
```

## Demo-Specific Patterns

### 1. Progressive Complexity
- Start with basic concepts
- Build up to advanced features
- Each example should teach one main concept

### 2. Interactive Examples
```python
def run_interactive_demo():
    print("Demo Title")
    print("=" * 50)
    print("What this demo shows...")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        
        # Process with graph
        result = graph.invoke({"messages": [user_input]})
        print(f"Assistant: {result}")
```

### 3. Clear Documentation
- Explain what each example demonstrates
- Provide sample queries
- Note any limitations (e.g., "simulated data")

## Common Patterns to Avoid

### 1. Over-Engineering
- Don't add production features to demos
- Avoid complex dependency injection
- Skip advanced error recovery

### 2. Hidden Complexity
- Don't hide important logic in utilities
- Keep the main flow visible
- Avoid too many abstraction layers

### 3. Unclear Examples
- Don't mix multiple concepts in one demo
- Avoid examples that require extensive setup
- Skip edge cases in basic demos

## Testing Patterns

For demo applications:
```python
def test_tools():
    """Simple functional tests for demos."""
    # Test each tool works
    assert add_numbers.invoke({"a": 1, "b": 2}) == 3
    
    # Test the graph processes messages
    result = graph.invoke({
        "messages": [HumanMessage("test query")]
    })
    assert len(result["messages"]) > 0
```

## Summary

When building LangChain/LangGraph demos:
1. **Keep it simple** - Focus on teaching concepts
2. **Use unified patterns** - Leverage init_chat_model()
3. **Be explicit** - Show the important code
4. **Progressive learning** - Build complexity gradually
5. **Test the basics** - Ensure examples work

Remember: The goal is education, not production deployment. Make the code easy to understand, modify, and learn from.