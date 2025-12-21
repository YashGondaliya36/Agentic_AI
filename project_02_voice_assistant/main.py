"""
Voice Assistant with Multi-Tool Integration
Main entry point
"""

import asyncio
from core import VoiceAssistant


def main():
    """Main entry point"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎙️  VOICE ASSISTANT WITH TOOL INTEGRATION             ║
║                                                              ║
║        Powered by Gemini Live API + LangChain                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create and run assistant
    assistant = VoiceAssistant()
    asyncio.run(assistant.run())


if __name__ == "__main__":
    main()
