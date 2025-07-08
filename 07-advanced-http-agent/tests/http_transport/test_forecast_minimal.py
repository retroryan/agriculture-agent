#!/usr/bin/env python3
"""
Minimal test for simplified forecast server.
"""

import asyncio
import httpx
import json


async def test_direct_http():
    """Test the server directly via HTTP."""
    print("🧪 Testing Simplified Forecast Server via HTTP\n")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Server is running
        print("1. Testing server connectivity...")
        try:
            response = await client.post(
                "http://localhost:7071/mcp/",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1
                },
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
            )
            print(f"   ✓ Server responded with status: {response.status_code}")
            data = response.json()
            tools = data.get("result", {}).get("tools", [])
            print(f"   ✓ Found {len(tools)} tools")
            for tool in tools:
                print(f"   - {tool['name']}")
        except Exception as e:
            print(f"   ❌ Failed to connect: {e}")
            return False
            
        # Test 2: Call get_forecast
        print("\n2. Testing get_forecast tool...")
        try:
            response = await client.post(
                "http://localhost:7071/mcp/",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "get_forecast",
                        "arguments": {
                            "location": "San Francisco",
                            "days": 3
                        }
                    },
                    "id": 2
                },
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
            )
            data = response.json()
            if "result" in data:
                result = data["result"]
                print(f"   ✓ Got forecast for: {result.get('location', 'Unknown')}")
                print(f"   ✓ Current temp: {result.get('current', {}).get('temperature_2m')}°C")
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            
    print("\n✅ Test complete!")
    return True


if __name__ == "__main__":
    print("Starting forecast server first...")
    
    # Start server in background
    import subprocess
    from pathlib import Path
    server_script = str(Path(__file__).parent.parent.parent / "mcp_servers" / "forecast_server_simple.py")
    server_proc = subprocess.Popen(
        ["python", server_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    import time
    time.sleep(3)
    
    try:
        # Run tests
        asyncio.run(test_direct_http())
    finally:
        # Kill server
        server_proc.terminate()
        server_proc.wait()
        print("\nServer stopped.")