# import os
# import struct
# import asyncio
# import tempfile
# from typing import Optional
# from google import genai
# from google.genai import types
# import google.generativeai as genai_legacy
# from dotenv import load_dotenv

# # --- Environment and API Key Setup ---
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# if not GOOGLE_API_KEY:
#     raise ValueError("GOOGLE_API_KEY not found in .env file.")

# genai_legacy.configure(api_key=GOOGLE_API_KEY)
# tts_client = genai.Client(api_key=GOOGLE_API_KEY)

# # --- Function to create a valid WAV file header ---
# def add_wav_header(audio_data: bytes, sample_rate: int = 24000, bits_per_sample: int = 16) -> bytes:
#     """Prepends a standard WAV header to raw PCM audio data."""
#     num_channels = 1
#     data_size = len(audio_data)
#     bytes_per_sample = bits_per_sample // 8
#     block_align = num_channels * bytes_per_sample
#     byte_rate = sample_rate * block_align
#     chunk_size = 36 + data_size

#     header = struct.pack(
#         "<4sI4s4sIHHIIHH4sI",
#         b"RIFF", chunk_size, b"WAVE", b"fmt ",
#         16, 1, num_channels, sample_rate,
#         byte_rate, block_align, bits_per_sample,
#         b"data", data_size,
#     )
#     return header + audio_data

# # --- MODIFIED TTS FUNCTION TO RETURN A COMPLETE WAV FILE ---
# async def text_to_speech(text: str) -> bytes:
#     """
#     Converts text to speech, assembles it into a complete WAV file, and returns it.
#     """
#     print(f"Generating audio for text: '{text[:30]}...'")
#     try:
#         model = "gemini-2.5-flash-preview-tts"
#         stream = await asyncio.to_thread(
#             tts_client.models.generate_content_stream,
#             model=model,
#             contents=[types.Content(role="user", parts=[types.Part.from_text(text=text)])],
#             config=types.GenerateContentConfig(response_modalities=["audio"]),
#         )
        
#         # Collect all audio chunks into a single byte array
#         audio_chunks = bytearray()
#         for chunk in stream:
#             if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
#                 part = chunk.candidates[0].content.parts[0]
#                 if part.inline_data and part.inline_data.data:
#                     audio_chunks.extend(part.inline_data.data)

#         if not audio_chunks:
#             print("[ERROR] No audio data received from TTS API.")
#             return b""
            
#         # Add the WAV header to make it a playable file
#         wav_audio_bytes = add_wav_header(bytes(audio_chunks))
#         print(f"Successfully generated {len(wav_audio_bytes)} bytes of WAV audio.")
#         return wav_audio_bytes

#     except Exception as e:
#         print(f"An error occurred during TTS generation: {e}")
#         return b""

# async def speech_to_text(audio_bytes: bytes) -> str:
#     """Transcribes audio by saving to a temporary file."""
#     print(f"Transcribing received audio of size: {len(audio_bytes)} bytes...")
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio_file:
#         temp_audio_file.write(audio_bytes)
#         temp_file_path = temp_audio_file.name

#     try:
#         stt_model = genai_legacy.GenerativeModel('models/gemini-1.5-flash')
#         audio_file = genai_legacy.upload_file(path=temp_file_path, mime_type="audio/webm")
#         response = stt_model.generate_content(["Transcribe this audio.", audio_file])
#         genai_legacy.delete_file(audio_file.name)
#         return response.text.strip() if response.text else ""
#     except Exception as e:
#         print(f"An error occurred during transcription: {e}")
#         return ""
#     finally:
#         os.unlink(temp_file_path)

# async def initialize_audio_system():
#     print("Audio system initialized.")







# import os
# import struct
# import asyncio
# import tempfile
# from google import genai
# from google.genai import types
# import google.generativeai as genai_legacy
# from dotenv import load_dotenv

# # --- Environment and Setup ---
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# if not GOOGLE_API_KEY:
#     raise ValueError("GOOGLE_API_KEY not found in .env file.")

# genai_legacy.configure(api_key=GOOGLE_API_KEY)
# tts_client = genai.Client(api_key=GOOGLE_API_KEY)

# def add_wav_header(audio_data: bytes, sample_rate: int = 24000, bits_per_sample: int = 16) -> bytes:
#     """Prepends a standard WAV header to raw PCM audio data."""
#     num_channels = 1
#     data_size = len(audio_data)
#     bytes_per_sample = bits_per_sample // 8
#     block_align = num_channels * bytes_per_sample
#     byte_rate = sample_rate * block_align
#     chunk_size = 36 + data_size
#     header = struct.pack(
#         "<4sI4s4sIHHIIHH4sI",
#         b"RIFF", chunk_size, b"WAVE", b"fmt ",
#         16, 1, num_channels, sample_rate,
#         byte_rate, block_align, bits_per_sample,
#         b"data", data_size,
#     )
#     return header + audio_data

# async def text_to_speech(text: str) -> bytes:
#     """
#     Converts text to speech, assembles it into a complete WAV file, and returns it.
#     """
#     print(f"Generating audio for text: '{text[:30]}...'")
#     try:
#         model = "gemini-2.5-flash-preview-tts"
#         stream = await asyncio.to_thread(
#             tts_client.models.generate_content_stream,
#             model=model,
#             contents=[types.Content(role="user", parts=[types.Part.from_text(text=text)])],
#             config=types.GenerateContentConfig(response_modalities=["audio"]),
#         )
        
#         audio_chunks = bytearray()
#         for chunk in stream:
#             if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
#                 part = chunk.candidates[0].content.parts[0]
#                 if part.inline_data and part.inline_data.data:
#                     audio_chunks.extend(part.inline_data.data)

#         if not audio_chunks:
#             print("[ERROR] No audio data received from TTS API.")
#             return b""
            
#         wav_audio_bytes = add_wav_header(bytes(audio_chunks))
#         print(f"Successfully generated {len(wav_audio_bytes)} bytes of WAV audio.")
#         return wav_audio_bytes

#     except Exception as e:
#         print(f"An error occurred during TTS generation: {e}")
#         return b""

# async def speech_to_text(audio_bytes: bytes) -> str:
#     # This function remains unchanged
#     pass

# async def initialize_audio_system():
#     print("Audio system initialized.")








import os
import struct
import asyncio
import tempfile
from typing import Optional

# These are the correct and necessary imports
from google import genai
from google.genai import types
import google.generativeai as genai_legacy
from dotenv import load_dotenv

# --- Environment and Setup ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")

genai_legacy.configure(api_key=GOOGLE_API_KEY)
tts_client = genai.Client(api_key=GOOGLE_API_KEY)


def add_wav_header(audio_data: bytes, sample_rate: int = 24000, bits_per_sample: int = 16) -> bytes:
    """Prepends a standard WAV header to raw PCM audio data."""
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE", b"fmt ",
        16, 1, num_channels, sample_rate,
        byte_rate, block_align, bits_per_sample,
        b"data", data_size,
    )
    return header + audio_data


async def text_to_speech(text: str) -> bytes:
    """Converts text to speech and returns a complete WAV file."""
    print(f"Generating audio for text: '{text[:30]}...'")
    try:
        model = "gemini-2.5-flash-preview-tts"
        stream = await asyncio.to_thread(
            tts_client.models.generate_content_stream,
            model=model,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=text)])],
            config=types.GenerateContentConfig(response_modalities=["audio"]),
        )
        audio_chunks = bytearray()
        for chunk in stream:
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    audio_chunks.extend(part.inline_data.data)
        if not audio_chunks:
            return b""
        return add_wav_header(bytes(audio_chunks))
    except Exception as e:
        print(f"An error occurred during TTS generation: {e}")
        return b""


async def speech_to_text(audio_bytes: bytes) -> str:
    """Transcribes audio by saving to a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_file_path = temp_audio_file.name
    try:
        stt_model = genai_legacy.GenerativeModel('models/gemini-1.5-flash')
        audio_file = genai_legacy.upload_file(path=temp_file_path, mime_type="audio/webm")
        response = stt_model.generate_content(["Transcribe this audio.", audio_file])
        genai_legacy.delete_file(audio_file.name)
        return response.text.strip() if response.text else ""
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return ""
    finally:
        os.unlink(temp_file_path)


async def initialize_audio_system():
    """Initializes the audio system."""
    print("Audio system initialized.")

#
# The line `from core.audio import ...` that was causing the error has been removed from here.
#