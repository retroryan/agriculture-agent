#!/usr/bin/env python3
"""
Comprehensive tests for MCP Agent in 05-advanced-mcp.

This consolidated test suite covers:
- Agent initialization and setup
- LangGraph integration with MCP servers
- Memory/checkpointer functionality  
- Query processing and tool selection
- Multi-turn conversations
- Structured output processing (LangGraph Option 1)
- Error handling and edge cases
- Integration with real MCP servers
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add the parent directories to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_agent.mcp_agent import MCPWeatherAgent, OpenMeteoResponse, AgricultureAssessment


# Test utilities
class TestResults:
    """Track test results and provide summary."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_test(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*60)
        print("CONSOLIDATED MCP AGENT TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/(self.passed + self.failed)*100):.1f}%")
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for test in self.tests:
                if not test["passed"]:
                    print(f"  ❌ {test['name']}")
                    if test["details"]:
                        print(f"     {test['details']}")
        
        print(f"\n🎯 {'All tests passed!' if self.failed == 0 else 'Some tests failed - check details above'}")


# Global test results
results = TestResults()


async def test_agent_initialization():
    """Test agent initialization and setup."""
    print("\n🧪 Testing Agent Initialization...")
    print("-" * 50)
    
    try:
        agent = MCPWeatherAgent()
        results.add_test("Agent Creation", True, "MCPWeatherAgent instance created")
        
        # Test initialization
        await agent.initialize()
        results.add_test("Agent Initialize", True, "MCP connections established")
        
        # Check tools are loaded
        if agent.tools and len(agent.tools) > 0:
            results.add_test("Tools Discovery", True, f"Found {len(agent.tools)} tools")
            print(f"✅ Tools discovered: {[tool.name for tool in agent.tools]}")
        else:
            results.add_test("Tools Discovery", False, "No tools found")
        
        # Check agent is created
        if agent.agent:
            results.add_test("LangGraph Agent", True, "React agent created")
        else:
            results.add_test("LangGraph Agent", False, "No agent created")
        
        # Check checkpointer
        if agent.checkpointer:
            results.add_test("Memory Checkpointer", True, "MemorySaver configured")
        else:
            results.add_test("Memory Checkpointer", False, "No checkpointer")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        results.add_test("Agent Initialization", False, str(e))
        print(f"❌ Initialization error: {e}")
        return False


async def test_basic_query():
    """Test basic query functionality."""
    print("\n🧪 Testing Basic Query Processing...")
    print("-" * 50)
    
    try:
        agent = MCPWeatherAgent()
        await agent.initialize()
        
        # Test simple weather query
        query = "What's the weather forecast for Des Moines, Iowa?"
        print(f"Query: {query}")
        
        response = await agent.query(query)
        
        if response and len(response) > 100:
            results.add_test("Basic Weather Query", True, f"Response length: {len(response)} chars")
            print(f"✅ Got response: {response[:100]}...")
        else:
            results.add_test("Basic Weather Query", False, f"Short/empty response: {response[:50] if response else 'None'}")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        results.add_test("Basic Query", False, str(e))
        print(f"❌ Query error: {e}")
        return False


async def test_structured_output():
    """Test structured output functionality (LangGraph Option 1)."""
    print("\n🧪 Testing Structured Output (LangGraph Option 1)...")
    print("-" * 50)
    
    try:
        agent = MCPWeatherAgent()
        await agent.initialize()
        
        # Test structured weather forecast
        print("\n1. Testing structured weather forecast...")
        forecast_query = "What's the weather forecast for Iowa City, Iowa?"
        
        structured_response = await agent.query_structured(
            forecast_query, 
            response_format="forecast"
        )
        
        if isinstance(structured_response, OpenMeteoResponse):
            results.add_test("Structured Forecast Type", True, "Returned OpenMeteoResponse")
            
            # Check required fields
            if structured_response.location:
                results.add_test("Forecast Location Field", True, f"Location: {structured_response.location}")
            else:
                results.add_test("Forecast Location Field", False, "Missing location")
            
            if structured_response.summary:
                results.add_test("Forecast Summary Field", True, f"Summary length: {len(structured_response.summary)}")
            else:
                results.add_test("Forecast Summary Field", False, "Missing summary")
            
            # Check optional structured data
            if structured_response.current_conditions:
                temp = structured_response.current_conditions.temperature
                results.add_test("Current Conditions", True, f"Temperature: {temp}°C")
            else:
                results.add_test("Current Conditions", False, "No current conditions")
            
            if structured_response.daily_forecast:
                days = len(structured_response.daily_forecast)
                results.add_test("Daily Forecast Array", True, f"Forecast for {days} days")
            else:
                results.add_test("Daily Forecast Array", False, "No daily forecast")
            
        else:
            results.add_test("Structured Forecast Type", False, f"Wrong type: {type(structured_response)}")
        
        # Test structured agricultural assessment  
        print("\n2. Testing structured agricultural assessment...")
        ag_query = "Are conditions good for planting corn in Nebraska?"
        
        ag_response = await agent.query_structured(
            ag_query,
            response_format="agriculture"
        )
        
        if isinstance(ag_response, AgricultureAssessment):
            results.add_test("Agricultural Assessment Type", True, "Returned AgricultureAssessment")
            
            if ag_response.location:
                results.add_test("Agriculture Location Field", True, f"Location: {ag_response.location}")
            else:
                results.add_test("Agriculture Location Field", False, "Missing location")
            
            if ag_response.planting_conditions:
                results.add_test("Planting Conditions Field", True, f"Conditions: {ag_response.planting_conditions}")
            else:
                results.add_test("Planting Conditions Field", False, "Missing planting conditions")
            
            if ag_response.recommendations:
                count = len(ag_response.recommendations)
                results.add_test("Recommendations Array", True, f"{count} recommendations")
            else:
                results.add_test("Recommendations Array", False, "No recommendations")
            
        else:
            results.add_test("Agricultural Assessment Type", False, f"Wrong type: {type(ag_response)}")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        results.add_test("Structured Output", False, str(e))
        print(f"❌ Structured output error: {e}")
        return False


async def test_multi_turn_conversation():
    """Test multi-turn conversation with memory."""
    print("\n🧪 Testing Multi-Turn Conversation Memory...")
    print("-" * 50)
    
    try:
        agent = MCPWeatherAgent()
        await agent.initialize()
        
        # Use consistent thread ID for conversation
        thread_id = "test-conversation-123"
        
        # First query
        query1 = "What's the weather forecast for Ames, Iowa?"
        response1 = await agent.query(query1, thread_id=thread_id)
        
        if response1:
            results.add_test("Multi-turn Query 1", True, f"Got first response: {len(response1)} chars")
        else:
            results.add_test("Multi-turn Query 1", False, "No response to first query")
        
        # Follow-up query (should have context)
        query2 = "What about the historical weather there?"
        response2 = await agent.query(query2, thread_id=thread_id)
        
        if response2:
            results.add_test("Multi-turn Query 2", True, f"Got follow-up response: {len(response2)} chars")
            
            # Check if response indicates understanding of "there" (location context)
            if "Ames" in response2 or "Iowa" in response2:
                results.add_test("Context Preservation", True, "Location context preserved")
            else:
                results.add_test("Context Preservation", False, "Location context not preserved")
        else:
            results.add_test("Multi-turn Query 2", False, "No response to follow-up query")
        
        # Test thread isolation with new thread
        new_thread_id = "test-conversation-456"
        query3 = "What about yesterday?"  # Should not have context from previous thread
        response3 = await agent.query(query3, thread_id=new_thread_id)
        
        if response3:
            results.add_test("Thread Isolation", True, "New thread responded")
            # This should ask for clarification since it doesn't have context
            if "clarification" in response3.lower() or "location" in response3.lower() or "where" in response3.lower():
                results.add_test("Thread Context Isolation", True, "New thread has no previous context")
            else:
                results.add_test("Thread Context Isolation", False, "Thread isolation may be broken")
        else:
            results.add_test("Thread Isolation", False, "New thread failed to respond")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        results.add_test("Multi-turn Conversation", False, str(e))
        print(f"❌ Multi-turn conversation error: {e}")
        return False


async def test_error_handling():
    """Test error handling scenarios."""
    print("\n🧪 Testing Error Handling...")
    print("-" * 50)
    
    try:
        agent = MCPWeatherAgent()
        await agent.initialize()
        
        # Test with invalid/unclear query
        print("\n1. Testing unclear query...")
        unclear_query = "Tell me about stuff"
        response = await agent.query(unclear_query)
        
        if response:
            results.add_test("Unclear Query Handling", True, "Handled unclear query gracefully")
        else:
            results.add_test("Unclear Query Handling", False, "Failed to handle unclear query")
        
        # Test with very long query
        print("\n2. Testing long query...")
        long_query = "What's the weather " + "very " * 100 + "detailed forecast for Des Moines?"
        response = await agent.query(long_query)
        
        if response:
            results.add_test("Long Query Handling", True, "Handled long query")
        else:
            results.add_test("Long Query Handling", False, "Failed to handle long query")
        
        # Test structured output with fallback
        print("\n3. Testing structured output fallback...")
        try:
            fallback_response = await agent.query_structured(
                "This is a nonsensical query about nothing specific",
                response_format="forecast"
            )
            
            if isinstance(fallback_response, OpenMeteoResponse):
                results.add_test("Structured Output Fallback", True, "Provided fallback structured response")
            else:
                results.add_test("Structured Output Fallback", False, "No fallback provided")
        except Exception as e:
            results.add_test("Structured Output Fallback", False, f"Exception in fallback: {str(e)}")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        results.add_test("Error Handling", False, str(e))
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_tool_integration():
    """Test integration with MCP tools."""
    print("\n🧪 Testing MCP Tool Integration...")
    print("-" * 50)
    
    try:
        agent = MCPWeatherAgent()
        await agent.initialize()
        
        # Test queries that should trigger different tools
        test_cases = [
            ("Get forecast for Dallas, Texas", "forecast"),
            ("Show historical weather for Seattle last month", "historical"),
            ("Are soil conditions good for planting in Iowa?", "agricultural")
        ]
        
        for query, expected_tool_type in test_cases:
            print(f"\nTesting: {query}")
            response = await agent.query(query)
            
            if response and len(response) > 50:
                results.add_test(f"Tool Integration ({expected_tool_type})", True, f"Got response: {len(response)} chars")
                print(f"✅ {expected_tool_type} tool integration working")
            else:
                results.add_test(f"Tool Integration ({expected_tool_type})", False, "No meaningful response")
                print(f"❌ {expected_tool_type} tool integration failed")
        
        await agent.cleanup()
        return True
        
    except Exception as e:
        results.add_test("Tool Integration", False, str(e))
        print(f"❌ Tool integration error: {e}")
        return False


async def main():
    """Run all consolidated agent tests."""
    print("🚀 Comprehensive MCP Agent Test Suite")
    print("=" * 60)
    print("Testing agent functionality, memory, structured output, and integration")
    
    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️ Warning: ANTHROPIC_API_KEY not set. Some tests may fail.")
    
    # Run all test categories
    print("\n📋 Running Basic Tests...")
    await test_agent_initialization()
    await test_basic_query()
    
    print("\n📋 Running Advanced Features...")
    await test_structured_output()
    await test_multi_turn_conversation()
    
    print("\n📋 Running Integration Tests...")
    await test_tool_integration()
    await test_error_handling()
    
    # Print consolidated results
    results.print_summary()
    
    return results.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)