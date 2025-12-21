"""Configuration module for Voice Assistant"""

from .gemini_config import get_gemini_config, get_model_name
from .tools_config import get_tools_config

__all__ = ['get_gemini_config', 'get_model_name', 'get_tools_config']
