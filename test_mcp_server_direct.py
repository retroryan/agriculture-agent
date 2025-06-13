#!/usr/bin/env python3
"""Test MCP server with actual JSON-RPC calls."""

import asyncio
import json
import subprocess
import sys

async def test_server_directly():
    """Test the forecast server with real JSON-RPC."""
    print("Starting forecast server...")
    
    process = subprocess.Popen(
        [sys.executable, "04-mcp-architecture/mcp_servers/forecast_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    try:
        await asyncio.sleep(1)  # Let server start
        
        # Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("Sending initialize...")
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(process.stdout.readline)), 
                timeout=5.0
            )
            print(f"Init response: {response_line.strip()}")
        except asyncio.TimeoutError:
            print("Timeout waiting for init response")
            # Check stderr
            stderr_data = process.stderr.read()
            if stderr_data:
                print(f"Server stderr: {stderr_data}")
            return
        
        # List tools
        tools_req = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("Listing tools...")
        process.stdin.write(json.dumps(tools_req) + "\n")
        process.stdin.flush()
        
        try:
            response_line = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
                timeout=5.0
            )
            print(f"Tools response: {response_line.strip()}")
        except asyncio.TimeoutError:
            print("Timeout waiting for tools response")
            return
            
        # Call tool
        call_req = {
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
        process.stdin.write(json.dumps(call_req) + "\n")
        process.stdin.flush()
        
        try:
            response_line = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
                timeout=10.0
            )
            print(f"Tool call response: {response_line.strip()}")
        except asyncio.TimeoutError:
            print("Timeout waiting for tool response")
            stderr_data = process.stderr.read()
            if stderr_data:
                print(f"Server stderr: {stderr_data}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        process.terminate()
        try:
            await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(process.wait)),
                timeout=2.0
            )
        except:
            process.kill()

if __name__ == "__main__":
    asyncio.run(test_server_directly())