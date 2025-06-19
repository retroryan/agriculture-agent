# MCP LangGraph Agent Investigation

## Problem Statement
The `client_langgraph_agent.py` example fails with an Anthropic API error about tool messages:
```
anthropic.BadRequestError: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'messages.0.content.0: unexpected `tool_use_id` found in `tool_result` blocks: toolu_01QrAWcw1KWnPhmM5Aioxduu. Each `tool_result` block must have a corresponding `tool_use` block in the previous message.'}}
```

## What Works

### 1. Basic Setup
- The serializer server runs correctly with HTTP transport: `python serializer.py`
- The simple client works perfectly: `python client_langgraph_simple.py`
- MCP server communication is functional
- Tool execution works when called directly

### 2. Working Simple Client Pattern
The `client_langgraph_simple.py` demonstrates the correct message ordering:
1. System message + Human message
2. AI response with tool_calls
3. Tool result message (ToolMessage with matching tool_call_id)
4. Final AI response interpreting the tool result

## What Doesn't Work

### 1. Original Agent Implementation
The `client_langgraph_agent.py` fails because:
- LangGraph's message accumulation creates invalid message sequences
- When the agent loops back after tool execution, it sends tool result messages without the corresponding tool use messages
- The state management doesn't properly handle the Claude API's strict message ordering requirements

### 2. Key Issues Identified
1. **Message History Corruption**: After tool execution, the graph loops back to the agent with a message history that includes ToolMessages but not the AIMessage that requested those tools
2. **State Persistence**: The original implementation tries to maintain conversation state across multiple turns, which conflicts with Claude's message validation
3. **System Message Handling**: Adding system messages mid-conversation causes issues

## Attempted Fixes

### 1. Message Filtering (Partial Success)
Tried filtering out ToolMessages before sending to Claude:
```python
clean_messages = []
for msg in messages:
    if not isinstance(msg, ToolMessage):
        clean_messages.append(msg)
```
Result: Led to empty message lists in some cases

### 2. Fresh Message Lists Per Turn (Successful)
Creating new message lists for each user input works:
```python
messages = [
    SystemMessage(content="..."),
    HumanMessage(content=user_input)
]
```
Result: This approach works but doesn't maintain conversation history

### 3. Working Implementation
Created `client_langgraph_agent_working.py` which:
- Uses fresh message lists for each query
- Properly sequences messages through the graph
- Displays results correctly
- Avoids state corruption issues

## Root Cause
The fundamental issue is that LangGraph's default message accumulation pattern doesn't align with Claude's strict requirements for tool message ordering. Claude requires:
1. An AIMessage with tool_calls must immediately precede 
2. ToolMessage(s) with matching tool_call_ids

When LangGraph accumulates messages across graph cycles, this ordering gets disrupted.

## Recommendations

### For Immediate Use
Use the `client_langgraph_agent_working.py` implementation which:
- Works reliably
- Demonstrates the LangGraph + MCP + Claude integration
- Avoids the message ordering issues

### For Future Development
1. **Conversation History**: If conversation history is needed, implement custom message management that ensures proper ordering
2. **State Management**: Consider storing conversation context separately from the message list sent to Claude
3. **Message Validation**: Add validation before sending messages to Claude to ensure proper ordering

## How to Run the Working Version

1. Start the MCP server:
```bash
python serializer.py
```

2. Run the working agent:
```bash
python client_langgraph_agent_working.py
```

3. Test with queries like:
- "What can you serialize?"
- "Can you fetch the data?"
- "Show me the example data"

## Files Created During Investigation
- `client_langgraph_agent_fixed.py` - Attempted fix with message filtering (failed)
- `client_langgraph_agent_v2.py` - Attempted fix with fresh messages per turn (failed)
- `client_langgraph_agent_final.py` - Attempted fix with separate conversation history (failed)
- `client_langgraph_agent_working.py` - Attempted simpler implementation (still fails)
- `test_agent.py`, `test_agent_fixed.py` - Test scripts for automated testing

## Current Status
All attempts to fix the LangGraph agent implementation have failed due to the fundamental incompatibility between LangGraph's message accumulation and Claude's strict tool message ordering requirements. The issue appears to be deep within LangGraph's graph execution model.

## Working Solution
Created `client_agent_simple_working.py` which:
- **Successfully integrates MCP + Claude without LangGraph**
- Properly handles tool messages and responses
- Maintains clean message ordering
- Works reliably with the current setup

### To run the working solution:
```bash
# Terminal 1: Start the MCP server
python serializer.py

# Terminal 2: Run the working agent
python client_agent_simple_working.py
```

## The Real Problem Discovered

After reviewing the official LangGraph documentation, the issue is that **the example is not using the proper MCP integration pattern**. 

The current `client_langgraph_agent.py`:
- Manually wraps MCP calls in LangChain tools
- Tries to manage message flow manually
- Conflicts with LangGraph's message handling

The **correct approach** according to the official LangGraph documentation:
- Use `langchain-mcp-adapters` library
- Use `MultiServerMCPClient` to connect to MCP servers
- Let LangGraph handle the message flow properly

### Official Documentation URLs:
- **Using MCP in LangGraph agents**: https://langchain-ai.github.io/langgraph/agents/mcp/
- **LangGraph MCP server concepts**: https://langchain-ai.github.io/langgraph/concepts/server-mcp/
- **Exposing agents as MCP tools**: https://langchain-ai.github.io/langgraph/concepts/server-mcp/#exposing-an-agent-as-mcp-tool

## Proper Solution (TESTED AND WORKING)

Created `client_langgraph_agent_proper.py` which follows the official pattern and **successfully works**:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# Connect to MCP server
client = MultiServerMCPClient({
    "serializer": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http"
    }
})

# Get tools and create agent
tools = await client.get_tools()
agent = create_react_agent(llm, tools)
```

**Requirements**:
1. Install `langchain-mcp-adapters` (already added to requirements.txt):
   ```bash
   pip install langchain-mcp-adapters
   ```
2. Start the MCP server with HTTP transport:
   ```bash
   python serializer.py
   ```
3. Run the proper client:
   ```bash
   python client_langgraph_agent_proper.py
   ```

**Key differences from the broken example**:
- Uses `langchain_mcp_adapters.client.MultiServerMCPClient` (note the import path)
- Uses `create_react_agent` from `langgraph.prebuilt`
- Lets LangGraph handle all message flow and tool execution
- Works perfectly with Claude's message ordering requirements

## What We Did Wrong in the First Approach

### 1. **Manual Tool Wrapping**
The original `client_langgraph_agent.py` manually wrapped MCP calls in LangChain tools:
```python
@tool
async def get_example_data():
    """Fetch example data from the MCP server."""
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("get_example_data", {})
        return result[0].text
```
**Problem**: This creates a disconnect between LangGraph's tool management and the actual MCP protocol.

### 2. **Custom Graph Construction**
Built a custom StateGraph with manual node definitions:
```python
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
```
**Problem**: This required manual message flow management, which conflicted with Claude's strict tool message ordering.

### 3. **Message Accumulation Issues**
The state management accumulated messages across graph cycles:
```python
# Messages would accumulate tool results without corresponding tool calls
state = await app.ainvoke({
    "messages": messages,
    "data": data
})
```
**Problem**: Created invalid message sequences where ToolMessages appeared without their corresponding AIMessage tool calls.

## How We Fixed It

### 1. **Used Official MCP Adapters**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
```
This library is specifically designed to bridge MCP servers with LangChain/LangGraph.

### 2. **Leveraged Pre-built Components**
```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools)
```
The pre-built agent handles all the complex message flow and state management.

### 3. **Let the Framework Handle Tool Execution**
Instead of manually managing tool calls and responses, the proper implementation:
- Automatically discovers tools from MCP servers
- Handles tool execution and result formatting
- Manages message ordering correctly for Claude

## Best Practices Learned

### 1. **Use Official Integrations When Available**
- Don't reinvent the wheel - check for official adapters first
- The `langchain-mcp-adapters` library exists specifically for this use case

### 2. **Understand the Tool Chain**
- MCP → MCP Adapters → LangChain Tools → LangGraph Agent
- Each layer has its own abstractions and requirements

### 3. **Message Ordering Matters**
- Claude has strict requirements: tool calls must immediately precede tool results
- Manual message management is error-prone
- Let frameworks handle the complexity when possible

### 4. **Start Simple, Then Add Complexity**
- The simple non-LangGraph version (`client_agent_simple_working.py`) helped understand the requirements
- Once we understood the message flow, we could identify why the complex version failed

### 5. **Read the Documentation Carefully**
- The LangGraph docs clearly show the proper MCP integration pattern at https://langchain-ai.github.io/langgraph/agents/mcp/
- Different docs covered different aspects:
  - Using MCP tools in agents: https://langchain-ai.github.io/langgraph/agents/mcp/
  - Exposing agents as MCP servers: https://langchain-ai.github.io/langgraph/concepts/server-mcp/

## Lessons for Future Development

### 1. **Check for Existing Solutions**
Before implementing a custom integration:
- Search for official adapters/libraries
- Check the framework's documentation for integration patterns
- Look for pre-built components that handle common use cases

### 2. **Understand Protocol Requirements**
- Claude's tool message ordering is strict and well-documented
- MCP has its own protocol requirements
- Integration layers must respect both sets of requirements

### 3. **Debugging Approach**
When facing integration issues:
1. Start with the simplest possible implementation
2. Verify each component works independently
3. Add complexity incrementally
4. Use official examples as reference

### 4. **Import Path Matters**
- The correct import was `from langchain_mcp_adapters.client import MultiServerMCPClient`
- Not all packages export from their root `__init__.py`
- Always verify the actual module structure when imports fail

## Summary

The journey from broken to working implementation taught us that:
- **Manual integration** of protocols is complex and error-prone
- **Official adapters** exist for a reason - they handle edge cases and protocol requirements
- **Pre-built components** (like `create_react_agent`) encapsulate best practices
- **Understanding the full stack** (MCP → Adapters → LangChain → LangGraph → Claude) is crucial for debugging

The final working solution is not just simpler but also more robust because it leverages the collective knowledge embedded in the official libraries.

## Final Implementation: Unified Demo

All working approaches have been combined into a single `demo.py` script that offers:

1. **Simple single-turn demo** - Shows basic MCP tool usage without LangGraph
2. **Full agent demo** - Uses LangGraph with official MCP adapters
3. **Interactive chat mode** - Allows free-form conversation with MCP tools

### Running the Demo

```bash
# Terminal 1: Start the MCP server
python serializer.py

# Terminal 2: Run the unified demo
python demo.py
```

The demo script:
- Checks if the MCP server is running before starting
- Provides a user-friendly menu to select different modes
- Demonstrates both simple and complex integration patterns
- Includes proper error handling and user feedback

This unified approach makes it easy to:
- Compare different integration methods
- Test MCP functionality quickly
- Understand the progression from simple to complex implementations