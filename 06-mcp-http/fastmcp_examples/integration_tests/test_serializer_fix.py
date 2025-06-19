#!/usr/bin/env python3
"""
Direct test of the serializer server fix for empty arguments
"""
import asyncio
import subprocess
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import Client

async def test_serializer_fix():
    """Test that the serializer server accepts empty arguments"""
    # Start the serializer server
    server_process = subprocess.Popen(
        [sys.executable, "servers/serializer.py"],
        cwd=Path(__file__).parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give server time to start
    time.sleep(3)
    
    try:
        # Test with empty arguments (what langchain-mcp-adapters sends)
        async with Client("http://127.0.0.1:8000/mcp") as client:
            # This should not raise a validation error
            result = await client.call_tool("get_example_data", {})
            print(f"✅ Success! Got result: {result[0].text}")
            
            # Verify the data is correct
            if "name: Test" in result[0].text and "value: 123" in result[0].text:
                print("✅ Data format is correct")
                return True
            else:
                print("❌ Unexpected data format")
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
    print("Testing serializer server fix for empty arguments")
    print("=" * 60)
    success = asyncio.run(test_serializer_fix())
    sys.exit(0 if success else 1)