#!/usr/bin/env python3
"""
Demo scenarios that showcase the different weather agent capabilities.

This module demonstrates:
- Single agent queries (Forecast, Historical, Agricultural)
- Multi-agent coordination
- Multi-turn conversation with memory
- Agricultural decision-making scenarios
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_agent.mcp_agent import MCPWeatherAgent

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_scenario_header(title: str, explanation: str):
    """Print a formatted scenario header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{explanation}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_query(query: str):
    """Print a formatted query."""
    print(f"{Colors.YELLOW}📝 Query:{Colors.ENDC} {query}")

def print_agent_info(agent_name: str):
    """Print which agent is being used."""
    print(f"{Colors.BLUE}🤖 Using Agent:{Colors.ENDC} {agent_name}")

def print_response(response: str):
    """Print the agent response."""
    print(f"\n{Colors.GREEN}📍 Response:{Colors.ENDC}")
    print(response)

def extract_agents_used(response: str) -> List[str]:
    """Extract which agents were used from the response."""
    agents = []
    if "forecast" in response.lower() or "weather forecast" in response.lower():
        agents.append("Forecast")
    if "historical" in response.lower() or "last month" in response.lower() or "past" in response.lower():
        agents.append("Historical")
    if "soil" in response.lower() or "agricultural" in response.lower() or "crop" in response.lower():
        agents.append("Agricultural")
    return agents if agents else ["Unknown"]

async def run_single_query(agent: MCPWeatherAgent, query: str, expected_agent: str):
    """Run a single query and display results."""
    print_query(query)
    
    start_time = time.time()
    response = await agent.query(query)
    elapsed_time = time.time() - start_time
    
    # Determine which agents were actually used
    if expected_agent == "Multiple":
        agents_used = extract_agents_used(response)
        print_agent_info(", ".join(agents_used))
    else:
        print_agent_info(expected_agent)
    
    print_response(response)
    print(f"\n{Colors.CYAN}⏱️  Response time: {elapsed_time:.2f} seconds{Colors.ENDC}")
    
    return response

# ============================================================================
# BASIC DEMOS
# ============================================================================

async def run_basic_demos():
    """Run basic single-agent demonstrations."""
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("🌟 Basic Weather Agent Demos 🌟")
    print(f"{Colors.ENDC}")
    print("This demo showcases the capabilities of our three specialized agents:")
    print("• Forecast Agent - Current conditions and predictions")
    print("• Historical Agent - Past weather data and trends")
    print("• Agricultural Agent - Farming-specific insights")
    
    # Define scenarios that demonstrate each agent
    scenarios = [
        {
            "title": "Forecast Agent Example",
            "query": "What's the weather forecast for Fresno, California for the next week?",
            "expected_agent": "Forecast",
            "explanation": "Future weather queries go to the Forecast Agent"
        },
        {
            "title": "Historical Agent Example", 
            "query": "How much rain did Ames, Iowa get last month?",
            "expected_agent": "Historical",
            "explanation": "Past weather queries go to the Historical Agent"
        },
        {
            "title": "Agricultural Agent Example",
            "query": "Check the soil moisture and evapotranspiration in Lubbock, Texas",
            "expected_agent": "Agricultural",
            "explanation": "Farming queries go to the Agricultural Agent"
        },
        {
            "title": "Multi-Agent Coordination",
            "query": "I need to plant corn in Grand Island, Nebraska. Is the soil ready and what's the weather looking like?",
            "expected_agent": "Multiple",
            "explanation": "Complex queries use multiple agents"
        }
    ]
    
    # Run each scenario
    for scenario in scenarios:
        print_scenario_header(scenario["title"], scenario["explanation"])
        
        try:
            response = await run_single_query(
                agent, 
                scenario["query"], 
                scenario["expected_agent"]
            )
            
            # Validate multi-agent coordination
            if scenario["expected_agent"] == "Multiple":
                agents_used = extract_agents_used(response)
                if len(agents_used) > 1:
                    print(f"\n{Colors.GREEN}✅ Confirmed: Multiple agents coordinated!{Colors.ENDC}")
                    print(f"   Agents involved: {', '.join(agents_used)}")
                else:
                    print(f"\n{Colors.YELLOW}⚠️  Warning: Expected multiple agents but detected: {agents_used}{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error in scenario: {e}{Colors.ENDC}")
        
        # Pause between scenarios
        await asyncio.sleep(2)
    
    # Clean up
    await agent.cleanup()

# ============================================================================
# MULTI-TURN DEMOS
# ============================================================================

class MultiTurnDemo:
    """Demonstrates multi-turn conversations with MCP servers."""
    
    def __init__(self):
        self.agent = MCPWeatherAgent()
        self.conversation_history = []
    
    async def initialize(self):
        """Initialize MCP connections."""
        print(f"{Colors.CYAN}🔌 Initializing MCP servers...{Colors.ENDC}")
        await self.agent.initialize()
        print(f"{Colors.GREEN}✅ Ready for multi-turn conversation!{Colors.ENDC}\n")
    
    async def have_conversation(self, query: str, pause: float = 1.5) -> str:
        """Process a query and display it conversationally."""
        # Display user query
        print(f"{Colors.YELLOW}👤 User:{Colors.ENDC} {query}")
        print(f"{Colors.BLUE}💭 Thinking...{Colors.ENDC}")
        
        # Get response
        response = await self.agent.query(query)
        
        # Display response
        print(f"{Colors.GREEN}🤖 Assistant:{Colors.ENDC} {response}")
        
        # Store in history
        self.conversation_history.append((query, response))
        
        # Pause for readability
        await asyncio.sleep(pause)
        
        return response
    
    async def run_scenario(self, scenario_name: str, conversations: List[str]):
        """Run a conversation scenario."""
        print(f"\n{Colors.MAGENTA}{'='*60}")
        print(f"📍 Scenario: {scenario_name}")
        print(f"{'='*60}{Colors.ENDC}\n")
        
        # Clear history for new scenario to start fresh
        self.agent.clear_history()
        self.conversation_history = []
        
        for i, query in enumerate(conversations, 1):
            print(f"{Colors.CYAN}Turn {i}:{Colors.ENDC}")
            await self.have_conversation(query)
            print()  # Add spacing between turns
    
    async def cleanup(self):
        """Clean up MCP connections."""
        await self.agent.cleanup()


async def run_mcp_multi_turn_demo():
    """Demo: MCP-based multi-turn conversations with agricultural planning context."""
    demo = MultiTurnDemo()
    
    # Calculate date ranges for queries
    today = datetime.now()
    last_year_start = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    last_year_end = (today - timedelta(days=358)).strftime("%Y-%m-%d")
    last_month_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    last_month_end = today.strftime("%Y-%m-%d")
    
    try:
        await demo.initialize()
        
        # Scenario 1: Corn Planting Decision in Iowa
        await demo.run_scenario(
            "Corn Planting Decision in Ames, Iowa",
            [
                "What's the weather forecast for Ames, Iowa for the next week?",
                "Based on that forecast, is it a good time to plant corn?",
                f"How does this week's forecast compare to historical data for from {last_year_start} to {last_year_end}?",
                "What about current soil moisture conditions?",
                "Given all this information, should I plant corn this week or wait?"
            ]
        )
        
        # Scenario 2: Cross-Location Comparison
        await demo.run_scenario(
            "Comparing Agricultural Conditions Across Regions",
            [
                "What's the current weather forecast for the next 5 days in Fresno, California?",
                "Now show me the same 5-day forecast for Grand Island, Nebraska",
                "Based on these forecasts, which location has better conditions for irrigation scheduling this week?",
                "What crops would you recommend for Fresno vs Grand Island based on current conditions?",
                "Show me the frost risk analysis for both Fresno and Grand Island",
                "Considering all factors, which location would be better for starting a vegetable farm?"
            ]
        )
        
        # Scenario 3: Contextual Weather Tracking
        await demo.run_scenario(
            "Weather Pattern Tracking with Context",
            [
                "What's the 7-day weather forecast for Lubbock, Texas?",
                "Are there any severe weather warnings or high winds expected in Lubbock?",
                f"Compare Lubbock's recent precipitation from {last_month_start} to {last_month_end} with the same period last year",
                "Based on current soil moisture and precipitation data, is Lubbock experiencing drought conditions?",
                "What specific agricultural practices would you recommend for cotton farmers in Lubbock given these conditions?"
            ]
        )
        
        print(f"\n{Colors.GREEN}{'='*60}")
        print(f"✅ MCP multi-turn demo complete!")
        print(f"{'='*60}{Colors.ENDC}")
        
        # Summary statistics
        print(f"\n{Colors.CYAN}📊 Demo Statistics:{Colors.ENDC}")
        print(f"  • Total conversations: {len(demo.conversation_history)}")
        print(f"  • Scenarios completed: 3")
        print(f"  • MCP servers used: forecast, historical, agricultural")
        
    finally:
        await demo.cleanup()


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

async def main():
    """Main entry point for demo scenarios."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Weather Agent Demo Scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Demo modes:
  basic - Run basic single-agent demos (default)
  mcp   - Run MCP-based multi-turn conversation demos  
  all   - Run all demo scenarios

All demos use MCP (Model Context Protocol) servers that run as separate 
processes for forecast, historical, and agricultural weather data.
        """
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='basic',
        choices=['basic', 'mcp', 'all'],
        help='Demo mode to run'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'basic':
        await run_basic_demos()
    elif args.mode == 'mcp':
        await run_mcp_multi_turn_demo()
    elif args.mode == 'all':
        print(f"{Colors.HEADER}{Colors.BOLD}🌟 Running All Demo Scenarios 🌟{Colors.ENDC}\n")
        await run_basic_demos()
        await run_mcp_multi_turn_demo()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}Demo completed successfully! 🎉{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main())