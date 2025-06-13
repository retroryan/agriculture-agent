"""Display utilities for formatting weather data output."""


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color


def print_colored(text: str, color: str = Colors.NC) -> None:
    """Print text with specified color."""
    print(f"{color}{text}{Colors.NC}")


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print()
    print_colored(f"{'=' * 60}", Colors.CYAN)
    print_colored(f"{title.center(60)}", Colors.CYAN)
    print_colored(f"{'=' * 60}", Colors.CYAN)
    print()


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print()
    print_colored(f"--- {title} ---", Colors.YELLOW)
    print()


def print_weather_data(data: dict) -> None:
    """Print formatted weather data."""
    if 'dates' in data:
        print(f"  Data points: {len(data['dates'])}")
        if data['dates']:
            print(f"  Date range: {data['dates'][0]} to {data['dates'][-1]}")
    
    if 'statistics' in data:
        stats = data['statistics']
        print_colored("\n  Statistics:", Colors.BLUE)
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"    {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"    {key.replace('_', ' ').title()}: {value}")


def print_insights(insights: list) -> None:
    """Print formatted insights."""
    if not insights:
        return
    
    print_colored("\nInsights and Recommendations:", Colors.GREEN)
    
    for insight in insights:
        insight_type = insight.get('type', 'general')
        message = insight.get('message', '')
        recommendation = insight.get('recommendation', '')
        
        # Color code by type
        if insight_type in ['warning', 'error', 'drought_risk', 'flood_risk']:
            color = Colors.RED
        elif insight_type in ['seasonal', 'monitoring']:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        
        print_colored(f"\n  [{insight_type.upper()}] {message}", color)
        if recommendation:
            print(f"  → {recommendation}")


def print_summary(analysis_results: dict) -> None:
    """Print analysis summary."""
    print_colored("\n\nAnalysis Summary", Colors.CYAN)
    print("=" * 40)
    
    print(f"Analysis Type: {analysis_results.get('analysis_type', 'N/A')}")
    
    if 'location' in analysis_results:
        loc = analysis_results['location']
        if 'name' in loc:
            print(f"Location: {loc['name']} ({loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')})")
        else:
            print(f"Location: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}")
    
    if 'time_range' in analysis_results:
        tr = analysis_results['time_range']
        print(f"Time Range: {tr['start']} to {tr['end']}")
    
    if 'data' in analysis_results:
        print_weather_data(analysis_results['data'])


def format_location_string(location: dict) -> str:
    """Format location dictionary as a readable string."""
    if 'name' in location:
        return location['name']
    elif 'latitude' in location and 'longitude' in location:
        return f"{location['latitude']:.2f}, {location['longitude']:.2f}"
    return "Unknown location"


def print_claude_analysis(analysis: str) -> None:
    """Print Claude's analysis with formatting."""
    print_colored("\n\n🤖 Claude Analysis", Colors.MAGENTA)
    print("=" * 60)
    print()
    
    # Split analysis into paragraphs and format
    paragraphs = analysis.strip().split('\n\n')
    for paragraph in paragraphs:
        # Check if it's a numbered list or bullet points
        if paragraph.strip().startswith(('1.', '2.', '3.', '4.', '5.', '•', '-')):
            # Print list items with proper indentation
            lines = paragraph.strip().split('\n')
            for line in lines:
                if line.strip():
                    print(f"  {line}")
        else:
            # Regular paragraph - wrap text
            import textwrap
            wrapped = textwrap.fill(paragraph, width=80, initial_indent='  ', subsequent_indent='  ')
            print(wrapped)
        print()  # Add space between paragraphs
    
    print_colored("=" * 60, Colors.MAGENTA)


def print_raw_data_summary(results: dict) -> None:
    """Print a summary of raw weather data."""
    print_colored("\n📊 Weather Data Summary", Colors.BLUE)
    print("=" * 60)
    
    if 'error' in results:
        print_colored(f"Error: {results['error']}", Colors.RED)
        return
    
    print(f"Analysis Type: {results.get('analysis_type', 'N/A')}")
    
    if 'location' in results:
        print(f"Location: {format_location_string(results['location'])}")
    
    if 'time_range' in results:
        tr = results['time_range']
        print(f"Period: {tr['start']} to {tr['end']}")
    
    if 'data' in results and 'statistics' in results['data']:
        print("\nKey Statistics:")
        stats = results['data']['statistics']
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  • {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    print()