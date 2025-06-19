#!/usr/bin/env python3
"""
Simple MCP + Claude integration without LangGraph
This demonstrates clean message ordering that works with Claude's requirements
"""
import os
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from fastmcp import Client

# Load environment variables
load_dotenv()


# Define MCP tool wrapper
@tool
async def get_example_data():
    """Fetch example data from the MCP server. Returns YAML formatted data."""
    try:
        async with Client("http://127.0.0.1:7070/mcp") as client:
            result = await client.call_tool("get_example_data", {})
            return result[0].text
    except Exception as e:
        return f"Error connecting to MCP server: {e}"


@tool
async def calculate_comfort_index(temperature: float, humidity: float):
    """Calculate comfort index based on temperature and humidity."""
    try:
        async with Client("http://127.0.0.1:7070/mcp") as client:
            result = await client.call_tool("calculate_comfort_index", {
                "temperature": temperature,
                "humidity": humidity
            })
            return result[0].text
    except Exception as e:
        return f"Error connecting to MCP server: {e}"


async def simple_demo():
    """Run a simple demo showing MCP tool usage with Claude"""
    print("=" * 60)
    print("Simple MCP + Claude Demo (No LangGraph)")
    print("=" * 60)
    
    # Initialize Claude
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Bind tools to the model
    llm_with_tools = llm.bind_tools([get_example_data, calculate_comfort_index])
    
    # Test queries
    test_queries = [
        "What weather data is available from the station?",
        "Calculate the comfort index for 25°C and 70% humidity",
        "Is it comfortable at 18°C with 40% humidity?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        
        # Create fresh message list for each query
        messages = [
            SystemMessage(content="You have access to tools that can fetch weather data and calculate comfort indices. Use them when asked."),
            HumanMessage(content=query)
        ]
        
        # Get Claude's response
        response = await llm_with_tools.ainvoke(messages)
        
        if response.tool_calls:
            print("Claude: Let me check that for you...")
            
            messages.append(response)
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                if tool_call["name"] == "get_example_data":
                    data = await get_example_data.ainvoke({})
                elif tool_call["name"] == "calculate_comfort_index":
                    data = await calculate_comfort_index.ainvoke(tool_call["args"])
                else:
                    data = "Unknown tool"
                
                print(f"\n[Tool Response]:\n{data}")
                
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
        
        print("-" * 60)


async def interactive_mode():
    """Interactive chat mode"""
    print("\n" + "="*60)
    print("Interactive Mode (type 'exit' to quit)")
    print("="*60)
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    llm_with_tools = llm.bind_tools([get_example_data, calculate_comfort_index])
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        messages = [
            SystemMessage(content="You have access to tools that can fetch weather data and calculate comfort indices."),
            HumanMessage(content=user_input)
        ]
        
        response = await llm_with_tools.ainvoke(messages)
        
        if response.tool_calls:
            print("\nClaude: Let me check that for you...")
            messages.append(response)
            
            for tool_call in response.tool_calls:
                if tool_call["name"] == "get_example_data":
                    data = await get_example_data.ainvoke({})
                elif tool_call["name"] == "calculate_comfort_index":
                    data = await calculate_comfort_index.ainvoke(tool_call["args"])
                else:
                    data = "Unknown tool"
                
                print(f"\n[Tool Response]:\n{data}")
                
                tool_msg = ToolMessage(
                    content=data,
                    tool_call_id=tool_call["id"]
                )
                messages.append(tool_msg)
            
            final_response = await llm.ainvoke(messages)
            print(f"\nClaude: {final_response.content}")
        else:
            print(f"\nClaude: {response.content}")
    
    print("\nGoodbye!")


async def main():
    """Main entry point"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment.")
        print("Please set it in your .env file or environment variables.")
        return
    
    print("Simple MCP Client Demo")
    print("\nChoose mode:")
    print("1. Run demo queries")
    print("2. Interactive chat")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        await simple_demo()
    elif choice == "2":
        await interactive_mode()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    asyncio.run(main())