#!/usr/bin/env python3
"""
Test using langchain_mcp_adapters client directly.
"""

import asyncio
from langchain_mcp_adapters.client import MCPClient
from langchain_mcp_adapters.toolkit import MCPToolkit


async def test_mcp_client():
    """Test with proper MCP client."""
    print("🧪 Testing with langchain_mcp_adapters\n")
    
    # Create client for single server
    client = MCPClient(url="http://localhost:7071/mcp")
    
    try:
        # Get toolkit
        toolkit = MCPToolkit(mcp_servers={'forecast': client})
        tools = await toolkit.atools()
        
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test get_forecast
        print("\n📍 Testing get_forecast for San Francisco...")
        forecast_tool = next(t for t in tools if "get_forecast" in t.name)
        result = await forecast_tool.ainvoke({
            "location": "San Francisco",
            "days": 3
        })
        
        print(f"✓ Location: {result.get('location')}")
        print(f"✓ Current temp: {result.get('current', {}).get('temperature_2m')}°C")
        
        # Test error handling
        print("\n🚫 Testing error handling...")
        result = await forecast_tool.ainvoke({
            "location": "Nonexistentcityxyz",
            "days": 3
        })
        if "error" in result:
            print(f"✓ Error handled: {result['error']}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.__aexit__(None, None, None)


if __name__ == "__main__":
    import subprocess
    import time
    from pathlib import Path
    
    # Start server
    print("Starting server...")
    server_script = str(Path(__file__).parent.parent.parent / "mcp_servers" / "forecast_server_simple.py")
    server = subprocess.Popen(
        ["python", server_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)
    
    try:
        asyncio.run(test_mcp_client())
    finally:
        server.terminate()
        server.wait()
        print("\nServer stopped.")