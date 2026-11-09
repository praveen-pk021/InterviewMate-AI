
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY")

PRISMA_URL = "https://api.vachana.ai/stt/v3"


def transcribe_audio(audio_file, language="en-IN"):

    if not GNANI_API_KEY:
        raise ValueError("Gnani API key not found. Check your .env file.")

    headers = {
        "X-API-Key-ID": GNANI_API_KEY
    }

    files = {
        "audio_file": (
            "interview_answer.wav",
            audio_file.getvalue(),
            "audio/wav"
        )
    }

    data = {
        "language_code": language,
        "preferred_language": language,
        "format": "transcribe",
        "itn_native_numerals": "true"
    }

    response = requests.post(
        PRISMA_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=90
    )

    response.raise_for_status()

    result = response.json()

    print("Gnani Prisma response:", result)

    if not result.get("success"):
        raise RuntimeError(f"Prisma transcription failed: {result}")

    transcript = result.get("transcript", "")

    if not transcript:
        raise ValueError("No transcript returned by Prisma.")

    return transcript
