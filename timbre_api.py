
import os
import requests

from dotenv import load_dotenv

load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY")

TIMBRE_URL = "https://api.vachana.ai/api/v1/tts/inference"


def generate_voice(text, language="en-IN", voice="Nalini"):

    if not GNANI_API_KEY:
        raise ValueError("Gnani API key is missing.")

    if not text or not text.strip():
        raise ValueError("Feedback text is empty.")

    headers = {
        "X-API-Key-ID": GNANI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text.strip(),
        "voice": voice,
        "model": "timbre-v2.5",
        "language": language,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 48000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav"
        }
    }

    try:
        response = requests.post(
            TIMBRE_URL,
            headers=headers,
            json=payload,
            timeout=90
        )

        if not response.ok:
            raise RuntimeError(
                f"Timbre HTTP {response.status_code}: "
                f"{response.text[:1000]}"
            )

        if not response.content:
            raise ValueError("Timbre returned empty audio.")

        content_type = response.headers.get("Content-Type", "")
        print("Timbre response:", content_type)

        if "audio/" not in content_type:
            raise ValueError(
                f"Expected audio response, received: {content_type}"
            )

        return response.content

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Timbre connection failed: {error}"
        ) from error
