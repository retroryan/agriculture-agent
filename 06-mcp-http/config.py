"""
Unified model configuration for 06-mcp-http.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def get_model(temperature=0.7, model_name=None, **kwargs):
    """
    Initialize a chat model using the unified interface.
    
    Args:
        temperature: Model temperature (default 0.7)
        model_name: Optional model override
        **kwargs: Additional model parameters
    
    Returns:
        Initialized chat model
    """
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
    
    return init_chat_model(
        model_name,
        temperature=temperature,
        api_key=api_key,
        **kwargs
    )