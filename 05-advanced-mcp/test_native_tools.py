#!/usr/bin/env python3
"""Test script for Phase 1: Native Tool Calling with Pydantic"""

import asyncio
import sys
sys.path.append('.')

from weather_agent.models import (
    DynamicToolCall,
    WeatherResponse,
    WeatherDataPoint,
    Location,
    DateRange,
    QueryClassification
)
from weather_agent.tool_registry import ToolRegistry
from weather_agent.claude_service import ClaudeService
from datetime import date, timedelta


async def test_pydantic_models():
    """Test Pydantic models validation."""
    print("🧪 Testing Dynamic Pydantic Models")
    print("=" * 50)
    
    # Test DynamicToolCall
    try:
        tool_call = DynamicToolCall(
            tool_name="get_forecast",
            arguments={
                "location": "Ames, Iowa",
                "date_range": {
                    "start_date": str(date.today()),
                    "end_date": str(date.today() + timedelta(days=7))
                },
                "parameters": ["temperature_2m_max", "precipitation_sum"]
            }
        )
        print("✅ DynamicToolCall validation passed")
        print(f"   Tool: {tool_call.tool_name}")
        print(f"   Arguments: {list(tool_call.arguments.keys())}")
    except Exception as e:
        print(f"❌ DynamicToolCall validation failed: {e}")
    
    # Test WeatherResponse with dynamic data
    try:
        weather_data = {
            "latitude": 42.0308,
            "longitude": -93.6319,
            "timezone": "America/Chicago",
            "daily": {
                "time": ["2024-01-01", "2024-01-02"],
                "temperature_2m_max": [10.5, 12.3],
                "precipitation_sum": [0.0, 2.5],
                "some_new_parameter": [1, 2]  # Dynamic parameter
            }
        }
        response = WeatherResponse(**weather_data)
        print("✅ WeatherResponse accepts dynamic fields")
        print(f"   Location: ({response.latitude}, {response.longitude})")
        print(f"   Daily parameters: {list(response.daily.keys())}")
        
        # Test conversion to structured data
        data_points = response.to_structured_data()
        print(f"   Converted to {len(data_points)} data points")
    except Exception as e:
        print(f"❌ WeatherResponse validation failed: {e}")
    
    print()


async def test_tool_registry():
    """Test tool registry functionality."""
    print("🧪 Testing Tool Registry")
    print("=" * 50)
    
    registry = ToolRegistry()
    
    # Get tool schemas
    schemas = registry.get_tools_schema()
    print(f"✅ Found {len(schemas)} registered tools:")
    for schema in schemas:
        print(f"   • {schema['name']}: {schema['description']}")
    
    # Test tool schema format
    forecast_schema = registry.get_tool_schema("get_forecast")
    print(f"\n📋 Forecast tool schema:")
    print(f"   Properties: {list(forecast_schema['input_schema']['properties'].keys())}")
    print(f"   Required: {forecast_schema['input_schema']['required']}")
    
    print()


async def test_claude_classification():
    """Test Claude query classification."""
    print("🧪 Testing Claude Query Classification")
    print("=" * 50)
    
    service = ClaudeService()
    
    test_queries = [
        "What's the weather in Fresno, California tomorrow?",
        "How much rain did Ames, Iowa get last month?",
        "Is it good weather for planting corn in Grand Island, Nebraska?",
        "Tell me about the weather"  # Ambiguous query
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        try:
            classification = await service.classify_query(query)
            print(f"   Type: {classification.query_type}")
            print(f"   Locations: {classification.locations}")
            print(f"   Time refs: {classification.time_references}")
            print(f"   Parameters: {classification.parameters}")
            if classification.requires_clarification:
                print(f"   ⚠️  Clarification needed: {classification.clarification_message}")
        except Exception as e:
            print(f"   ❌ Classification failed: {e}")
    
    print()


async def test_dynamic_tool_registry():
    """Test dynamic tool registry."""
    print("🧪 Testing Dynamic Tool Registry")
    print("=" * 50)
    
    registry = ToolRegistry()
    
    # Simulate registering a tool with dynamic schema
    registry.register_tool(
        name="get_weather_custom",
        description="Custom weather tool",
        input_schema={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "custom_param": {"type": "array", "items": {"type": "string"}},
                "dynamic_field": {"type": "number"}
            },
            "required": ["location"]
        }
    )
    
    schemas = registry.get_tools_schema()
    print(f"✅ Registered {len(schemas)} tools dynamically")
    
    # Test getting schema
    custom_schema = registry.get_tool_schema("get_weather_custom")
    print(f"✅ Retrieved custom tool schema")
    print(f"   Properties: {list(custom_schema['input_schema']['properties'].keys())}")
    
    print()


async def main():
    """Run all tests."""
    print("🚀 Phase 1: Native Tool Calling with Pydantic - Test Suite")
    print("=" * 70)
    print()
    
    await test_pydantic_models()
    await test_tool_registry()
    await test_claude_classification()
    await test_dynamic_tool_registry()
    
    print("=" * 70)
    print("✅ Phase 1 testing complete!")
    print("\nTo test the full integration, run:")
    print("  python 05-advanced-mcp/main.py --native-tools")
    print("  python 05-advanced-mcp/main.py --demo --native-tools")


if __name__ == "__main__":
    asyncio.run(main())