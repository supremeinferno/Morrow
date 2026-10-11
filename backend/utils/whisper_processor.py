from functools import cache

from groq import Groq

from backend.utils.config import GROQ_TRANSCRIPTION_MODEL, get_groq_api_key


@cache
def get_client():
    """Create the Groq client once, on first use."""

    return Groq(api_key=get_groq_api_key(), max_retries=3)


def transcribe_chunk(chunk_path):
    """Transcribe one audio file with Whisper hosted on Groq."""

    with open(chunk_path, "rb") as audio:
        result = get_client().audio.transcriptions.create(
            file=(chunk_path.name, audio.read()),
            model=GROQ_TRANSCRIPTION_MODEL,
            response_format="json",
            temperature=0,
        )

    return result.text.strip()


def transcribe_chunks(chunk_files, on_progress=None):
    """
    Transcribe audio chunks in order and join them into one transcript.
    `on_progress(done, total)` is called after each chunk, if given.
    """

    transcripts = []
    total = len(chunk_files)

    for index, chunk_file in enumerate(chunk_files, start=1):
        print(f"Transcribing chunk {index}/{total}: {chunk_file.name}")
        transcripts.append(transcribe_chunk(chunk_file))

        if on_progress:
            on_progress(index, total)

    return "\n\n".join(transcripts)
