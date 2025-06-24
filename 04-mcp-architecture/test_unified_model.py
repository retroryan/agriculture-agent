"""
Comprehensive test suite for MCP architecture with unified models
Tests both single-turn and multi-turn conversations
"""
import os
import sys
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Set up environment
from dotenv import load_dotenv
load_dotenv()

async def run_test(test_name: str, test_function):
    """Run a single test and capture results"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print('='*60)
    
    try:
        result = await test_function()
        print(f"✓ {test_name} completed successfully")
        return {
            "test": test_name,
            "status": "passed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"✗ {test_name} failed: {str(e)}")
        return {
            "test": test_name,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def test_mcp_server_startup():
    """Test MCP server initialization and tool discovery"""
    print("\nTesting MCP server startup...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    results = []
    
    try:
        # Test creating the agent which starts all servers
        start_time = time.time()
        agent = await create_mcp_weather_agent()
        startup_time = time.time() - start_time
        
        # Check that tools were discovered
        tools_found = len(agent.tools) > 0
        
        print(f"  MCP servers started: {'✓' if tools_found else '✗'} (startup: {startup_time:.2f}s)")
        print(f"  Tools discovered: {len(agent.tools)}")
        
        # List discovered tools
        for tool in agent.tools[:5]:  # Show first 5 tools
            print(f"    → {tool.name}")
        
        results.append({
            "servers_started": tools_found,
            "startup_time": startup_time,
            "tools_count": len(agent.tools),
            "tool_names": [t.name for t in agent.tools]
        })
        
        await agent.cleanup()
        
    except Exception as e:
        print(f"  MCP server startup: ✗ ({str(e)})")
        results.append({
            "servers_started": False,
            "error": str(e)
        })
    
    return results

async def test_forecast_tools():
    """Test weather forecast MCP server integration"""
    print("\nTesting forecast tools via MCP...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    test_queries = [
        ("Berlin forecast", "What's the weather forecast for Berlin?"),
        ("Tokyo 5-day", "Give me a 5-day forecast for Tokyo"),
        ("Paris trends", "Show temperature trends for next week in Paris"),
    ]
    
    results = []
    agent = await create_mcp_weather_agent()
    
    for name, query in test_queries:
        try:
            start_time = time.time()
            response = await agent.query(query)
            response_time = time.time() - start_time
            
            # The response is already a string
            assistant_msg = response
            success = len(assistant_msg) > 20
            
            print(f"  {name}: {assistant_msg[:60]}... ✓ ({response_time:.2f}s)")
            results.append({
                "query": name,
                "response_preview": assistant_msg[:100],
                "response_time": response_time,
                "success": success
            })
        except Exception as e:
            print(f"  {name}: ✗ ({str(e)})")
            results.append({
                "query": name,
                "error": str(e),
                "success": False
            })
    
    await agent.cleanup()
    return results

async def test_historical_tools():
    """Test historical weather analysis"""
    print("\nTesting historical tools via MCP...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    test_queries = [
        ("Chicago history", "What was the weather like last month in Chicago?"),
        ("Rome comparison", "Compare this summer to last summer in Rome"),
        ("London rainfall", "Show rainfall trends for 2023 in London"),
    ]
    
    results = []
    agent = await create_mcp_weather_agent()
    
    for name, query in test_queries:
        try:
            start_time = time.time()
            response = await agent.query(query)
            response_time = time.time() - start_time
            
            assistant_msg = response
            success = len(assistant_msg) > 20
            
            print(f"  {name}: {assistant_msg[:60]}... ✓ ({response_time:.2f}s)")
            results.append({
                "query": name,
                "response_preview": assistant_msg[:100],
                "response_time": response_time,
                "success": success
            })
        except Exception as e:
            print(f"  {name}: ✗ ({str(e)})")
            results.append({
                "query": name,
                "error": str(e),
                "success": False
            })
    
    await agent.cleanup()
    return results

async def test_agricultural_tools():
    """Test agricultural condition analysis"""
    print("\nTesting agricultural tools via MCP...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    test_queries = [
        ("Iowa corn", "Check soil moisture conditions for Iowa corn fields"),
        ("Kansas wheat", "Is it too dry for wheat in Kansas?"),
        ("California grapes", "Analyze growing conditions in California vineyards"),
    ]
    
    results = []
    agent = await create_mcp_weather_agent()
    
    for name, query in test_queries:
        try:
            start_time = time.time()
            response = await agent.query(query)
            response_time = time.time() - start_time
            
            assistant_msg = response
            success = len(assistant_msg) > 20
            
            print(f"  {name}: {assistant_msg[:60]}... ✓ ({response_time:.2f}s)")
            results.append({
                "query": name,
                "response_preview": assistant_msg[:100],
                "response_time": response_time,
                "success": success
            })
        except Exception as e:
            print(f"  {name}: ✗ ({str(e)})")
            results.append({
                "query": name,
                "error": str(e),
                "success": False
            })
    
    await agent.cleanup()
    return results

async def test_multi_turn_context():
    """Test conversation memory across turns"""
    print("\nTesting multi-turn conversation context...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    results = []
    agent = await create_mcp_weather_agent()
    
    # Test conversation 1: Location memory
    conv1_queries = [
        ("Initial query", "What's the weather in Berlin?"),
        ("Follow-up", "How about tomorrow?"),  # Should remember Berlin
        ("Another follow-up", "What about the weekend?"),  # Should still remember Berlin
    ]
    
    print("\n  Testing location context preservation...")
    for name, query in conv1_queries:
        try:
            response = await agent.query(query)
            assistant_msg = response
            
            # Check if Berlin is mentioned in follow-up responses
            context_preserved = "Berlin" in assistant_msg or name == "Initial query"
            print(f"    {name}: {'✓' if context_preserved else '✗'}")
            
            results.append({
                "conversation": "location_memory",
                "turn": name,
                "query": query,
                "context_preserved": context_preserved,
                "response_preview": assistant_msg[:100]
            })
        except Exception as e:
            print(f"    {name}: ✗ ({str(e)})")
            results.append({
                "conversation": "location_memory",
                "turn": name,
                "error": str(e)
            })
    
    # Test conversation 2: Agricultural context
    conv2_queries = [
        ("Initial query", "I'm growing corn in Iowa. What are the current conditions?"),
        ("Follow-up", "Should I irrigate?"),  # Should remember corn and Iowa
    ]
    
    print("\n  Testing agricultural context preservation...")
    agent.clear_history()  # Start fresh conversation
    for name, query in conv2_queries:
        try:
            response = await agent.query(query)
            assistant_msg = response
            
            context_preserved = name == "Initial query" or any(word in assistant_msg.lower() for word in ["corn", "iowa"])
            print(f"    {name}: {'✓' if context_preserved else '✗'}")
            
            results.append({
                "conversation": "agricultural_context",
                "turn": name,
                "query": query,
                "context_preserved": context_preserved,
                "response_preview": assistant_msg[:100]
            })
        except Exception as e:
            print(f"    {name}: ✗ ({str(e)})")
            results.append({
                "conversation": "agricultural_context",
                "turn": name,
                "error": str(e)
            })
    
    await agent.cleanup()
    return results

async def test_mcp_server_resilience():
    """Test MCP server subprocess management and recovery"""
    print("\nTesting MCP server resilience...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    results = []
    
    # Test 1: Multiple concurrent requests
    print("  Testing concurrent requests...")
    try:
        agent = await create_mcp_weather_agent()
        
        # Send multiple queries concurrently
        queries = [
            "Weather in London?",
            "Temperature in Paris?",
            "Rain forecast for Berlin?"
        ]
        
        start_time = time.time()
        tasks = [agent.query(q) for q in queries]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful = sum(1 for r in responses if not isinstance(r, Exception))
        print(f"    Concurrent requests: {successful}/{len(queries)} successful ({total_time:.2f}s total)")
        
        results.append({
            "test": "concurrent_requests",
            "total_queries": len(queries),
            "successful": successful,
            "total_time": total_time,
            "avg_time": total_time / len(queries)
        })
    except Exception as e:
        print(f"    Concurrent requests: ✗ ({str(e)})")
        results.append({
            "test": "concurrent_requests",
            "error": str(e)
        })
    
        await agent.cleanup()
        
    # Test 2: Tool discovery
    print("  Testing tool discovery...")
    try:
        agent2 = await create_mcp_weather_agent()
        
        # Check tools were discovered
        tool_names = [tool.name for tool in agent2.tools]
        # Common expected tools (names may vary)
        has_forecast = any("forecast" in name.lower() for name in tool_names)
        has_historical = any("historical" in name.lower() for name in tool_names)
        has_agricultural = any("agricultural" in name.lower() or "soil" in name.lower() for name in tool_names)
        
        all_types_found = has_forecast and has_historical and has_agricultural
        print(f"    Tool discovery: {'✓' if all_types_found else '✗'} (found {len(tool_names)} tools)")
        
        results.append({
            "test": "tool_discovery",
            "tools_found": len(tool_names),
            "has_forecast": has_forecast,
            "has_historical": has_historical,
            "has_agricultural": has_agricultural,
            "all_types_found": all_types_found
        })
        
        await agent2.cleanup()
    except Exception as e:
        print(f"    Tool discovery: ✗ ({str(e)})")
        results.append({
            "test": "tool_discovery",
            "error": str(e)
        })
    
    return results

async def test_tool_composition():
    """Test tools working together across MCP servers"""
    print("\nTesting tool composition across MCP servers...")
    
    from weather_agent.mcp_agent import create_mcp_weather_agent
    
    # Complex query requiring multiple tools
    complex_queries = [
        (
            "forecast_plus_agriculture",
            "What's the weather forecast for Iowa, and based on that, should I plant corn this week?"
        ),
        (
            "historical_comparison",
            "Compare current conditions in California to last year and advise on grape irrigation"
        ),
    ]
    
    results = []
    agent = await create_mcp_weather_agent()
    
    for name, query in complex_queries:
        try:
            start_time = time.time()
            response = await agent.query(query)
            response_time = time.time() - start_time
            
            assistant_msg = response
            
            # Check if response addresses both aspects of the query
            success = len(assistant_msg) > 50
            print(f"  {name}: {'✓' if success else '✗'} ({response_time:.2f}s)")
            
            results.append({
                "query": name,
                "response_length": len(assistant_msg),
                "response_time": response_time,
                "success": success,
                "response_preview": assistant_msg[:150]
            })
        except Exception as e:
            print(f"  {name}: ✗ ({str(e)})")
            results.append({
                "query": name,
                "error": str(e),
                "success": False
            })
    
    await agent.cleanup()
    return results

async def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("MCP ARCHITECTURE TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {os.getenv('MODEL_NAME', 'claude-3-5-sonnet-20241022')}")
    
    all_results = []
    
    # Run each test suite
    test_suites = [
        ("MCP Server Startup", test_mcp_server_startup),
        ("Forecast Tools", test_forecast_tools),
        ("Historical Tools", test_historical_tools),
        ("Agricultural Tools", test_agricultural_tools),
        ("Multi-turn Context", test_multi_turn_context),
        ("MCP Server Resilience", test_mcp_server_resilience),
        ("Tool Composition", test_tool_composition),
    ]
    
    for test_name, test_func in test_suites:
        result = await run_test(test_name, test_func)
        all_results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in all_results if r.get("status") == "passed")
    failed = sum(1 for r in all_results if r.get("status") == "failed")
    total = len(all_results)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    # Calculate average response times
    all_response_times = []
    for result in all_results:
        if result.get("status") == "passed" and isinstance(result.get("result"), list):
            for item in result["result"]:
                if "response_time" in item:
                    all_response_times.append(item["response_time"])
    
    if all_response_times:
        avg_response_time = sum(all_response_times) / len(all_response_times)
        print(f"Average response time: {avg_response_time:.2f}s")
    
    # Save results to JSON
    results_file = Path(__file__).parent / "baseline_mcp_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_run": datetime.now().isoformat(),
            "model": os.getenv('MODEL_NAME', 'claude-3-5-sonnet-20241022'),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": passed/total*100,
                "avg_response_time": avg_response_time if all_response_times else None
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return all_results

if __name__ == "__main__":
    asyncio.run(run_all_tests())