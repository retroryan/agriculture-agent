#!/usr/bin/env python3
"""Debug tool schemas"""

import asyncio
import sys
import json
sys.path.append('.')

from weather_agent.mcp_agent import MCPWeatherAgent


async def debug_tools():
    """Debug tool schemas."""
    print("🐛 Debugging Tool Schemas")
    print("=" * 50)
    
    # Create agent
    agent = MCPWeatherAgent()
    
    try:
        # Initialize
        print("\n🔌 Initializing MCP connections...")
        await agent.initialize()
        
        # Print tool schemas
        print("\n📋 Tool Schemas from Registry:")
        schemas = agent.tool_registry.get_tools_schema()
        for schema in schemas:
            print(f"\n Tool: {schema['name']}")
            print(f" Description: {schema['description']}")
            print(f" Input Schema: {json.dumps(schema['input_schema'], indent=2)}")
        
        # Test a direct tool call
        print("\n\n🔧 Testing Direct Tool Call:")
        print("Calling get_weather_forecast with location='Ames, IA'")
        
        # Find the forecast tool
        forecast_tool = None
        for tool in agent.tools:
            if 'forecast' in tool.name.lower():
                forecast_tool = tool
                break
        
        if forecast_tool:
            result = await forecast_tool.ainvoke({"location": "Ames, IA"})
            print(f"\nResult: {json.dumps(result, indent=2)[:500]}...")
        else:
            print("❌ Forecast tool not found!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(debug_tools())