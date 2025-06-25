#!/usr/bin/env python3
"""
MCP Weather Demo - stdio Subprocess Architecture with Structured Output

This demonstrates MCP servers running as subprocesses with stdio communication
and LangGraph Option 1 structured output.

Usage:
    python 05-advanced-mcp/main.py                    # Interactive mode
    python 05-advanced-mcp/main.py --demo             # Demo mode
    python 05-advanced-mcp/main.py --structured       # Interactive with structured output
    python 05-advanced-mcp/main.py --demo --structured # Demo with structured output
"""

import sys
import os
import argparse

# Handle different execution contexts
# This allows the script to work whether run as:
# - python -m 05-advanced-mcp
# - python 05-advanced-mcp/main.py
# - cd 05-advanced-mcp && python main.py
if __name__ == "__main__" and __package__ is None:
    # Running as a script, not as a module
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    
    # Add parent to path if running from within directory
    if os.path.basename(os.getcwd()) == '05-advanced-mcp':
        sys.path.insert(0, os.getcwd())
    # Add package directory if running from parent
    elif os.path.exists(os.path.join(os.getcwd(), '05-advanced-mcp')):
        sys.path.insert(0, os.path.join(os.getcwd(), '05-advanced-mcp'))
    else:
        sys.path.insert(0, file_dir)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Weather Demo - stdio Subprocess Architecture with Structured Output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This demo shows how MCP servers work:
- Servers run as stdio subprocesses
- Communication via JSON-RPC over stdin/stdout
- Tools are discovered dynamically
- Automatic subprocess cleanup

With --structured flag:
- Shows tool calls with arguments
- Displays raw JSON responses from MCP servers
- Demonstrates structured output transformation
- Implements LangGraph Option 1 approach
        """
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run demo with example queries'
    )
    
    parser.add_argument(
        '--structured',
        action='store_true',
        help='Enable structured output display showing tool calls and transformations'
    )
    
    parser.add_argument(
        '--multi-turn-demo',
        action='store_true',
        help='Run multi-turn conversation demo'
    )
    
    args = parser.parse_args()
    
    import asyncio
    
    # Handle multi-turn demo
    if args.multi_turn_demo:
        try:
            # Try module-style import first
            from .weather_agent.demo_scenarios import run_mcp_multi_turn_demo
        except (ImportError, ValueError):
            # Fall back to absolute import
            from weather_agent.demo_scenarios import run_mcp_multi_turn_demo
        asyncio.run(run_mcp_multi_turn_demo(structured=args.structured))
    else:
        # Import and run the chatbot
        try:
            # Try module-style import first
            from .weather_agent.chatbot import main as chatbot_main
        except (ImportError, ValueError):
            # Fall back to absolute import
            from weather_agent.chatbot import main as chatbot_main
        
        # Pass flags if provided
        sys.argv = [sys.argv[0]]
        if args.demo:
            sys.argv.append('--demo')
        if args.structured:
            sys.argv.append('--structured')
        
        asyncio.run(chatbot_main())


if __name__ == "__main__":
    main()