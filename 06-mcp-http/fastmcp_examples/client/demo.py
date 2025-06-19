#!/usr/bin/env python3
"""
FastMCP + LangGraph Demo
Unified demo script showcasing different integration patterns
"""
import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from fastmcp import Client

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print("Please create a .env file with your API key")
    sys.exit(1)

# MCP tool definition (used by simple and manual modes)
@tool
async def get_example_data():
    """Fetch example data from the MCP server. Returns YAML formatted data."""
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("get_example_data", {})
        return result[0].text

async def simple_demo():
    """Simple single-turn demo without LangGraph"""
    print("\n" + "="*60)
    print("Simple Single-Turn Demo (Without LangGraph)")
    print("="*60)
    print("This demo shows basic MCP tool usage with Claude")
    print("-"*60)
    
    # Initialize Claude
    llm = ChatAnthropic(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-haiku-20240307",
        temperature=0
    )
    
    # Bind the MCP tool
    llm_with_tools = llm.bind_tools([get_example_data])
    
    # Example queries
    queries = [
        "Can you fetch the data from the MCP server?",
        "What data is available from the server?",
        "Please get the example data and tell me what type it is."
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        
        # Create messages
        messages = [
            SystemMessage(content="You have access to a tool that can fetch data from an MCP server. Use it when asked about data."),
            HumanMessage(content=query)
        ]
        
        # Get Claude's response
        response = await llm_with_tools.ainvoke(messages)
        
        # Process tool calls if any
        if response.tool_calls:
            print("Claude: Let me fetch that data for you...")
            
            # Execute tool and show results
            messages.append(response)
            for tool_call in response.tool_calls:
                if tool_call["name"] == "get_example_data":
                    data = await get_example_data.ainvoke({})
                    print(f"\nData retrieved:\n{data}")
                    
                    tool_msg = ToolMessage(
                        content=data,
                        tool_call_id=tool_call["id"]
                    )
                    messages.append(tool_msg)
            
            # Get final response
            final_response = await llm.ainvoke(messages)
            print(f"\nClaude: {final_response.content}")
        else:
            print(f"Claude: {response.content}")
        
        print("-"*60)

async def langgraph_agent_demo():
    """Full LangGraph agent demo using official MCP adapters"""
    print("\n" + "="*60)
    print("Full LangGraph Agent Demo (With MCP Adapters)")
    print("="*60)
    print("This demo uses the official langchain-mcp-adapters library")
    print("-"*60)
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langgraph.prebuilt import create_react_agent
    except ImportError as e:
        print(f"\nError importing required modules: {e}")
        print("\nPlease ensure langchain-mcp-adapters is installed:")
        print("  pip install langchain-mcp-adapters")
        return
    
    # Initialize MCP client
    client = MultiServerMCPClient({
        "serializer": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http"
        }
    })
    
    # Get tools from MCP server
    print("\nConnecting to MCP server...")
    tools = await client.get_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")
    
    # Create LangGraph agent
    llm = ChatAnthropic(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-haiku-20240307"
    )
    agent = create_react_agent(llm, tools)
    
    # Example queries
    queries = [
        "What can you serialize?",
        "Show me the example data",
        "What format is the data in?"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        print("Claude: ", end="", flush=True)
        
        # Stream the response
        tool_used = False
        async for chunk in agent.astream({"messages": [("user", query)]}):
            if "agent" in chunk:
                for message in chunk["agent"]["messages"]:
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        if not tool_used:
                            print("Let me fetch that data for you...", flush=True)
                            tool_used = True
                    elif hasattr(message, 'content') and message.content:
                        if isinstance(message.content, str):
                            print(message.content, end="", flush=True)
            elif "tools" in chunk:
                for message in chunk["tools"]["messages"]:
                    if hasattr(message, 'content'):
                        print(f"\n\nData retrieved:\n{message.content}\n")
                        print("Claude: ", end="", flush=True)
        
        print("\n" + "-"*60)

async def interactive_chat():
    """Interactive chat mode with MCP tools"""
    print("\n" + "="*60)
    print("Interactive Chat Mode")
    print("="*60)
    print("Chat with Claude using MCP tools (type 'exit' to quit)")
    print("-"*60)
    
    # Initialize Claude
    llm = ChatAnthropic(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-haiku-20240307",
        temperature=0
    )
    
    # Bind the MCP tool
    llm_with_tools = llm.bind_tools([get_example_data])
    
    # System message
    system_msg = SystemMessage(content="You are a helpful assistant that can fetch data from an MCP server. When users ask about data, serialization, or want to see example data, use the get_example_data tool.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Create message list for this turn
        messages = [system_msg, HumanMessage(content=user_input)]
        
        # Get Claude's initial response
        response = await llm_with_tools.ainvoke(messages)
        
        # Check if Claude wants to use tools
        if response.tool_calls:
            print("\nClaude: Let me fetch that data for you...")
            
            # Build the complete message sequence
            messages.append(response)
            
            # Execute each tool call
            for tool_call in response.tool_calls:
                if tool_call["name"] == "get_example_data":
                    data = await get_example_data.ainvoke({})
                    print(f"\nData retrieved:\n{data}")
                    
                    # Add tool result to messages
                    tool_msg = ToolMessage(
                        content=data,
                        tool_call_id=tool_call["id"]
                    )
                    messages.append(tool_msg)
            
            # Get Claude's final response after seeing tool results
            final_response = await llm.ainvoke(messages)
            print(f"\nClaude: {final_response.content}")
        else:
            # No tool use, just display the response
            print(f"\nClaude: {response.content}")

async def check_server():
    """Check if the MCP server is running"""
    try:
        async with Client("http://127.0.0.1:8000/mcp") as client:
            # Try to list tools
            await client.list_tools()
            return True
    except Exception:
        return False

async def main():
    """Main demo entry point"""
    print("\nFastMCP + LangGraph Demo")
    print("========================\n")
    
    # Check if server is running
    print("Checking MCP server status...", end="", flush=True)
    if not await check_server():
        print(" ❌ Not running!")
        print("\nError: MCP server is not running.")
        print("Please start the server first:")
        print("  python serializer.py")
        sys.exit(1)
    print(" ✅ Running!")
    
    while True:
        print("\nChoose demo mode:")
        print("1. Simple single-turn demo (without LangGraph)")
        print("2. Full agent demo (with LangGraph + MCP adapters)")
        print("3. Interactive chat mode")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            await simple_demo()
        elif choice == "2":
            await langgraph_agent_demo()
        elif choice == "3":
            await interactive_chat()
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")
        
        if choice in ["1", "2"]:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)