#!/usr/bin/env python3
"""
Main entry point for the weather/agricultural intelligence application.
- Accepts user input or runs demo queries.
- Classifies the query using Claude.
- Calls the appropriate API helper based on classification.
- Analyzes results with Claude.
- Prints output.
"""
import sys
sys.path.append('02-domain-applications')
import argparse
from utils.claude_integration import ClaudeIntegration
from utils.display import print_colored, print_section_header
from api_utils.api_client import OpenMeteoClient
from api_utils.temperature_api import TemperatureAnalyzer
from api_utils.precipitation_api import PrecipitationAnalyzer
from api_utils.soil_moisture_api import SoilMoistureAnalyzer

# Demo queries for demo mode
demo_queries = [
    "How much rain did we get in Austin last week?",
    "What was the average temperature in Iowa City in May?",
    "Tell me about soil moisture in Des Moines for the past 10 days."
]

def get_api_helper(classification):
    if classification == "temperature":
        return TemperatureAnalyzer(OpenMeteoClient())
    elif classification == "precipitation":
        return PrecipitationAnalyzer(OpenMeteoClient())
    elif classification == "soil_moisture":
        return SoilMoistureAnalyzer(OpenMeteoClient())
    else:
        return None

def run_query(query):
    print_section_header(f"User Query: {query}")
    claude = ClaudeIntegration()
    intent = claude.classify_query(query, location=None)
    # Pick the main classification from data_needs if present
    data_needs = intent.get("data_needs", [])
    main_type = data_needs[0] if data_needs else None
    api_helper = get_api_helper(main_type)
    if not api_helper:
        print_colored(f"No API helper found for classification: {main_type}", "red")
        return
    location = intent.get("location")
    if not location:
        print_colored("No location provided in query. Using default location: Austin, TX.", "yellow")
        location = {"latitude": 30.2672, "longitude": -97.7431}
    time_range = intent.get("time_range")
    if not time_range:
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=30)
        time_range = (start, end)
    results = api_helper.analyze(location, time_range)
    summary = claude.analyze_data(main_type, results)
    print_colored("\nClaude's Analysis:", "cyan")
    print(summary)

def main():
    parser = argparse.ArgumentParser(description="Weather/Agricultural Intelligence App")
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with sample queries')
    parser.add_argument('--query', type=str, help='Run a single query and exit')
    args = parser.parse_args()
    
    if args.query:
        run_query(args.query)
    elif args.demo:
        for q in demo_queries:
            run_query(q)
            print("\n" + "-"*40 + "\n")
    else:
        print("Enter your query (or 'exit' to quit):")
        while True:
            query = input('> ').strip()
            if query.lower() in ('exit', 'quit'):
                break
            if query:
                run_query(query)
                print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    main()
