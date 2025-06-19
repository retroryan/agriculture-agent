"""
MCP Weather Agent using LangGraph with Structured Output

This module demonstrates how to use MCP servers with LangGraph:
- Uses create_react_agent for robust tool handling
- MCP servers run as stdio subprocesses
- Automatic tool discovery and execution
- Claude's native tool calling works through LangChain
- Implements structured output using LangGraph Option 1 approach in this document https://langchain-ai.github.io/langgraph/how-tos/react-agent-structured-output/
"""

import asyncio
import os
import json
from typing import Optional, Dict, Any, Union
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# Load environment variables
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass


# Structured Output Models for LangGraph Option 1
class WeatherCondition(BaseModel):
    """Current weather condition."""
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[int] = Field(None, description="Relative humidity percentage")
    precipitation: Optional[float] = Field(None, description="Current precipitation in mm")
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")
    conditions: Optional[str] = Field(None, description="Weather description")


class DailyForecast(BaseModel):
    """Daily weather forecast."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    temperature_max: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    temperature_min: Optional[float] = Field(None, description="Minimum temperature in Celsius")
    precipitation_sum: Optional[float] = Field(None, description="Total precipitation in mm")
    conditions: Optional[str] = Field(None, description="Weather conditions summary")


class OpenMeteoResponse(BaseModel):
    """Structured response consolidating Open-Meteo data."""
    location: str = Field(..., description="Location name")
    coordinates: Optional[Any] = Field(None, description="Latitude and longitude")
    timezone: Optional[str] = Field(None, description="Timezone")
    current_conditions: Optional[WeatherCondition] = Field(None, description="Current weather")
    daily_forecast: Optional[List[DailyForecast]] = Field(None, description="Daily forecast data")
    summary: str = Field(..., description="Natural language summary")
    data_source: str = Field(default="Open-Meteo API", description="Data source")


class AgricultureAssessment(BaseModel):
    """Agricultural conditions assessment."""
    location: str = Field(..., description="Location name")
    soil_temperature: Optional[float] = Field(None, description="Soil temperature in Celsius")
    soil_moisture: Optional[float] = Field(None, description="Soil moisture content")
    evapotranspiration: Optional[float] = Field(None, description="Daily evapotranspiration in mm")
    planting_conditions: str = Field(..., description="Assessment of planting conditions")
    recommendations: List[str] = Field(default_factory=list, description="Farming recommendations")
    summary: str = Field(..., description="Natural language summary")


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
        
        # Note: Simplified approach - no query classifier needed
        # The LLM will directly determine which tools to use
        
        # Initialize memory checkpointer for conversation state
        self.checkpointer = MemorySaver()
        
        # Initialize conversation ID (thread_id for checkpointer)
        self.conversation_id = str(uuid.uuid4())
        
        # Enhanced system message for the agent that works with pre-classified queries
        self.system_message = SystemMessage(
            content=(
                "You are a helpful weather and agricultural assistant powered by AI.\n\n"
                "IMPORTANT: When users ask about weather, ALWAYS use the available tools to get data. The tools provide:\n"
                "- Weather forecasts (current conditions and predictions up to 16 days)\n"
                "- Historical weather data (past weather patterns and trends)\n"
                "- Agricultural conditions (soil moisture, evapotranspiration, growing degree days)\n\n"
                "For every weather query:\n"
                "1. ALWAYS call the appropriate tool(s) first to get real data\n"
                "2. Use the data from tools to provide accurate, specific answers\n"
                "3. Focus on agricultural applications like planting decisions, irrigation scheduling, frost warnings, and harvest planning\n\n"
                "Tool Usage Guidelines:\n"
                "- For current/future weather → use get_weather_forecast tool\n"
                "- For past weather → use get_historical_weather tool\n"
                "- For soil/agricultural conditions → use get_agricultural_conditions tool\n"
                "- For complex queries → use multiple tools to gather comprehensive data\n\n"
                "Location context may be provided in [brackets] to help with disambiguation.\n"
                "Always prefer calling tools with this context over asking for clarification.\n\n"
                "COORDINATE HANDLING:\n"
                "- When users mention coordinates (lat/lon, latitude/longitude), ALWAYS pass them to tools\n"
                "- For faster responses, provide latitude/longitude coordinates for any location you know\n"
                "- You have extensive geographic knowledge - use it to provide coordinates for cities worldwide\n"
                "- If you're unsure of exact coordinates, let the tools handle geocoding instead"
            )
        )
        
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
        
        # Create React agent with discovered tools and checkpointer
        self.agent = create_react_agent(
            self.llm.bind_tools(self.tools),
            self.tools,
            checkpointer=self.checkpointer
        )
    
    async def query(self, user_query: str, thread_id: str = None) -> str:
        """
        Process a query using the LangGraph agent with conversation memory.
        
        Simplified approach:
        1. Pass query directly to LangGraph agent
        2. Agent uses Claude's native tool calling to select appropriate MCP tools
        3. Maintain conversation history via checkpointer
        4. Return natural language response
        
        Args:
            user_query: The user's question
            thread_id: Optional thread ID for conversation tracking. 
                      If not provided, uses the instance's conversation_id
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # Use provided thread_id or instance conversation_id
        thread_id = thread_id or self.conversation_id
        
        # Configure checkpointer with thread_id
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Create messages for the agent
            messages = {"messages": [HumanMessage(content=user_query)]}
            
            # Check if this is the first message in the thread
            checkpoint = await self.checkpointer.aget(config)
            if checkpoint is None or not checkpoint.get("channel_values", {}).get("messages"):
                # First message in thread - include system message
                messages["messages"].insert(0, self.system_message)
            
            # Run the agent with checkpointer config
            result = await asyncio.wait_for(
                self.agent.ainvoke(messages, config=config),
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
    
    async def query_structured(
        self, 
        user_query: str, 
        response_format: str = "forecast", 
        thread_id: str = None
    ) -> Union[OpenMeteoResponse, AgricultureAssessment]:
        """
        Process a query and return structured output using LangGraph Option 1 approach.
        
        This method demonstrates structured output where:
        1. The agent calls MCP tools to get raw JSON data
        2. The response is parsed and structured into Pydantic models
        3. Returns a structured OpenMeteoResponse consolidating the data
        
        Args:
            user_query: The user's question
            response_format: "forecast" for weather data, "agriculture" for farming assessment
            thread_id: Optional thread ID for conversation tracking
            
        Returns:
            Structured Pydantic model with consolidated Open-Meteo data
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # First get the raw response from the agent
        raw_response = await self.query(user_query, thread_id)
        
        # Create structured output parser based on format
        if response_format == "agriculture":
            parser = PydanticOutputParser(pydantic_object=AgricultureAssessment)
            system_prompt = """
            Based on the weather data provided, create a structured agricultural assessment.
            Extract key information about soil conditions, temperatures, moisture, and provide
            farming recommendations. Focus on planting conditions and agricultural decision-making.
            
            {format_instructions}
            
            Weather data to analyze:
            {weather_data}
            """
        else:
            parser = PydanticOutputParser(pydantic_object=OpenMeteoResponse)
            system_prompt = """
            Based on the weather data provided, create a structured weather forecast response.
            Extract current conditions, daily forecasts, and location information.
            Consolidate all Open-Meteo data into the structured format.
            
            IMPORTANT: If coordinates are not available or are null, omit the coordinates field entirely 
            rather than including null values.
            
            {format_instructions}
            
            Weather data to analyze:
            {weather_data}
            """
        
        # Create prompt template
        prompt = PromptTemplate(
            template=system_prompt,
            input_variables=["weather_data"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create LLM chain for structured parsing
        llm_chain = prompt | self.llm | parser
        
        try:
            # Parse the raw response into structured format
            structured_response = await llm_chain.ainvoke({"weather_data": raw_response})
            
            print(f"\n📊 Generated structured {response_format} response")
            return structured_response
            
        except Exception as e:
            print(f"\n⚠️ Error parsing structured output: {e}")
            # Fallback: return minimal structured response
            if response_format == "agriculture":
                return AgricultureAssessment(
                    location="Unknown",
                    planting_conditions="Unable to assess",
                    summary=raw_response
                )
            else:
                return OpenMeteoResponse(
                    location="Unknown",
                    summary=raw_response
                )
    
    def clear_history(self):
        """
        Clear conversation history by generating a new conversation ID.
        
        This effectively starts a new conversation thread while keeping
        the checkpointer's previous conversations intact.
        """
        # Generate new conversation ID for a fresh thread
        self.conversation_id = str(uuid.uuid4())
        print(f"🆕 Started new conversation: {self.conversation_id}")
    
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