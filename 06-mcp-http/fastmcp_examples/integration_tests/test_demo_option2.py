#!/usr/bin/env python3
"""
Integration test for demo.py option 2 - LangGraph agent demo
Specifically tests the "What format is the data in?" query
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

# Load environment variables
load_dotenv()

async def test_demo_option2():
    """Test demo.py option 2 with the specific query that was failing"""
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
    time.sleep(3)
    
    # Verify server is running
    import aiohttp
    async def check_server():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://127.0.0.1:8000/mcp") as resp:
                    return resp.status == 200
        except:
            return False
    
    # Wait for server to be ready
    for _ in range(10):
        if await check_server():
            break
        time.sleep(1)
    else:
        print("Server failed to start")
        server_process.terminate()
        return False
    
    try:
        # Run demo.py with option 2 input
        demo_process = subprocess.Popen(
            [sys.executable, "client/demo.py"],
            cwd=Path(__file__).parent.parent,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send option 2 and wait for demo to execute
        stdout, stderr = demo_process.communicate(input="2\n4\n", timeout=30)
        
        # Check if the error occurred
        if "ToolException" in stdout or "validation error" in stdout:
            print("❌ Test failed - validation error still occurs")
            print("\nStdout:")
            print(stdout)
            print("\nStderr:")
            print(stderr)
            return False
        
        # Check if we got the expected data output
        if "name: Test" in stdout and "value: 123" in stdout and "status: true" in stdout:
            print("✅ Test passed - got expected data output")
            return True
        else:
            print("❌ Test failed - didn't get expected data")
            print("\nStdout:")
            print(stdout)
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
    print("Testing demo.py option 2 - LangGraph agent demo")
    print("=" * 60)
    success = asyncio.run(test_demo_option2())
    sys.exit(0 if success else 1)