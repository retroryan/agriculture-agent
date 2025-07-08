#!/usr/bin/env python3
"""
Run all async tests for 07-advanced-http-agent in sequence.
This handles the async nature of the tests and provides a summary.
"""

import asyncio
import sys
import os
import time
from typing import List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from coordinates.test_simple_coordinate import test_simple
from coordinates.test_coordinate_usage import test_coordinate_provision
from coordinates.test_coordinates import test_coordinates
from coordinates.test_coordinate_handling import test_forecast_server
from integration.test_diverse_cities import test_diverse_city_coordinates
from integration.test_structured_output_demo import test_structured_output
from integration.test_extended_queries import main as test_extended_queries
from agent.test_mcp_agent import test_mcp_agent_functionality
from agent.test_minimal_agent import test_minimal_agent
from mcp_servers.test_mcp_servers import test_all_servers
from mcp_servers.test_forecast_only import test_forecast_only
from mcp_servers.test_mcp_client import test_mcp_client_tools
from http_transport.test_forecast_minimal import test_forecast_minimal
from integration.test_docker_agent import test_docker_integration


async def run_test(test_name: str, test_func) -> Tuple[str, bool, float, Optional[str]]:
    """Run a single test and return results."""
    print(f"\n{'='*70}")
    print(f"🧪 Running: {test_name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    error_msg = None
    success = False
    
    try:
        await test_func()
        success = True
        print(f"\n✅ {test_name} completed successfully")
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ {test_name} failed with error: {error_msg}")
    
    elapsed_time = time.time() - start_time
    return test_name, success, elapsed_time, error_msg


async def run_all_tests():
    """Run all tests and provide a summary."""
    print("🚀 Starting 07-advanced-http-agent Test Suite")
    print("=" * 70)
    print("\n⚠️  Note: This will start MCP servers as subprocesses")
    print("⚠️  Some tests may take time due to API calls and LLM interactions\n")
    
    # Define all tests to run - organized by category
    tests = [
        # Coordinate Tests
        ("Simple Coordinate Test", test_simple),
        ("Coordinate Provision Test", test_coordinate_provision),
        ("Coordinate Handling Test", test_forecast_server),
        ("Coordinates General Test", test_coordinates),
        
        # MCP Server Tests
        ("MCP Servers Test", test_all_servers),
        ("Forecast Only Test", test_forecast_only),
        ("MCP Client Tools Test", test_mcp_client_tools),
        
        # HTTP Transport Tests
        ("Forecast Minimal HTTP Test", test_forecast_minimal),
        
        # Agent Tests
        ("MCP Agent Functionality Test", test_mcp_agent_functionality),
        ("Minimal Agent Test", test_minimal_agent),
        
        # Integration Tests
        ("Diverse Cities Test", test_diverse_city_coordinates),
        ("Structured Output Demo", test_structured_output),
        ("Extended Queries Test", test_extended_queries),
        # Skip Docker test by default as it requires Docker
        # ("Docker Integration Test", test_docker_integration),
    ]
    
    results: List[Tuple[str, bool, float, Optional[str]]] = []
    total_start = time.time()
    
    # Run each test
    for test_name, test_func in tests:
        result = await run_test(test_name, test_func)
        results.append(result)
        
        # Brief pause between tests to let servers clean up
        await asyncio.sleep(2)
    
    total_time = time.time() - total_start
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _, _ in results if success)
    failed = len(results) - passed
    
    print(f"\nTotal tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    
    print("\nDetailed Results:")
    print("-" * 70)
    for name, success, elapsed, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {name:<40} | {elapsed:>6.2f}s")
        if error:
            print(f"       Error: {error}")
    
    print("\n" + "="*70)
    
    # Return exit code
    return 0 if failed == 0 else 1


def main():
    """Main entry point."""
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()