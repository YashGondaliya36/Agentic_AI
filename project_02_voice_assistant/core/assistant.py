"""
Voice Assistant - Main logic with tool integration
Based on Gemini Live API with LangChain tools
"""

import os
import asyncio
import traceback
import pyaudio
from dotenv import load_dotenv

from google import genai
from config import get_gemini_config, get_model_name
from tools import ToolManager

load_dotenv()

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024


class VoiceAssistant:
    """
    Real-time voice assistant with tool integration
    
    Features:
    - Voice input/output
    - Tool calling (search, calendar, etc.)
    - Async execution
    - Real-time streaming
    """
    
    def __init__(self):
        """Initialize the voice assistant"""
        
        print("\n🎙️  Initializing Voice Assistant...")
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please set it in .env file"
            )
        
        # Initialize Gemini client
        self.client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=api_key
        )
        
        # Get model and config
        self.model = get_model_name()
        self.config = get_gemini_config()
        
        # Initialize tool manager
        self.tool_manager = ToolManager()
        
        # Audio setup
        self.pya = pyaudio.PyAudio()
        self.audio_in_queue = None
        self.audio_out_queue = None
        
        # Session state
        self.session = None
        self.audio_stream = None
        
        print("✅ Voice Assistant initialized!")
        print(f"📱 Model: {self.model}")
        print(f"🎤 Microphone: Ready")
        print(f"🔊 Speaker: Ready")
        print(f"🛠️  Tools: {len(self.tool_manager.tool_map)} available\n")
    
    async def send_text(self):
        """Handle text input from console"""
        while True:
            text = await asyncio.to_thread(
                input,
                "💬 Type message (or 'q' to quit): ",
            )
            if text.lower() == 'q':
                break
            
            await self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            )
    
    async def send_realtime(self):
        """Send real-time audio to Gemini"""
        while True:
            msg = await self.audio_out_queue.get()
            await self.session.send(input=msg)
    
    async def listen_audio(self):
        """Capture audio from microphone"""
        mic_info = self.pya.get_default_input_device_info()
        
        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        
        print("🎤 Listening... Speak into your microphone!")
        
        kwargs = {"exception_on_overflow": False} if __debug__ else {}
        
        while True:
            data = await asyncio.to_thread(
                self.audio_stream.read, 
                CHUNK_SIZE, 
                **kwargs
            )
            await self.audio_out_queue.put({
                "data": data, 
                "mime_type": "audio/pcm"
            })
    
    async def receive_audio(self):
        """
        Receive audio and tool calls from Gemini
        This is where tool integration happens!
        """
        while True:
            turn = self.session.receive()
            
            # Collect transcriptions for this turn
            user_transcript_parts = []
            ai_transcript_parts = []
            
            async for response in turn:
                # Handle audio data
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                
                # Handle text responses (for debugging)
                if text := response.text:
                    print(f"\n💬 AI (text): {text}")
                    continue
                
                # 🎤 TRANSCRIPTION: Collect during turn
                if hasattr(response, 'server_content') and response.server_content:
                    # User's voice input
                    if response.server_content.input_transcription:
                        transcript = response.server_content.input_transcription.text
                        user_transcript_parts.append(transcript)
                    
                    # AI's voice output
                    if response.server_content.output_transcription:
                        transcript = response.server_content.output_transcription.text
                        ai_transcript_parts.append(transcript)
                
                # 🔥 HANDLE TOOL CALLS 🔥
                if tool_call := response.tool_call:
                    print(f"\n🔧 Tool call detected!")
                    
                    # Execute tools via ToolManager
                    function_responses = await self.tool_manager.execute_tool_calls(
                        tool_call
                    )
                    
                    # Send results back to Gemini
                    await self.session.send_tool_response(
                        function_responses=function_responses
                    )
                    
                    print("📤 Tool results sent to Gemini\n")
            
            # 🎤 Print complete transcriptions after turn ends
            if user_transcript_parts:
                full_user_text = " ".join(user_transcript_parts)
                print(f"\n🎤 YOU SAID: {full_user_text}")
            
            if ai_transcript_parts:
                full_ai_text = " ".join(ai_transcript_parts)
                print(f"\n🤖 AI SAYS: {full_ai_text}")
            
            # Clear audio queue on turn complete (for interruptions)
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()
    
    async def play_audio(self):
        """Play audio responses from Gemini"""
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)
    
    async def run(self):
        """Main run loop"""
        try:
            async with (
                self.client.aio.live.connect(
                    model=self.model, 
                    config=self.config
                ) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                
                # Create queues
                self.audio_in_queue = asyncio.Queue()
                self.audio_out_queue = asyncio.Queue(maxsize=5)
                
                print("\n" + "="*60)
                print("🎙️  VOICE ASSISTANT IS READY!")
                print("="*60)
                print("\n💡 Try saying:")
                print("   - 'Search for the latest AI news'")
                print("   - 'What's trending in machine learning?'")
                print("   - 'Find information about Gemini 2.5'")
                print("\n⌨️  Or type 'q' to quit\n")
                
                # Start all tasks
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())
                
                # Wait for user to quit
                await send_text_task
                raise asyncio.CancelledError("User requested exit")
        
        except asyncio.CancelledError:
            print("\n\n👋 Assistant shutting down...")
            if self.audio_stream:
                self.audio_stream.close()
        
        except ExceptionGroup as EG:
            if self.audio_stream:
                self.audio_stream.close()
            print("\n❌ Error occurred:")
            traceback.print_exception(EG)
        
        finally:
            print("✅ Cleanup complete. Goodbye!")
