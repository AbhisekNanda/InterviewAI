import google.generativeai as genai
import io
import base64
import os

# Configure the Gemini API key
GOOGLE_API_KEY = "AIzaSyANrzOyBTxj6vCN84l2taAGkeyRSBR-NtQ"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # Default to a high-quality TTS model
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini Pro model
model = genai.GenerativeModel(GEMINI_MODEL)  # Or the appropriate model for audio



async def text_to_speech(text: str) -> bytes:
    """
    Converts a string of text into speech audio bytes using the Gemini TTS API.
    
    Args:
        text: The text to be converted to speech.

    Returns:
        The audio data as a bytes object (in WAV format).
    """
    print(f"Generating audio for text: '{text[:30]}...'")
    try:
        tts_model = genai.GenerativeModel(GEMINI_MODEL)
        audio_data_stream = tts_model.generate_content(text, stream=True)
        
        # We need to accumulate the audio bytes from each chunk in the stream.
        full_audio_bytes = bytearray()
        for chunk in audio_data_stream:
            # Fix: Access the .audio_content attribute which contains the bytes.
            if chunk.audio_content:
                full_audio_bytes.extend(chunk.audio_content)
            
        return bytes(full_audio_bytes)

    except Exception as e:
        print(f"An error occurred during Text-to-Speech generation: {e}")
        return b"" # Return empty bytes on failure


async def speech_to_text(audio_bytes: bytes) -> str:
    """
    Transcribes audio data into text using the Gemini API.

    Args:
        audio_bytes: The audio data as a bytes object.

    Returns:
        The transcribed text as a string.
    """
    print("Transcribing received audio...")
    try:
        # Using a model that supports audio transcription
        stt_model = genai.GenerativeModel(GEMINI_MODEL)

        # The API expects a file-like object, so we wrap the bytes
        audio_file = genai.upload_file(contents=audio_bytes, mime_type="audio/wav")
        
        # Generate the text
        response = stt_model.generate_content(["Transcribe the following audio.", audio_file])
        
        # Clean up the uploaded file
        genai.delete_file(audio_file.name)

        if response.text:
            print(f"Transcription successful: '{response.text}'")
            return response.text
        else:
            print("Transcription failed: No text returned.")
            return ""

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return ""