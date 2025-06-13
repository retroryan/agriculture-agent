#!/usr/bin/env python3
"""Debug MCP server directly."""

import asyncio
import json
import subprocess
import sys

async def test_forecast_server():
    """Test forecast server with direct JSON-RPC."""
    print("Testing forecast server...")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "04-mcp-architecture/mcp_servers/forecast_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialization message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "debug", "version": "1.0.0"}
            }
        }
        
        print("Sending initialization...")
        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Init response: {response.strip()}")
        
        # List tools
        list_tools_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("Listing tools...")
        process.stdin.write(json.dumps(list_tools_msg) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print(f"Tools response: {response.strip()}")
        
        # Call tool
        call_tool_msg = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather_forecast",
                "arguments": {
                    "location": "Ames, Iowa",
                    "days": 3
                }
            }
        }
        
        print("Calling tool...")
        process.stdin.write(json.dumps(call_tool_msg) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print(f"Tool response: {response.strip()}")
        
        # Check for any stderr output
        try:
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"Server stderr: {stderr_output}")
        except:
            pass
        
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    asyncio.run(test_forecast_server())