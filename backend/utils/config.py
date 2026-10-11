import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
VECTOR_DB_DIR = BASE_DIR / "chroma_db"

load_dotenv(BASE_DIR / ".env")

GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_TRANSCRIPTION_MODEL = os.getenv("GROQ_TRANSCRIPTION_MODEL", "whisper-large-v3-turbo")


def get_groq_api_key():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in the root .env file.")

    return api_key


def get_llm(**kwargs):
    """Return a Groq chat model configured from the root .env file."""

    return ChatGroq(
        model=GROQ_MODEL,
        api_key=get_groq_api_key(),
        temperature=0,
        max_retries=2,
        **kwargs,
    )
