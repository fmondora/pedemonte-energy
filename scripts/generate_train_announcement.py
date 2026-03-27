#!/usr/bin/env python3.12
"""
Genera annunci stile stazione ferroviaria usando Google Gemini TTS.
Uso: python3.12 scripts/generate_train_announcement.py
"""

import os
import sys
import wave
import subprocess
from pathlib import Path

# Carica API key da .env o variabile d'ambiente
def load_env():
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env()

from google import genai
from google.genai import types


def save_wav(filename: str, pcm_data: bytes, rate: int = 24000):
    """Salva dati PCM come file WAV."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def wav_to_mp3(wav_path: str, mp3_path: str):
    """Converte WAV in MP3 con ffmpeg."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-b:a", "192k", mp3_path],
        capture_output=True, check=True,
    )
    os.remove(wav_path)


def generate_announcement(text: str, voice: str = "Kore", output: str = "announcement.mp3"):
    """Genera un annuncio audio con Gemini TTS."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Errore: GEMINI_API_KEY non trovata in .env o nelle variabili d'ambiente")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print(f"Generazione audio con voce '{voice}'...")
    print(f"Testo: {text}")

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice,
                    )
                )
            ),
        ),
    )

    pcm_data = response.candidates[0].content.parts[0].inline_data.data

    wav_path = output.replace(".mp3", ".wav")
    save_wav(wav_path, pcm_data)
    wav_to_mp3(wav_path, output)

    print(f"Audio salvato: {output}")
    return output


# --- Annunci predefiniti ---

ANNOUNCEMENTS = {
    "battery_full": {
        "text": (
            "Say this as a calm, professional British train station announcement, "
            "with measured pacing and a warm tone. Add a brief pause after 'Attention please': "
            "Attention please. The home battery has reached full charge. "
            "One hundred percent. Thank you."
        ),
        "voice": "Kore",
        "file": "battery_full_announcement.mp3",
    },
    "battery_low": {
        "text": (
            "Say this as a calm but slightly urgent British train station announcement, "
            "with measured pacing: "
            "Attention please. The home battery level is low. "
            "Please reduce energy consumption. Thank you."
        ),
        "voice": "Kore",
        "file": "battery_low_announcement.mp3",
    },
    "grid_export": {
        "text": (
            "Say this cheerfully as a British train station announcement: "
            "Good news. Solar production is exceeding consumption. "
            "Energy is being exported to the grid. Splendid."
        ),
        "voice": "Kore",
        "file": "grid_export_announcement.mp3",
    },
    "surplus_all": {
        "text": (
            "Say this as a calm, professional British train station announcement, "
            "with measured pacing and a warm, cheerful tone: "
            "Good afternoon, ladies and gentlemen. "
            "We are pleased to announce an abundance of solar energy. "
            "Battery fully charged, with hours of sunshine remaining. "
            "This would be an excellent time to fire up the sauna, "
            "plug in your Tesla, "
            "or run your washing machine, dishwasher, or tumble dryer. "
            "Thank you for choosing solar energy."
        ),
        "voice": "Kore",
        "file": "surplus_all.mp3",
    },
    "surplus_appliances": {
        "text": (
            "Say this as a calm, professional British train station announcement, "
            "with measured pacing and a warm, cheerful tone: "
            "Good morning, ladies and gentlemen. "
            "We are pleased to announce an abundance of solar energy. "
            "Battery fully charged, with hours of sunshine remaining. "
            "This would be an excellent time to run your washing machine, "
            "dishwasher, or tumble dryer. "
            "Thank you for choosing solar energy."
        ),
        "voice": "Kore",
        "file": "surplus_appliances.mp3",
    },
    "surplus_sauna": {
        "text": (
            "Say this as a calm, professional British train station announcement, "
            "with measured pacing and a warm, cheerful tone: "
            "Good afternoon, ladies and gentlemen. "
            "We are pleased to announce an abundance of solar energy. "
            "Battery fully charged, with hours of sunshine remaining. "
            "This would be an excellent time to fire up the sauna, "
            "or run your washing machine, dishwasher, or tumble dryer. "
            "Thank you for choosing solar energy."
        ),
        "voice": "Kore",
        "file": "surplus_sauna.mp3",
    },
    "surplus_tesla": {
        "text": (
            "Say this as a calm, professional British train station announcement, "
            "with measured pacing and a warm, cheerful tone: "
            "Good afternoon, ladies and gentlemen. "
            "We are pleased to announce an abundance of solar energy. "
            "Battery fully charged, with hours of sunshine remaining. "
            "This would be an excellent time to plug in your Tesla, "
            "or run your washing machine, dishwasher, or tumble dryer. "
            "Thank you for choosing solar energy."
        ),
        "voice": "Kore",
        "file": "surplus_tesla.mp3",
    },
}


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "audio"
    output_dir.mkdir(exist_ok=True)

    # Genera un annuncio specifico o tutti
    target = sys.argv[1] if len(sys.argv) > 1 else "battery_full"

    if target == "all":
        for name, config in ANNOUNCEMENTS.items():
            output_path = str(output_dir / config["file"])
            generate_announcement(config["text"], config["voice"], output_path)
    elif target in ANNOUNCEMENTS:
        config = ANNOUNCEMENTS[target]
        output_path = str(output_dir / config["file"])
        generate_announcement(config["text"], config["voice"], output_path)
    else:
        # Testo personalizzato
        output_path = str(output_dir / "custom_announcement.mp3")
        generate_announcement(target, output=output_path)
