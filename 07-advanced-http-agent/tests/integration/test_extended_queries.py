#!/usr/bin/env python3
"""
Extended test script for testing edge cases and various query types.
"""

import asyncio
import subprocess
import time
import os
from pathlib import Path
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables from project root
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
except ImportError:
    print("python-dotenv not available, using system environment")


def get_model(temperature=0):
    """Get Claude model with temperature setting."""
    return ChatAnthropic(
        model="claude-3-haiku-20240307",
        temperature=temperature
    )


async def test_extended_queries():
    """Test various query types and edge cases."""
    print("🧪 Extended Query Testing\n")
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    # Start server
    print("Starting forecast server...")
    server_script = str(Path(__file__).parent.parent.parent / "mcp_servers" / "forecast_server_simple.py")
    server_process = subprocess.Popen(
        ["python", server_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Wait for server to start
    
    try:
        # Initialize components
        llm = get_model(temperature=0)
        
        server_config = {
            "forecast": {
                "url": "http://127.0.0.1:7071/mcp",
                "transport": "streamable_http"
            }
        }
        
        print("1. Connecting to MCP server...")
        mcp_client = MultiServerMCPClient(server_config)
        tools = await mcp_client.get_tools()
        print(f"   ✓ Connected! Found {len(tools)} tools")
        
        print("\n2. Creating LangGraph agent...")
        agent = create_react_agent(llm.bind_tools(tools), tools)
        print("   ✓ Agent created")
        
        # Extended test queries covering different scenarios
        test_queries = [
            # Basic weather queries
            "What's the weather like in Berlin today?",
            "Give me a 5-day forecast for Miami",
            
            # Location variations
            "How's the weather in New York City?", 
            "What's the temperature in São Paulo, Brazil?",
            "Tell me about weather conditions in Mumbai, India",
            
            # Specific weather aspects
            "Is it raining in Seattle right now?",
            "What's the wind speed in Chicago?",
            "How hot is it in Phoenix today?",
            
            # Multi-day forecasts
            "What will the weather be like in Vancouver for the next 3 days?",
            "Give me a week-long forecast for Sydney",
            
            # Edge cases
            "What's the weather in a small town like Podunk?",  # Geocoding challenge
            "Tell me about weather conditions in Antarctica",   # Extreme location
        ]
        
        print("\n3. Testing extended query scenarios...")
        success_count = 0
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}/{len(test_queries)}: {query}")
            
            try:
                result = await agent.ainvoke({
                    "messages": [HumanMessage(content=query)]
                })
                
                final_message = result["messages"][-1]
                response_length = len(final_message.content)
                
                # Check if tools were used
                tool_calls = []
                for msg in result["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_calls.extend([tc["name"] for tc in msg.tool_calls])
                
                if tool_calls and response_length > 50:  # Reasonable response length
                    print(f"   ✓ Success - Tools: {', '.join(tool_calls)}, Response: {response_length} chars")
                    success_count += 1
                else:
                    print(f"   ⚠️  Partial - Tools: {', '.join(tool_calls) if tool_calls else 'None'}, Response: {response_length} chars")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}...")
        
        print(f"\n📊 Results Summary:")
        print(f"   ✓ Successful queries: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.1f}%)")
        
        # Success criteria: 80% of queries should work
        success = success_count >= len(test_queries) * 0.8
        
        if success:
            print("✅ Extended testing passed!")
        else:
            print("❌ Extended testing needs improvement")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
        
    finally:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")


if __name__ == "__main__":
    success = asyncio.run(test_extended_queries())
    exit(0 if success else 1)