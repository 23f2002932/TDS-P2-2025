"""
Audio transcription tool for the autonomous quiz-solving agent.
"""
from langchain_core.tools import tool
import requests
import os
import tempfile
from google import genai
from google.genai import types


@tool
def transcribe_audio(url: str) -> str:
    """
    Downloads an audio file from a URL and transcribes it to text using Google Gemini.
    Supports MP3, WAV, and other common audio formats.
    
    Args:
        url: The URL of the audio file to transcribe
        
    Returns:
        The transcribed text from the audio file
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Error: GOOGLE_API_KEY not set"
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        
        # Download the audio file
        print(f"Downloading audio from: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Determine MIME type from URL
        ext = url.split('.')[-1].split('?')[0].lower()
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac',
            'm4a': 'audio/mp4',
        }
        mime_type = mime_types.get(ext, 'audio/mpeg')
        
        print(f"Audio MIME type: {mime_type}")
        
        # Create the audio part
        audio_part = types.Part.from_bytes(
            data=response.content,
            mime_type=mime_type
        )
        
        # Use Gemini to transcribe
        print("Transcribing audio with Gemini...")
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                "Transcribe this audio file exactly. If there's a secret code or specific phrase mentioned, make sure to include it. Return only the transcription.",
                audio_part
            ]
        )
        
        transcription = result.text.strip()
        print(f"Transcription result: {transcription}")
        return transcription
        
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"
