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
import argparse
sys.path.append('05-advanced-mcp')

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
        from weather_agent.demo_scenarios import run_mcp_multi_turn_demo
        asyncio.run(run_mcp_multi_turn_demo())
    else:
        # Import and run the chatbot
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