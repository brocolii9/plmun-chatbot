"""
Pre-generates TTS audio files for all KB answers + referral messages.
Uses gTTS (Google Text-to-Speech) — free, no API key needed.

Run once:  python generate_audio.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gtts import gTTS
from app.database import SessionLocal
from app.models import Intent, KnowledgeBase
from app.config import REGISTRAR_REFERRAL_EN, REGISTRAR_REFERRAL_FIL

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "app", "static", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate(text, filename, lang):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        print(f"  skip (exists): {filename}")
        return
    try:
        # gTTS uses 'en' for English, 'tl' for Tagalog (Filipino)
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(path)
        size = os.path.getsize(path) // 1024
        print(f"  OK: {filename} ({size} KB)")
    except Exception as e:
        print(f"  FAIL: {filename} — {e}")


def main():
    db = SessionLocal()
    try:
        intents = db.query(Intent).all()
        print(f"Found {len(intents)} intents. Generating audio...\n")

        for intent in intents:
            kb = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == intent.kb_entry_id
            ).first()
            if not kb:
                continue

            print(f"[{intent.name}]")
            generate(kb.answer_en,  f"{intent.name}_en.mp3",  lang="en")
            generate(kb.answer_fil, f"{intent.name}_fil.mp3", lang="tl")

        print("\n[Referral messages]")
        generate(REGISTRAR_REFERRAL_EN,  "referral_en.mp3",  lang="en")
        generate(REGISTRAR_REFERRAL_FIL, "referral_fil.mp3", lang="tl")

        print(f"\nDone. Files saved to: {OUTPUT_DIR}")
        files = os.listdir(OUTPUT_DIR)
        print(f"Total files: {len(files)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()