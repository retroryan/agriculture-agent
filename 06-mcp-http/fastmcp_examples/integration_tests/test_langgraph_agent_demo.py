#!/usr/bin/env python3
"""
Integration test for the LangGraph agent demo option 2
Tests the specific scenario where Claude calls get_example_data tool
"""
import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

async def test_langgraph_agent_demo():
    """Test the specific failing scenario from option 2"""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found")
        return False
    
    # Start the serializer server
    server_process = subprocess.Popen(
        [sys.executable, "servers/serializer.py"],
        cwd=Path(__file__).parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give server time to start
    time.sleep(2)
    
    try:
        # Initialize MCP client
        client = MultiServerMCPClient({
            "serializer": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http"
            }
        })
        
        # Get tools from MCP server
        print("Connecting to MCP server...")
        tools = await client.get_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Create LangGraph agent
        llm = ChatAnthropic(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-haiku-20240307"
        )
        agent = create_react_agent(llm, tools)
        
        # Test the specific query that fails
        query = "What format is the data in?"
        print(f"\nTesting query: {query}")
        
        # Process the query
        messages_collected = []
        async for chunk in agent.astream({"messages": [("user", query)]}):
            if "agent" in chunk:
                for message in chunk["agent"]["messages"]:
                    messages_collected.append(message)
            elif "tools" in chunk:
                for message in chunk["tools"]["messages"]:
                    messages_collected.append(message)
        
        # Check if we got a proper response
        success = any(hasattr(msg, 'content') and msg.content for msg in messages_collected)
        
        if success:
            print("✅ Test passed - got valid response")
            return True
        else:
            print("❌ Test failed - no valid response")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    success = asyncio.run(test_langgraph_agent_demo())
    sys.exit(0 if success else 1)