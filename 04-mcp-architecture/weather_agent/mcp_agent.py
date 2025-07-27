"""
Simple MCP Weather Agent

This module demonstrates how to use MCP servers with LangGraph.
Key concepts:
- MCP servers run as stdio subprocesses
- Communication happens via JSON-RPC over stdin/stdout
- LangGraph's MultiServerMCPClient handles the subprocess management
"""

import asyncio
import os
from typing import List
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

# Import unified model configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_model


class MCPWeatherAgent:
    """
    A simple weather agent that uses MCP servers.
    
    This demonstrates the core MCP concepts:
    1. Servers run as subprocesses
    2. Communication via stdio (stdin/stdout)
    3. Tools are discovered dynamically
    4. Conversation context is maintained across queries
    """
    
    def __init__(self):
        # Create LLM using unified model interface
        self.llm = get_model(temperature=0.7)
        self.mcp_client = None
        self.tools = []
        self.agent = None
        
        # Initialize message history with system message
        self.messages = [
            SystemMessage(content="You are a helpful weather assistant. Use the available tools to answer questions about weather, historical data, and agricultural conditions.")
        ]
        
    async def initialize(self):
        """Initialize MCP connections and create the agent."""
        # Get path to MCP servers
        mcp_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "mcp_servers"
        )
        
        # Configure unified MCP server - runs as a single subprocess
        server_config = {
            "weather": {
                "command": "python",
                "args": [os.path.join(mcp_path, "weather_server.py")],
                "transport": "stdio"  # This is the only transport MCP supports
            }
        }
        
        # Create MCP client - this spawns the server subprocesses
        self.mcp_client = MultiServerMCPClient(server_config)
        
        # Discover tools from the servers
        self.tools = await self.mcp_client.get_tools()
        print(f"✅ Connected to {len(server_config)} MCP servers")
        print(f"🔧 Available tools: {len(self.tools)}")
        for tool in self.tools:
            print(f"  → {tool.name}: {tool.description[:60]}...")
        
        # Create React agent with discovered tools
        self.agent = create_react_agent(
            self.llm.bind_tools(self.tools),
            self.tools
        )
    
    async def query(self, user_query: str) -> str:
        """
        Process a query using MCP tools while maintaining conversation context.
        
        The agent will:
        1. Add the query to conversation history
        2. Analyze with full context
        3. Call appropriate MCP server tools via stdio
        4. Return a natural language response
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # Append user message to conversation history
        self.messages.append(HumanMessage(content=user_query))
        
        # Run agent with full message history
        try:
            result = await asyncio.wait_for(
                self.agent.ainvoke({"messages": self.messages}),
                timeout=120.0
            )
            
            # Update messages with full history (including tool calls and responses)
            self.messages = result["messages"]
            
            # Log which tools were used
            tool_calls = []
            for msg in result["messages"]:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for call in msg.tool_calls:
                        tool_calls.append(call['name'])
            
            if tool_calls:
                print(f"\n🔧 MCP tools used: {', '.join(set(tool_calls))}")
            
            # Return the final response
            return self.messages[-1].content
            
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Query timed out after 120 seconds")
    
    def clear_history(self):
        """
        Clear conversation history while keeping the system message.
        
        This is useful when starting a new topic or conversation.
        """
        # Reset to just the system message
        self.messages = [self.messages[0]]
    
    async def cleanup(self):
        """Clean up MCP connections (subprocesses are terminated automatically)."""
        # The MultiServerMCPClient handles subprocess cleanup
        pass


# Convenience function
async def create_mcp_weather_agent():
    """Create and initialize an MCP weather agent."""
    agent = MCPWeatherAgent()
    await agent.initialize()
    return agent