#!/usr/bin/env python3
"""
Demo script showing the complete FastMCP + LangGraph workflow.

This demonstrates:
1. Starting a FastMCP server (you should run serializer.py separately)
2. Creating a LangGraph agent that discovers and uses FastMCP tools
3. Running example queries that showcase the integration
"""

import asyncio
import os
from dotenv import load_dotenv
from langgraph_agent import SimpleFastMCPAgent


load_dotenv()


async def run_full_agent_demo():
    """Run demonstration queries with the FastMCP agent."""
    print("=" * 60)
    print("FastMCP + LangGraph Integration Demo")
    print("=" * 60)
    print("\nMake sure the FastMCP server is running:")
    print("  python serializer.py")
    print("\nContinuing with demo...")
    
    # Create and initialize the agent
    agent = SimpleFastMCPAgent()
    
    print("\n🚀 Initializing agent...")
    if not await agent.initialize():
        print("❌ Failed to initialize. Is the FastMCP server running?")
        return
    
    # Demo queries
    demo_queries = [
        "What weather data is available from the station?",
        "Can you calculate the comfort index for 25°C and 70% humidity?",
        "What would be the comfort level at 18°C with 40% humidity?",
        "Get the current weather station data and tell me if conditions are comfortable based on the temperature and humidity."
    ]
    
    print("\n📋 Running demo queries...\n")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print("-" * 60)
        
        response = await agent.chat(query)
        print(f"Response: {response}")
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Demo completed!")
    print("="*60)
    
    # Cleanup
    await agent.cleanup()


async def run_minimal_example():
    """Run a minimal example showing direct tool usage."""
    print("\n🔧 Minimal FastMCP Tool Usage Example")
    print("-" * 40)
    
    from langgraph_agent import FastMCPTool
    
    # Create tool wrapper
    mcp_tools = FastMCPTool()
    
    try:
        # List available tools
        print("Available tools:")
        tools = await mcp_tools.list_tools()
        for tool in tools:
            print(f"  - {tool.name if hasattr(tool, 'name') else tool}")
        
        # Call a tool directly
        print("\nCalling get_example_data:")
        result = await mcp_tools.call_tool("get_example_data", {})
        print(result)
        
        print("\nCalling calculate_comfort_index(22, 50):")
        result = await mcp_tools.call_tool("calculate_comfort_index", {
            "temperature": 22,
            "humidity": 50
        })
        print(result)
        
    finally:
        await mcp_tools.close()


async def main():
    """Main demo entry point."""
    print("FastMCP + LangGraph Demo")
    print("\nChoose demo mode:")
    print("1. Full agent demo (conversational)")
    print("2. Minimal tool usage example")
    print("3. Interactive chat mode")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        await run_full_agent_demo()
    elif choice == "2":
        await run_minimal_example()
    elif choice == "3":
        agent = SimpleFastMCPAgent()
        await agent.run_interactive()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment.")
        print("Please set it in your .env file or environment variables.")
        exit(1)
    
    asyncio.run(main())