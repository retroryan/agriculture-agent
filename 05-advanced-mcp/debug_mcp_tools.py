#!/usr/bin/env python3
"""Debug MCP tool structure"""

import asyncio
import sys
sys.path.append('.')

from weather_agent.mcp_agent import MCPWeatherAgent


async def debug_mcp_tools():
    """Debug MCP tool structure."""
    print("🐛 Debugging MCP Tool Structure")
    print("=" * 50)
    
    # Create agent
    agent = MCPWeatherAgent()
    
    try:
        # Initialize
        print("\n🔌 Initializing MCP connections...")
        await agent.initialize()
        
        # Print tool details
        print(f"\n📋 Found {len(agent.tools)} MCP Tools:")
        for i, tool in enumerate(agent.tools):
            print(f"\n[Tool {i+1}]")
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description[:100]}...")
            print(f"Type: {type(tool)}")
            
            # Check for different schema attributes
            for attr in ['args_schema', 'input_schema', 'schema', '_schema']:
                if hasattr(tool, attr):
                    val = getattr(tool, attr)
                    print(f"{attr}: {type(val)} - {str(val)[:100]}...")
            
            # Print all attributes
            print(f"All attributes: {[a for a in dir(tool) if not a.startswith('_')][:10]}...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(debug_mcp_tools())