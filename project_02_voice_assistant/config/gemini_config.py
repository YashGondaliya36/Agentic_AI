"""Gemini Live API configuration"""

import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()


def get_gemini_config():
    """
    Get Gemini Live API configuration
    
    Returns:
        LiveConnectConfig with all settings
    """
    
    # Import tools config here to avoid circular imports
    from .tools_config import get_tools_config
    
    config = types.LiveConnectConfig(
        # Response modality
        response_modalities=["AUDIO"],
        
        # Media resolution for video/screen
        media_resolution="MEDIA_RESOLUTION_MEDIUM",
        
        # Voice configuration
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=os.getenv("VOICE_NAME", "Zephyr")
                )
            )
        ),
        
        # Context window compression for long conversations
        context_window_compression=types.ContextWindowCompressionConfig(
            trigger_tokens=25600,
            sliding_window=types.SlidingWindow(target_tokens=12800),
        ),
        
        # Add tools configuration
        tools=get_tools_config(),
        
        # 🎤 Enable transcription for both input and output audio
        input_audio_transcription={},   # Transcribe user's voice
        output_audio_transcription={}   # Transcribe AI's voice
    )
    
    return config


def get_model_name():
    """Get Gemini model name from environment"""
    return os.getenv(
        "GEMINI_MODEL", 
        "models/gemini-2.5-flash-native-audio-preview-12-2025"
    )
