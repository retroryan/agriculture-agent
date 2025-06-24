"""
Comprehensive test suite for tools integration
Run before and after migration to ensure functionality is preserved
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def run_test(test_name, test_function):
    """Run a single test and capture results"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print('='*60)
    
    try:
        result = test_function()
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

def test_basic_math_tools():
    """Test mathematical operations"""
    print("\nTesting basic math tools...")
    
    # Import and test the math tools
    from basic_tools.tools import multiply_numbers, add_numbers
    
    test_cases = [
        ("Addition", lambda: add_numbers.invoke({"a": 42, "b": 17}), 59),
        ("Multiplication", lambda: multiply_numbers.invoke({"a": 15.5, "b": 3.2}), 49.6),
    ]
    
    results = []
    for name, func, expected in test_cases:
        result = func()
        passed = result == expected
        print(f"  {name}: {result} {'✓' if passed else '✗ (expected ' + str(expected) + ')'}")
        results.append({
            "operation": name,
            "result": result,
            "expected": expected,
            "passed": passed
        })
    
    return results

def test_weather_tools():
    """Test simulated weather functionality"""
    print("\nTesting weather tools...")
    
    from basic_tools.tools import get_simulated_weather
    
    test_cases = [
        ("Berlin, Germany", lambda: get_simulated_weather.invoke({"location": "Berlin, Germany"})),
        ("Tokyo, Japan", lambda: get_simulated_weather.invoke({"location": "Tokyo, Japan"})),
        ("New York, USA", lambda: get_simulated_weather.invoke({"location": "New York, USA"})),
    ]
    
    results = []
    for location, func in test_cases:
        result = func()
        # Check that we got a weather description
        passed = isinstance(result, str) and "°" in result
        print(f"  {location}: {result[:50]}... {'✓' if passed else '✗'}")
        results.append({
            "location": location,
            "result": result,
            "passed": passed
        })
    
    return results

def test_text_analysis():
    """Test word count and text analysis"""
    print("\nTesting text analysis tools...")
    
    from basic_tools.tools import count_words
    
    test_cases = [
        ("Simple sentence", "The quick brown fox jumps", 5),
        ("Empty string", "", 0),
        ("Single word", "Hello", 1),
        ("Multiple spaces", "Hello    world   test", 3),
    ]
    
    results = []
    for name, text, expected_count in test_cases:
        result = count_words.invoke({"text": text})
        # count_words returns a dict, so check the word_count key
        word_count = result.get("word_count", 0)
        passed = word_count == expected_count
        print(f"  {name}: '{text}' → {word_count} words {'✓' if passed else '✗ (expected ' + str(expected_count) + ')'}")
        results.append({
            "test": name,
            "text": text,
            "result": result,
            "word_count": word_count,
            "expected": expected_count,
            "passed": passed
        })
    
    return results

def test_date_time_tools():
    """Test date/time operations"""
    print("\nTesting date/time tools...")
    
    from basic_tools.tools import get_current_time, calculate_days_between
    
    results = []
    
    # Test current time
    current_time = get_current_time.invoke({})
    time_passed = isinstance(current_time, str) and len(current_time) > 0
    print(f"  Current time: {current_time} {'✓' if time_passed else '✗'}")
    results.append({
        "test": "Current time",
        "result": current_time,
        "passed": time_passed
    })
    
    # Test days between dates
    test_cases = [
        ("Year 2024", "2024-01-01", "2024-12-31", 365),
        ("Same day", "2024-01-01", "2024-01-01", 0),
        ("One week", "2024-01-01", "2024-01-08", 7),
    ]
    
    for name, start, end, expected in test_cases:
        result = calculate_days_between.invoke({"start_date": start, "end_date": end})
        passed = result == expected
        print(f"  {name}: {start} to {end} → {result} days {'✓' if passed else '✗ (expected ' + str(expected) + ')'}")
        results.append({
            "test": f"Days between - {name}",
            "start": start,
            "end": end,
            "result": result,
            "expected": expected,
            "passed": passed
        })
    
    return results

def test_agricultural_advice():
    """Test agricultural advice tool"""
    print("\nTesting agricultural advice tool...")
    
    from basic_tools.tools import agricultural_advice
    
    test_cases = [
        ("Corn watering", {"crop": "corn", "condition": "dry"}),
        ("Wheat in wet conditions", {"crop": "wheat", "condition": "wet"}),
        ("Tomatoes general", {"crop": "tomatoes", "condition": "normal"}),
    ]
    
    results = []
    for name, params in test_cases:
        result = agricultural_advice.invoke(params)
        # Check that we got advice
        passed = isinstance(result, str) and len(result) > 20
        print(f"  {name}: {result[:60]}... {'✓' if passed else '✗'}")
        results.append({
            "test": name,
            "params": params,
            "result": result,
            "passed": passed
        })
    
    return results

def test_web_fetch_tools():
    """Test external web fetching"""
    print("\nTesting web fetch tools...")
    
    # Check if external_tools exists
    external_tools_path = Path(__file__).parent / "external_tools"
    if not external_tools_path.exists():
        print("  External tools directory not found - skipping web fetch tests")
        return [{"test": "Web fetch", "status": "skipped", "reason": "external_tools not found"}]
    
    try:
        from external_tools.fetch_tool import fetch_raw_content
        
        # Test with a simple URL
        test_url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m"
        result = fetch_raw_content.invoke({"url": test_url})
        
        # Check if we got JSON data
        passed = isinstance(result, str) and ("temperature" in result or "current" in result)
        print(f"  Fetch weather API: {'✓' if passed else '✗'}")
        
        return [{
            "test": "Weather API fetch",
            "url": test_url,
            "result_length": len(result),
            "passed": passed
        }]
    except Exception as e:
        print(f"  Web fetch test failed: {str(e)}")
        return [{"test": "Web fetch", "status": "failed", "error": str(e)}]

def test_tool_imports():
    """Test that all tools can be imported"""
    print("\nTesting tool imports...")
    
    results = []
    
    # Test basic tools
    try:
        from basic_tools.tools import ALL_TOOLS
        basic_tools_count = len(ALL_TOOLS)
        print(f"  Basic tools imported: {basic_tools_count} tools ✓")
        results.append({
            "module": "basic_tools",
            "tool_count": basic_tools_count,
            "passed": True
        })
    except Exception as e:
        print(f"  Basic tools import failed: {str(e)} ✗")
        results.append({
            "module": "basic_tools",
            "error": str(e),
            "passed": False
        })
    
    # Test external tools if available
    try:
        from external_tools.fetch_tool import FETCH_TOOLS
        external_tools_count = len(FETCH_TOOLS)
        print(f"  External tools imported: {external_tools_count} tools ✓")
        results.append({
            "module": "external_tools",
            "tool_count": external_tools_count,
            "passed": True
        })
    except Exception as e:
        print(f"  External tools not available: {str(e)}")
        results.append({
            "module": "external_tools",
            "status": "not_available",
            "passed": None
        })
    
    return results

def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("TOOLS INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Run each test suite
    test_suites = [
        ("Tool Imports", test_tool_imports),
        ("Basic Math Tools", test_basic_math_tools),
        ("Weather Tools", test_weather_tools),
        ("Text Analysis", test_text_analysis),
        ("Date/Time Tools", test_date_time_tools),
        ("Agricultural Advice", test_agricultural_advice),
        ("Web Fetch Tools", test_web_fetch_tools),
    ]
    
    for test_name, test_func in test_suites:
        result = run_test(test_name, test_func)
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
    
    # Save results to JSON
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_run": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": passed/total*100
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return all_results

if __name__ == "__main__":
    run_all_tests()