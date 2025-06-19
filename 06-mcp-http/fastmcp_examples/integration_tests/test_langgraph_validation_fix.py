#!/usr/bin/env python3
"""
Test script to verify the validation error fix for LangGraph agent demo
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

async def test_validation_fix():
    """Test the specific query that was causing validation errors"""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        return False
    
    # Initialize MCP client
    client = MultiServerMCPClient({
        "serializer": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http"
        }
    })
    
    try:
        # Get tools from MCP server
        print("Connecting to MCP server...")
        tools = await client.get_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Create LangGraph agent
        llm = ChatAnthropic(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-haiku-20240307"
        )
        agent = create_react_agent(llm, tools)
        
        # Test the specific query that was failing
        query = "What format is the data in?"
        print(f"\nUser: {query}")
        print("Claude: ", end="", flush=True)
        
        # Collect the response
        tool_used = False
        data_retrieved = False
        error_occurred = False
        
        async for chunk in agent.astream({"messages": [("user", query)]}):
            if "agent" in chunk:
                for message in chunk["agent"]["messages"]:
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        if not tool_used:
                            print("Let me fetch that data for you...", flush=True)
                            tool_used = True
                    elif hasattr(message, 'content') and message.content:
                        if isinstance(message.content, str):
                            if "ToolException" in message.content or "validation error" in message.content:
                                error_occurred = True
                            print(message.content, end="", flush=True)
            elif "tools" in chunk:
                for message in chunk["tools"]["messages"]:
                    if hasattr(message, 'content'):
                        content = message.content
                        if "ToolException" in str(content) or "validation error" in str(content):
                            error_occurred = True
                            print(f"\n\n❌ Error occurred: {content}\n")
                        else:
                            data_retrieved = True
                            print(f"\n\nData retrieved:\n{content}\n")
                        print("Claude: ", end="", flush=True)
        
        print("\n")
        
        if error_occurred:
            print("❌ Test FAILED - Validation error occurred")
            return False
        elif data_retrieved:
            print("✅ Test PASSED - Data retrieved successfully without validation errors")
            return True
        else:
            print("❌ Test FAILED - No data retrieved")
            return False
            
    except Exception as e:
        print(f"\n❌ Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test entry point"""
    print("Testing LangGraph Agent Demo Validation Fix")
    print("=" * 60)
    print("This test verifies that the 'What format is the data in?' query works")
    print("without validation errors when langchain-mcp-adapters passes empty args")
    print("=" * 60)
    
    # Ensure server is running
    print("\nNote: Make sure the serializer server is running on http://localhost:8000")
    print("If not, run: python servers/serializer.py")
    print()
    
    success = await test_validation_fix()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
        sys.exit(1)