#!/usr/bin/env python3
"""
Run all tests in the tests directory
"""
import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file.name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file.name} - PASSED")
            return True
        else:
            print(f"❌ {test_file.name} - FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {test_file.name} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {test_file.name} - ERROR: {e}")
        return False

def main():
    """Run all test files"""
    tests_dir = Path(__file__).parent
    test_files = [
        "test_mcp_simple.py",
        "test_agent_simple.py",
        "test_coordinates.py",
        "test_diverse_cities.py",
        "test_error_handling.py"
    ]
    
    print("Starting test suite...")
    print(f"Make sure MCP servers are running on ports 8000, 8001, 8002")
    print(f"Run: ../start_servers.sh in another terminal\n")
    
    passed = 0
    failed = 0
    
    for test_name in test_files:
        test_file = tests_dir / test_name
        if test_file.exists():
            if run_test(test_file):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  {test_name} - NOT FOUND")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {passed} passed, {failed} failed")
    print('='*60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())