import google.generativeai as genai
import os
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
import base64


try:
    genai.configure(api_key="AIzaSyANrzOyBTxj6vCN84l2taAGkeyRSBR-NtQ")
    print("Gemini API key configured successfully from environment variable.")
except (AttributeError, KeyError):
    print("="*80)
    print("ERROR: GEMINI_API_KEY environment variable not found.")
    print("Please set the environment variable or configure the API key directly in the script.")
    print("="*80)
    exit()

# --- Step 3: Model Definition ---
#
# We are using a specific model variant designed for native Text-to-Speech generation.
TTS_MODEL = "gemini-2.5-flash-preview-tts"
SAMPLE_RATE = 24000  # The native sample rate of the TTS model

def generate_and_play_speech(prompt, voice_name="Kore"):
    """
    Generates speech from text using the Gemini TTS model, saves it to a file,
    and plays it through the default audio device.

    Args:
        prompt (str): The text to convert to speech. You can include style
                      guidance directly in the prompt (e.g., "Say this angrily: ...").
        voice_name (str): The name of the prebuilt voice to use.
                          Other examples: 'Eka', 'Asha', 'Ludo'.
    """
    print("\n" + "-"*50)
    print(f"Generating speech for prompt: '{prompt}'")
    print(f"Using voice: {voice_name}")

    # Instantiate the GenerativeModel with the specific TTS model
    model = genai.GenerativeModel(TTS_MODEL)

    try:
        # The core API call to generate content.
        # We specify the response format and voice options in the 'generation_config'.
        response = model.generate_content(
            contents=[
                {
                    "parts": [{"text": prompt}]
                }
            ],
            generation_config={
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_name
                        }
                    }
                }
            }
        )

        # The API returns the audio data as a base64 encoded string.
        # We need to extract and decode it.
        audio_data_base64 = response.candidates[0].content.parts[0].inline_data.data
        
        # --- DEBUGGING STEP ---
        # Check if we actually received any audio data before trying to process it.
        if not audio_data_base64:
            print("!!! ERROR: The API returned an empty audio response. Skipping this prompt.")
            return

        print(f"-> Received {len(audio_data_base64)} bytes of base64 audio data.")

        return audio_data_base64
    except Exception as e:
        print(f"An error occurred while generating speech: {e}")
        return None



# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- Gemini Text-to-Speech Python Script ---")

    # Example 1: A standard, clear voice prompt.
    text_1 = "Hello! This is a demonstration of the new native text-to-speech capabilities in the Gemini 2.5 Flash model."
    generate_and_play_speech(prompt=text_1, voice_name="Kore", output_filename="demo_standard.wav")

    # Example 2: Using prompt engineering to control the speech style.
    text_2 = "Say this with a lot of excitement and a slightly faster pace: Isn't it amazing what we can create with generative AI?"
    generate_and_play_speech(prompt=text_2, voice_name="Kore", output_filename="demo_excited.wav")

    # Example 3: A more professional and informative tone.
    text_3 = "This technology enables developers to build more immersive and interactive applications by generating dynamic, high-quality audio in real time."
    print(generate_and_play_speech(prompt=text_3, voice_name="Kore", output_filename="demo_professional.wav"))

    print("\nScript finished.")
