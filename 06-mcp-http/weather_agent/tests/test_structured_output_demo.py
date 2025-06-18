#!/usr/bin/env python3
"""
Test script for structured output using LangGraph Option 1 approach.

This demonstrates how the MCP agent can return structured Pydantic models
instead of just text responses, consolidating Open-Meteo data.
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Load environment variables from project root
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(env_path)
    print(f"🔑 Loading environment from: {env_path}")
    print(f"🔑 ANTHROPIC_API_KEY present: {'ANTHROPIC_API_KEY' in os.environ}")
except ImportError:
    print("⚠️ dotenv not available, using system environment")

from weather_agent.mcp_agent import MCPWeatherAgent, OpenMeteoResponse, AgricultureAssessment


async def test_structured_forecast():
    """Test structured weather forecast output."""
    print("🧪 Testing Structured Weather Forecast Output")
    print("=" * 60)
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    try:
        # Test structured forecast
        query = "What's the weather forecast for Des Moines, Iowa?"
        print(f"Query: {query}")
        print("\n📊 Getting structured forecast...")
        
        structured_response = await agent.query_structured(
            query, 
            response_format="forecast"
        )
        
        print(f"\n✅ Structured Response Type: {type(structured_response).__name__}")
        print(f"📍 Location: {structured_response.location}")
        print(f"🌐 Data Source: {structured_response.data_source}")
        
        if structured_response.current_conditions:
            current = structured_response.current_conditions
            print(f"🌡️ Current Temperature: {current.temperature}°C")
            print(f"💧 Current Humidity: {current.humidity}%")
            
        if structured_response.daily_forecast:
            print(f"\n📅 Daily Forecast ({len(structured_response.daily_forecast)} days):")
            for day in structured_response.daily_forecast[:3]:  # Show first 3 days
                print(f"  {day.date}: {day.temperature_min}°C to {day.temperature_max}°C")
                if day.precipitation_sum:
                    print(f"    Rain: {day.precipitation_sum}mm")
        
        print(f"\n📝 Summary: {structured_response.summary[:200]}...")
        
        # Show raw JSON structure
        print(f"\n🔧 Raw JSON Structure:")
        print(json.dumps(structured_response.model_dump(), indent=2, default=str)[:500] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.cleanup()


async def test_structured_agriculture():
    """Test structured agricultural assessment output."""
    print("\n\n🧪 Testing Structured Agricultural Assessment Output")
    print("=" * 60)
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    try:
        # Test agricultural assessment
        query = "Are conditions good for planting corn in Iowa?"
        print(f"Query: {query}")
        print("\n🌾 Getting structured agricultural assessment...")
        
        structured_response = await agent.query_structured(
            query, 
            response_format="agriculture"
        )
        
        print(f"\n✅ Structured Response Type: {type(structured_response).__name__}")
        print(f"📍 Location: {structured_response.location}")
        print(f"🌱 Planting Conditions: {structured_response.planting_conditions}")
        
        if structured_response.soil_temperature:
            print(f"🌡️ Soil Temperature: {structured_response.soil_temperature}°C")
        if structured_response.soil_moisture:
            print(f"💧 Soil Moisture: {structured_response.soil_moisture}")
        if structured_response.evapotranspiration:
            print(f"💨 Evapotranspiration: {structured_response.evapotranspiration}mm/day")
            
        if structured_response.recommendations:
            print(f"\n💡 Recommendations ({len(structured_response.recommendations)}):")
            for i, rec in enumerate(structured_response.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n📝 Summary: {structured_response.summary[:200]}...")
        
        # Show raw JSON structure
        print(f"\n🔧 Raw JSON Structure:")
        print(json.dumps(structured_response.model_dump(), indent=2, default=str)[:500] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.cleanup()


async def test_comparison():
    """Compare regular vs structured output."""
    print("\n\n🧪 Comparing Regular vs Structured Output")
    print("=" * 60)
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    try:
        query = "What's the weather like in Fresno, California?"
        
        # Regular text response
        print("📝 Regular Text Response:")
        text_response = await agent.query(query)
        print(text_response[:300] + "...")
        
        # Structured response
        print("\n📊 Structured Response Summary:")
        structured_response = await agent.query_structured(query, response_format="forecast")
        print(f"Location: {structured_response.location}")
        print(f"Current temp: {structured_response.current_conditions.temperature if structured_response.current_conditions else 'N/A'}°C")
        print(f"Forecast days: {len(structured_response.daily_forecast) if structured_response.daily_forecast else 0}")
        print(f"Summary length: {len(structured_response.summary)} chars")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.cleanup()


async def main():
    """Run all tests."""
    print("🚀 Testing LangGraph Option 1 Structured Output Implementation")
    print("=" * 80)
    
    await test_structured_forecast()
    await test_structured_agriculture()
    await test_comparison()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("\nKey Benefits of LangGraph Option 1 Approach:")
    print("• Raw JSON from MCP servers → Agent processes → Structured output")
    print("• Pydantic models ensure type safety and validation")
    print("• Consolidates Open-Meteo data into consistent format")
    print("• Maintains conversation memory through checkpointer")
    print("• Flexible: Can return either text or structured data")


if __name__ == "__main__":
    asyncio.run(main())