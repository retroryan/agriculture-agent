from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check if API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print(f"Looking for .env file at: {env_path.absolute()}")
    print("Please ensure you have a .env file with ANTHROPIC_API_KEY=your-api-key")
    exit(1)

# Initialize Claude model with LangChain
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    anthropic_api_key=api_key,
    temperature=0
)

# Hardcoded prompt about DAYMET for agricultural analysis
prompt = """How can earthdata DAYMET be used for agricultural analysis?

DAYMET details:
- Purpose: Daily surface weather data for North America
- Resolution: 1km
- Common short_names:
  - Daymet_Daily_V4R1
  - Daymet_Annual_V4R1"""

# Get response using invoke method
messages = [HumanMessage(content=prompt)]
response = llm.invoke(messages)

# Print the response
print(response.content)