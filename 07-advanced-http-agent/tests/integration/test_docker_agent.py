#!/usr/bin/env python3
"""
Test script to verify Docker deployment with LangGraph agent.
"""

import asyncio
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient


def get_model(temperature=0):
    """Get Claude model with temperature setting."""
    return ChatAnthropic(
        model="claude-3-haiku-20240307",
        temperature=temperature
    )


async def test_docker_deployment():
    """Test the Docker deployment with a simple agent."""
    print("🐳 Testing Docker Deployment with LangGraph Agent\n")
    
    # Configure MCP client to use Docker container
    server_config = {
        "forecast": {
            "url": "http://localhost:7072/mcp",  # Docker container port
            "transport": "streamable_http"
        }
    }
    
    # Initialize components
    llm = get_model(temperature=0)
    
    print("1. Connecting to Docker container...")
    mcp_client = MultiServerMCPClient(server_config)
    tools = await mcp_client.get_tools()
    
    print(f"   ✓ Connected! Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}")
    
    print("\n2. Creating LangGraph agent...")
    agent = create_react_agent(llm.bind_tools(tools), tools)
    print("   ✓ Agent created")
    
    print("\n3. Testing Docker deployment...")
    query = "What's the current weather in Paris?"
    print(f"   Query: {query}")
    
    try:
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=query)]
        })
        
        final_message = result["messages"][-1]
        print(f"   ✓ Response: {final_message.content[:100]}...")
        
        # Check if tools were used
        tool_calls = []
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_calls.extend([tc["name"] for tc in msg.tool_calls])
        
        if tool_calls:
            print(f"   ✓ Tools used: {', '.join(tool_calls)}")
        
        print("\n✅ Docker deployment test successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("Make sure Docker container is running:")
    print("docker run -d -p 7072:7071 weather-forecast-server\n")
    
    success = asyncio.run(test_docker_deployment())
    exit(0 if success else 1)