#!/usr/bin/env python3
"""
Simple MCP Weather Chatbot

This demonstrates how MCP servers work with stdio subprocesses.
MCP servers are spawned as child processes and communicate via JSON-RPC over stdin/stdout.
"""

import asyncio
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.append('.')

from weather_agent.mcp_agent import MCPWeatherAgent


class SimpleWeatherChatbot:
    """A simple chatbot that uses MCP servers for weather data."""
    
    def __init__(self):
        self.agent = MCPWeatherAgent()
        self.initialized = False
    
    async def initialize(self):
        """Initialize MCP connections."""
        if not self.initialized:
            print("🔌 Initializing MCP connections...")
            await self.agent.initialize()
            self.initialized = True
            print("✅ Ready to answer weather questions!\n")
    
    async def chat(self, query: str) -> str:
        """Process a user query."""
        if not self.initialized:
            await self.initialize()
        
        try:
            response = await self.agent.query(query)
            return response
        except asyncio.TimeoutError:
            return "Sorry, the request timed out. Please try again."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    async def cleanup(self):
        """Clean up MCP connections."""
        if self.initialized:
            await self.agent.cleanup()


async def interactive_mode():
    """Run the chatbot in interactive mode."""
    chatbot = SimpleWeatherChatbot()
    
    # Import agricultural locations
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp_servers'))
    from parameters import AGRICULTURAL_LOCATIONS
    
    print("🌤️  MCP Weather Chatbot")
    print("=" * 50)
    print("Ask me about weather forecasts, historical data,")
    print("or agricultural conditions!")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    print("📍 Known Agricultural Locations:")
    for location, info in AGRICULTURAL_LOCATIONS.items():
        city_state = f"{location.split(',')[0]}, {info['state']}"
        print(f"   • {city_state} - {info['crops']}")
    print()
    
    try:
        await chatbot.initialize()
        
        while True:
            try:
                query = input("\n🤔 You: ").strip()
                
                if query.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print("\n💭 Thinking...")
                response = await chatbot.chat(query)
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
                
    finally:
        await chatbot.cleanup()


async def demo_mode():
    """Run a simple demo showing MCP in action."""
    chatbot = SimpleWeatherChatbot()
    
    print("🌤️  MCP Weather Demo")
    print("=" * 50)
    print("This demo shows MCP servers in action.")
    print("Each server runs as a stdio subprocess.\n")
    
    try:
        await chatbot.initialize()
        
        # Demo queries
        queries = [
            "What's the weather forecast for Ames, Iowa?",
            "Show me historical weather for Fresno last month",
            "Are conditions good for planting in Grand Island?"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'='*50}")
            print(f"Query {i}: {query}")
            print("-" * 50)
            
            response = await chatbot.chat(query)
            print(f"\nResponse: {response}")
            
            if i < len(queries):
                await asyncio.sleep(1)  # Brief pause between queries
        
        print(f"\n{'='*50}")
        print("✅ Demo complete!")
        
    finally:
        await chatbot.cleanup()


async def main():
    """Main entry point."""
    # Check for demo flag
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        await demo_mode()
    else:
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())