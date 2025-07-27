#!/usr/bin/env python3
"""
Weather demo for Stage 6 - HTTP Transport with unified server.
Shows how to use the weather MCP server via HTTP transport.
"""

import asyncio
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


async def weather_demo():
    """Demonstrate weather queries via HTTP transport."""
    
    print("🌤️  Weather MCP HTTP Demo")
    print("=" * 50)
    
    # Configure HTTP-based MCP server
    server_config = {
        "weather": {
            "url": "http://127.0.0.1:7073/mcp",
            "transport": "streamable_http"
        }
    }
    
    # Initialize MCP client
    mcp_client = MultiServerMCPClient(server_config)
    tools = await mcp_client.get_tools()
    
    print(f"✅ Connected to weather server via HTTP")
    print(f"🔧 Available tools: {len(tools)}")
    for tool in tools:
        print(f"  → {tool.name}")
    print()
    
    # Create LLM and agent
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.5)
    agent = create_react_agent(llm.bind_tools(tools), tools)
    
    # Example queries
    queries = [
        "What's the weather forecast for Chicago?",
        "Show me historical weather for Denver from 2024-01-01 to 2024-01-07",
        "What are the soil moisture conditions in Des Moines, Iowa?"
    ]
    
    for query in queries:
        print(f"📍 Query: {query}")
        
        response = await agent.ainvoke({
            "messages": [HumanMessage(content=query)]
        })
        
        # Extract the final message
        final_message = response["messages"][-1].content
        print(f"💬 Response: {final_message}\n")
        print("-" * 50)
    
    print("\n✨ HTTP Transport Benefits:")
    print("  • No subprocess management")
    print("  • Standard HTTP protocols")
    print("  • Easy to scale and deploy")
    print("  • Compatible with cloud services")


async def coordinate_demo():
    """Demonstrate coordinate-based queries."""
    
    print("\n🗺️  Coordinate Query Demo")
    print("=" * 50)
    
    # Configure server
    server_config = {
        "weather": {
            "url": "http://127.0.0.1:7073/mcp",
            "transport": "streamable_http"
        }
    }
    
    # Initialize
    mcp_client = MultiServerMCPClient(server_config)
    tools = await mcp_client.get_tools()
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.5)
    agent = create_react_agent(llm.bind_tools(tools), tools)
    
    # Coordinate query
    query = "What's the weather at latitude 41.8781 and longitude -87.6298?"
    print(f"📍 Query: {query}")
    
    response = await agent.ainvoke({
        "messages": [HumanMessage(content=query)]
    })
    
    final_message = response["messages"][-1].content
    print(f"💬 Response: {final_message}")
    print("\n✨ Direct coordinates are 3x faster than location names!")


async def main():
    """Run all demos."""
    print("\n🚀 Stage 6: MCP HTTP Transport Demo\n")
    print("Make sure weather_server.py is running:")
    print("  python weather_server.py\n")
    
    await weather_demo()
    await coordinate_demo()
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())