"""
MCP Weather Agent using LangGraph with Structured Output

This module demonstrates how to use a hybrid of MCP servers with LangGraph:
- One server (forecast) runs over HTTP using fastmcp
- Other servers (historical, agricultural) run as stdio subprocesses
- Uses create_react_agent for robust tool handling
- Automatic tool discovery for stdio, manual tool creation for HTTP
- Claude's native tool calling works through LangChain
- Implements structured output using LangGraph Option 1 approach
"""

import asyncio
import os
import json
from typing import Optional, Dict, Any, Union, List
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from fastmcp import Client
from langchain_core.tools import tool as create_langchain_tool
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import uuid
from pydantic import BaseModel, Field
from datetime import datetime

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
    coordinates: Optional[Dict[str, float]] = Field(None, description="Latitude and longitude")
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
    A weather agent that uses a hybrid of MCP servers with LangGraph.
    
    This demonstrates a mixed-protocol approach:
    1. The forecast server runs independently over HTTP (FastMCP).
    2. Historical and agricultural servers run as stdio subprocesses.
    3. A specific tool is created for the HTTP server.
    4. Other tools are discovered dynamically from stdio servers.
    5. LangGraph's create_react_agent handles execution for all tools.
    """
    
    def __init__(self, forecast_server_url="http://127.0.0.1:8000/mcp", historical_server_url="http://127.0.0.1:8001/mcp", agricultural_server_url="http://127.0.0.1:8002/mcp"):
        # Create LLM instance
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0
        )
        # Store server URLs for creating clients in each tool call
        self.forecast_server_url = forecast_server_url
        self.historical_server_url = historical_server_url
        self.agricultural_server_url = agricultural_server_url
        self.tools = []
        self.agent = None
        
        # Initialize memory checkpointer for conversation state
        self.checkpointer = MemorySaver()
        
        # Initialize conversation ID (thread_id for checkpointer)
        self.conversation_id = str(uuid.uuid4())
        
        # Enhanced system message for the agent
        self.system_message = SystemMessage(
            content="""You are a helpful weather and agricultural assistant powered by AI.

IMPORTANT: When users ask about weather, ALWAYS use the available tools to get data. The tools provide:
- Weather forecasts (current conditions and predictions up to 16 days) via an HTTP server.
- Historical weather data (past weather patterns and trends) via a stdio server.
- Agricultural conditions (soil moisture, evapotranspiration, growing degree days) via a stdio server.

For every weather query:
1. ALWAYS call the appropriate tool(s) first to get real data.
2. Use the data from tools to provide accurate, specific answers.
3. Focus on agricultural applications like planting decisions, irrigation scheduling, frost warnings, and harvest planning.

Tool Usage Guidelines:
- For current/future weather → use get_weather_forecast tool.
- For past weather → use get_historical_weather tool.
- For soil/agricultural conditions → use get_agricultural_conditions tool.
- For complex queries → use multiple tools to gather comprehensive data.

Location context may be provided in [brackets] to help with disambiguation.
Always prefer calling tools with this context over asking for clarification.

COORDINATE HANDLING:
- When users mention coordinates (lat/lon, latitude/longitude), ALWAYS pass them to tools
- For faster responses, provide latitude/longitude coordinates for any location you know
- You have extensive geographic knowledge - use it to provide coordinates for cities worldwide
- If you're unsure of exact coordinates, let the tools handle geocoding instead"""
        )
        
    async def initialize(self):
        """Initialize MCP HTTP clients and create the LangGraph agent."""
        # Note: FastMCP clients will be created fresh in each tool call
        
        # 1. Create tool for the HTTP-based forecast server
        @create_langchain_tool
        async def get_weather_forecast(location: str, days: int = 7, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
            """Get weather forecast data from the Open-Meteo API via FastMCP HTTP server.
            
            Args:
                location: Location name (e.g., 'Des Moines, Iowa')
                days: Number of forecast days (1-16)
                latitude: Latitude (optional, overrides location if provided)
                longitude: Longitude (optional, overrides location if provided)
            """
            try:
                args = {"location": location, "days": days}
                if latitude is not None and longitude is not None:
                    args["latitude"] = latitude
                    args["longitude"] = longitude
                    
                # Create a new client for this tool call
                client = Client(self.forecast_server_url)
                async with client:
                    response = await client.call_tool(
                        "get_weather_forecast",
                        args
                    )
                    # FastMCP returns a list of TextContent objects
                    if isinstance(response, list) and len(response) > 0:
                        content = response[0]
                        if hasattr(content, 'text'):
                            return json.loads(content.text)
                    return response
            except Exception as e:
                print(f"DEBUG: Forecast tool error: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return {"error": f"Failed to call forecast server: {str(e)}"}

        @create_langchain_tool
        async def get_historical_weather(location: str, start_date: str, end_date: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
            """Get historical weather data from the Open-Meteo API via FastMCP HTTP server.
            
            Args:
                location: Location name (e.g., 'Des Moines, Iowa')
                start_date: Start date in YYYY-MM-DD format
                end_date: End date in YYYY-MM-DD format
                latitude: Latitude (optional, overrides location if provided)
                longitude: Longitude (optional, overrides location if provided)
            """
            try:
                args = {"location": location, "start_date": start_date, "end_date": end_date}
                if latitude is not None and longitude is not None:
                    args["latitude"] = latitude
                    args["longitude"] = longitude
                    
                # Create a new client for this tool call
                client = Client(self.historical_server_url)
                async with client:
                    response = await client.call_tool(
                        "get_historical_weather",
                        args
                    )
                    # FastMCP returns a list of TextContent objects
                    if isinstance(response, list) and len(response) > 0:
                        content = response[0]
                        if hasattr(content, 'text'):
                            return json.loads(content.text)
                    return response
            except Exception as e:
                return {"error": f"Failed to call historical server: {str(e)}"}

        @create_langchain_tool
        async def get_agricultural_conditions(location: str, days: int = 7, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
            """Get agricultural weather conditions from the Open-Meteo API via FastMCP HTTP server.
            
            Args:
                location: Location name (e.g., 'Des Moines, Iowa')
                days: Number of forecast days (1-7)
                latitude: Latitude (optional, overrides location if provided)
                longitude: Longitude (optional, overrides location if provided)
            """
            try:
                args = {"location": location, "days": days}
                if latitude is not None and longitude is not None:
                    args["latitude"] = latitude
                    args["longitude"] = longitude
                    
                # Create a new client for this tool call
                client = Client(self.agricultural_server_url)
                async with client:
                    response = await client.call_tool(
                        "get_agricultural_conditions",
                        args
                    )
                    # FastMCP returns a list of TextContent objects
                    if isinstance(response, list) and len(response) > 0:
                        content = response[0]
                        if hasattr(content, 'text'):
                            return json.loads(content.text)
                    return response
            except Exception as e:
                return {"error": f"Failed to call agricultural server: {str(e)}"}

        self.tools = [get_weather_forecast, get_historical_weather, get_agricultural_conditions]
        print(f"🔧 Configured {len(self.tools)} HTTP tools for FastMCP servers")
        
        # 2. Create React agent with combined tools and checkpointer
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
        """Clean up MCP connections."""
        # No persistent connections to clean up - each tool call manages its own
        print("MCP agent cleanup complete.")


# Convenience function
async def create_mcp_weather_agent(forecast_server_url="http://127.0.0.1:8000", historical_server_url="http://127.0.0.1:8001", agricultural_server_url="http://127.0.0.1:8002"):
    """Create and initialize an MCP weather agent."""
    agent = MCPWeatherAgent(
        forecast_server_url=forecast_server_url,
        historical_server_url=historical_server_url,
        agricultural_server_url=agricultural_server_url
    )
    await agent.initialize()
    return agent