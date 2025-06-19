import asyncio
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


load_dotenv()


class SimpleFastMCPAgent:
    """A simple agent that uses FastMCP tools via LangGraph with official MCP adapters."""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.mcp_client = None
        self.agent = None
        
    async def initialize(self):
        """Initialize the agent with discovered FastMCP tools."""
        print("🔄 Connecting to FastMCP server...")
        
        # Initialize MCP client with proper configuration
        self.mcp_client = MultiServerMCPClient({
            "weather": {
                "url": "http://127.0.0.1:7070/mcp",
                "transport": "streamable_http"
            }
        })
        
        # Get tools from the MCP server
        try:
            tools = await self.mcp_client.get_tools()
            if not tools:
                print("❌ No tools found on FastMCP server!")
                return False
            
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            
            # Create the React agent with discovered tools
            self.agent = create_react_agent(self.llm, tools)
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            print("\nMake sure the server is running:")
            print("  python serializer.py")
            return False
    
    async def chat(self, message: str) -> str:
        """Process a single chat message."""
        if not self.agent:
            return "Agent not initialized. Please run initialize() first."
        
        # Invoke the agent with proper message format
        result = await self.agent.ainvoke({"messages": [("user", message)]})
        
        # Extract the final message
        if result["messages"]:
            return result["messages"][-1].content
        return "No response generated."
    
    async def run_interactive(self):
        """Run an interactive chat session."""
        if not await self.initialize():
            print("Failed to initialize agent.")
            return
        
        print("\n🤖 FastMCP + LangGraph Agent Ready!")
        print("Type 'quit' to exit, 'help' for available commands.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  - Ask about weather data")
                    print("  - Calculate comfort index for specific temperature/humidity")
                    print("  - Type 'quit' to exit\n")
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = await self.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
        
        print("\n👋 Goodbye!")
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources."""
        # No explicit cleanup needed for MultiServerMCPClient
        pass


async def main():
    """Main entry point for the agent."""
    agent = SimpleFastMCPAgent()
    await agent.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())