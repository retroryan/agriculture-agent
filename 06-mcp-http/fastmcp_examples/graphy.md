# LangGraph Integration Demo Proposal

## Overview
This proposal outlines how to add a LangGraph-based agent client alongside the existing `client_serializer.py` without modifying the original client. The new agent will demonstrate how to integrate FastMCP tools into a LangGraph workflow with Claude LLM for intelligent decision-making.

## Proposed Implementation

### 1. New File: `client_langgraph_agent.py` ✓ IMPLEMENTED (with issues)

Created a new client that uses LangGraph with Claude for intelligent agent workflow. 

**Implementation Status:**
- ✅ File created successfully
- ✅ Dependencies added to requirements.txt
- ✅ All dependencies installed
- ❌ LangGraph agent has message formatting issues with Claude API
- ✅ Created simplified version `client_langgraph_simple.py` which works correctly

**Issues Encountered:**
1. **ToolExecutor Import Error**: The `ToolExecutor` class was removed from langgraph.prebuilt in newer versions. Fixed by directly invoking tools.
2. **Claude API Message Formatting**: Claude's API is strict about message formatting:
   - Error: "messages: final assistant content cannot end with trailing whitespace"
   - Error: "tool_use ids were found without tool_result blocks"
   - Error: "unexpected tool_use_id found in tool_result blocks"
3. **LangGraph State Management**: The state graph seems to have issues with proper message sequencing for Claude's tool use pattern.

**What Works:**
- ✅ Simple client (`client_langgraph_simple.py`) successfully:
  - Connects to MCP server
  - Uses Claude to decide when to call tools
  - Executes the `get_mcp_data` tool
  - Retrieves YAML data from the server
  - Claude properly summarizes the retrieved data
  - Handles multiple queries in sequence

**What Doesn't Work:**
- ❌ Full LangGraph agent (`client_langgraph_agent.py`):
  - Message sequencing issues with tool calls
  - State management complications
  - Proper tool result handling in the graph flow

**Testing Results:**
```bash
# Server running successfully:
python serializer.py
# Output: Server started on http://127.0.0.1:8000/mcp

# Simple client works:
python client_langgraph_simple.py
# Successfully retrieves and displays:
# name: Test
# value: 123
# status: true
# Claude provides summaries of the data

# LangGraph agent fails with message formatting errors
```

### 2. Alternative Implementation: `client_langgraph_simple.py`

A simpler version using LangChain's ChatAnthropic directly without the full graph:

```python
# client_langgraph_simple.py
import os
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from fastmcp import Client

# Load environment variables
load_dotenv()

@tool
async def get_mcp_data():
    """Fetch example data from the MCP server."""
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("get_example_data", {})
        return result[0].text

async def main():
    # Initialize Claude
    llm = ChatAnthropic(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-haiku-20240307",
        temperature=0
    )
    
    # Bind the MCP tool to the LLM
    llm_with_tools = llm.bind_tools([get_mcp_data])
    
    print("Simple FastMCP + Claude Demo")
    print("=" * 30)
    
    # Example queries
    queries = [
        "Can you fetch the data from the MCP server?",
        "What data is available from the server?",
        "Please get the example data and summarize what you find."
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        
        # Create messages
        messages = [
            SystemMessage(content="You have access to a tool that can fetch data from an MCP server. Use it when asked about data."),
            HumanMessage(content=query)
        ]
        
        # Get Claude's response with tool usage
        response = await llm_with_tools.ainvoke(messages)
        
        # If Claude wants to use a tool
        if response.tool_calls:
            print("Claude: Let me fetch that data for you...")
            
            # Execute the tool
            for tool_call in response.tool_calls:
                if tool_call["name"] == "get_mcp_data":
                    data = await get_mcp_data.ainvoke({})
                    print(f"\nData retrieved:\n{data}")
                    
                    # Get Claude's interpretation
                    followup = await llm.ainvoke([
                        *messages,
                        response,
                        HumanMessage(content=f"The tool returned this data:\n{data}\n\nPlease summarize what you found.")
                    ])
                    print(f"\nClaude's summary: {followup.content}")
        else:
            print(f"Claude: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Generic LLM Support: `client_langgraph_generic.py`

A version that supports multiple LLM providers through LangChain:

```python
# client_langgraph_generic.py
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from fastmcp import Client

# Load environment variables
load_dotenv()

def get_llm(provider: str = "anthropic") -> BaseChatModel:
    """Factory function to get LLM based on provider"""
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-haiku-20240307"
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4-turbo-preview"
        )
    elif provider == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model="llama2")
    else:
        raise ValueError(f"Unsupported provider: {provider}")

@tool
async def query_mcp_server(query: Optional[str] = None):
    """Query the MCP server for example data. Optionally pass a query string."""
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("get_example_data", {})
        return f"MCP Server Data:\n{result[0].text}"

async def create_agent(llm_provider: str = "anthropic"):
    """Create an agent with the specified LLM provider"""
    # Get the LLM
    llm = get_llm(llm_provider)
    llm_with_tools = llm.bind_tools([query_mcp_server])
    
    # Create a simple state graph
    from typing import TypedDict, Sequence
    from langchain_core.messages import BaseMessage
    
    class State(TypedDict):
        messages: Sequence[BaseMessage]
        llm_provider: str
    
    async def call_model(state: State):
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}
    
    async def call_tool(state: State):
        last_message = state["messages"][-1]
        tool_call = last_message.tool_calls[0]
        result = await query_mcp_server.ainvoke(tool_call["args"])
        return {"messages": [HumanMessage(content=result)]}
    
    def should_continue(state: State):
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "call_tool"
        return "end"
    
    # Build the graph
    workflow = StateGraph(State)
    workflow.add_node("agent", call_model)
    workflow.add_node("call_tool", call_tool)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"call_tool": "call_tool", "end": END}
    )
    workflow.add_edge("call_tool", "agent")
    
    return workflow.compile(), llm_provider

async def main():
    print("Generic LLM + FastMCP Demo")
    print("=" * 30)
    
    # Let user choose LLM provider
    provider = input("Choose LLM provider (anthropic/openai/ollama) [anthropic]: ").strip() or "anthropic"
    
    try:
        app, provider_name = await create_agent(provider)
        print(f"\nUsing {provider_name} as LLM provider")
        
        # Interactive loop
        messages = [
            SystemMessage(content="You are a helpful assistant that can query an MCP server for data.")
        ]
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            messages.append(HumanMessage(content=user_input))
            
            # Run the agent
            result = await app.ainvoke({
                "messages": messages,
                "llm_provider": provider_name
            })
            
            # Display response
            last_msg = result["messages"][-1]
            if not hasattr(last_msg, 'tool_calls'):
                print(f"\n{provider_name}: {last_msg.content}")
            
            messages = result["messages"]
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have the required API keys in your .env file")

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Benefits

1. **No Changes to Existing Code**: Both `client_serializer.py` and `serializer.py` remain untouched
2. **Real LLM Integration**: Uses Claude (or other LLMs) for intelligent decision-making
3. **Progressive Complexity**: Three examples - full LangGraph, simple LangChain, and generic LLM support
4. **Production-Ready Patterns**: Demonstrates async tool execution, state management, and error handling
5. **Generic LLM Support**: Shows how to support multiple LLM providers (Claude, GPT-4, Ollama)

## Requirements

Add to `requirements.txt`:
```
langgraph>=0.2.0
langchain-core>=0.1.0
langchain-anthropic>=0.1.0
langchain-openai>=0.0.5  # Optional: for OpenAI support
langchain-community>=0.0.10  # Optional: for Ollama support
python-dotenv>=1.0.0
```

## Environment Setup

Create a `.env` file with your API keys:
```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

## Demo Script

```bash
# Terminal 1: Start the MCP server
python serializer.py

# Terminal 2: Run original client (unchanged)
python client_serializer.py

# Terminal 3: Run interactive LangGraph agent with Claude
python client_langgraph_agent.py

# Terminal 4: Run simple Claude integration
python client_langgraph_simple.py

# Terminal 5: Run generic LLM version (choose provider at runtime)
python client_langgraph_generic.py
```

## Architecture Highlights

### 1. **Tool Integration Pattern**
- FastMCP tools wrapped as LangChain tools using `@tool` decorator
- Async-first design for efficient I/O operations
- Clean separation between MCP client and LLM logic

### 2. **State Management**
- LangGraph StateGraph for complex workflows
- Message history tracking for context-aware responses
- Data persistence across conversation turns

### 3. **LLM Flexibility**
- Claude integration via `langchain-anthropic`
- Generic `BaseChatModel` interface for provider swapping
- Factory pattern for LLM instantiation

### 4. **Interactive Features**
- Real-time conversation loop
- Tool execution visualization
- Graceful error handling

## Next Steps

1. Create the new client files without modifying existing code
2. Install additional dependencies: `pip install langgraph langchain-anthropic python-dotenv`
3. Set up environment variables in `.env`
4. Run the demos to see intelligent agent behavior
5. Extend with more MCP tools or additional LLM capabilities

This approach demonstrates modern AI agent patterns while preserving the simplicity of the original FastMCP examples.