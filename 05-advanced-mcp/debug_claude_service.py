#!/usr/bin/env python3
"""Debug Claude service tool calling"""

import asyncio
import sys
import json
sys.path.append('.')

from weather_agent.claude_service import ClaudeService
from weather_agent.tool_registry import ToolRegistry


async def debug_claude_service():
    """Debug Claude service tool calling."""
    print("🐛 Debugging Claude Service Tool Calling")
    print("=" * 50)
    
    # Create service and registry
    service = ClaudeService()
    registry = service.tool_registry
    
    # Register a test tool
    registry.register_tool(
        name="get_weather",
        description="Get weather for a location",
        input_schema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for"
                }
            },
            "required": ["location"]
        }
    )
    
    # Set a handler
    async def test_handler(args):
        return {"temperature": 72, "condition": "sunny", "location": args.get("location")}
    
    registry.set_handler("get_weather", test_handler)
    
    # Get tools that will be sent to Claude
    tools = registry.get_tools_schema()
    print("\n📋 Tools being sent to Claude:")
    print(json.dumps(tools, indent=2))
    
    # Test a query
    query = "What's the weather in Lubbock, Texas?"
    print(f"\n📝 Query: {query}")
    
    try:
        response, tool_calls = await service.execute_with_tools(query)
        
        print(f"\n🔧 Tool calls made: {len(tool_calls)}")
        for tc in tool_calls:
            print(f"  - {tc.tool_name}: {tc.arguments}")
        
        print(f"\n🤖 Response: {response}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_claude_service())