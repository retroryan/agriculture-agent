"""
MCP Weather Agent using LangGraph

This module demonstrates how to use MCP servers with LangGraph:
- Uses create_react_agent for robust tool handling
- MCP servers run as stdio subprocesses
- Automatic tool discovery and execution
- Claude's native tool calling works through LangChain
"""

import asyncio
import os
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import uuid

# Load environment variables
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass


class MCPWeatherAgent:
    """
    A weather agent that uses MCP servers with LangGraph.
    
    This demonstrates the correct approach:
    1. MCP servers run as stdio subprocesses
    2. Tools are discovered dynamically
    3. LangGraph's create_react_agent handles tool execution
    4. Claude's native tool calling works automatically
    """
    
    def __init__(self):
        # Create LLM instance
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0
        )
        
        # Initialize properties
        self.mcp_client = None
        self.tools = []
        self.agent = None
        
        # Initialize conversation ID
        self.conversation_id = str(uuid.uuid4())
        
        # System message for the agent
        self.system_message = SystemMessage(
            content="""You are a helpful weather assistant. Use the available tools to answer questions about weather, historical data, and agricultural conditions.

When users ask about weather, ALWAYS use the available tools to get data. Make reasonable assumptions:

For ambiguous locations:
- "Fresno" → "Fresno, CA" (most populous)
- "Grand Island" → "Grand Island, NE" (agricultural region)
- "Ames" → "Ames, IA" (agricultural region)

For time periods when not specified:
- General forecast → next 7 days
- "last month" → previous 30 days
- Agricultural/planting → next 14 days

Always call tools first with reasonable defaults, then provide specific data. Only ask for clarification if the tool call fails."""
        )
        
        # Initialize message history (reset for each query to avoid state issues)
        self.messages = []
        
    async def initialize(self):
        """Initialize MCP connections and create the LangGraph agent."""
        # Get path to MCP servers
        mcp_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "mcp_servers"
        )
        
        # Configure MCP servers
        server_config = {
            "forecast": {
                "command": "python",
                "args": [os.path.join(mcp_path, "forecast_server.py")],
                "transport": "stdio"
            },
            "historical": {
                "command": "python",
                "args": [os.path.join(mcp_path, "historical_server.py")],
                "transport": "stdio"
            },
            "agricultural": {
                "command": "python", 
                "args": [os.path.join(mcp_path, "agricultural_server.py")],
                "transport": "stdio"
            }
        }
        
        # Create MCP client and discover tools
        self.mcp_client = MultiServerMCPClient(server_config)
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
        Process a query using the LangGraph agent.
        
        The agent will:
        1. Understand the user's query
        2. Call appropriate MCP tools automatically
        3. Return a natural language response
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # Create messages for this query (fresh state to avoid tool_use_id issues)
        messages = [self.system_message, HumanMessage(content=user_query)]
        
        try:
            # Run the agent
            result = await asyncio.wait_for(
                self.agent.ainvoke({"messages": messages}),
                timeout=120.0
            )
            
            # Log which tools were used
            tool_calls = []
            for msg in result["messages"]:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for call in msg.tool_calls:
                        tool_calls.append(call['name'])
            
            if tool_calls:
                print(f"\n🔧 Tools used: {', '.join(set(tool_calls))}")
            
            # Return the final response
            final_message = result["messages"][-1]
            return final_message.content
            
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Query timed out after 120 seconds")
        except Exception as e:
            print(f"\n❌ Error during query: {e}")
            import traceback
            traceback.print_exc()
            return f"An error occurred: {str(e)}"
    
    def clear_history(self):
        """
        Clear conversation history.
        
        This is useful when starting a new topic or conversation.
        """
        # Reset message history
        self.messages = []
        
        # Generate new conversation ID
        self.conversation_id = str(uuid.uuid4())
    
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