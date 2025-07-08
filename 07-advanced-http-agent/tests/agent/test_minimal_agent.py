#!/usr/bin/env python3
"""
Minimal agent test for simplified forecast server.
Tests the full integration with LangGraph and MCP.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from config import get_model


async def test_minimal_agent():
    """Test simplified forecast server with minimal agent setup."""
    print("🧪 Testing Minimal Weather Agent\n")
    
    # Initialize LLM
    llm = get_model(temperature=0)
    
    # Configure single MCP server
    server_config = {
        "forecast": {
            "url": "http://127.0.0.1:7071/mcp",
            "transport": "streamable_http"
        }
    }
    
    # Create MCP client and get tools
    print("1. Connecting to MCP server...")
    mcp_client = MultiServerMCPClient(server_config)
    tools = await mcp_client.get_tools()
    
    print(f"   ✓ Connected! Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}")
    
    # Create simple agent
    print("\n2. Creating LangGraph agent...")
    agent = create_react_agent(llm.bind_tools(tools), tools)
    print("   ✓ Agent created")
    
    # Test queries
    test_queries = [
        "What's the weather in San Francisco?",
        "What's the current temperature in Tokyo?",
        "Give me a 3-day forecast for London"
    ]
    
    print("\n3. Testing queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        
        try:
            # Run agent
            result = await agent.ainvoke({
                "messages": [HumanMessage(content=query)]
            })
            
            # Get final response
            final_message = result["messages"][-1]
            response = final_message.content
            
            # Check if tools were used
            tool_calls = []
            for msg in result["messages"]:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for call in msg.tool_calls:
                        tool_calls.append(call['name'])
            
            print(f"   ✓ Tools used: {', '.join(tool_calls) if tool_calls else 'None'}")
            print(f"   ✓ Response: {response[:150]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    import subprocess
    import time
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)
    
    # Start simplified server
    print("Starting simplified forecast server...")
    server_script = str(Path(__file__).parent.parent.parent / "mcp_servers" / "forecast_server_simple.py")
    server = subprocess.Popen(
        ["python", server_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    time.sleep(3)
    
    try:
        # Run test
        asyncio.run(test_minimal_agent())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        # Cleanup
        print("\nStopping server...")
        server.terminate()
        server.wait()
        print("Server stopped.")