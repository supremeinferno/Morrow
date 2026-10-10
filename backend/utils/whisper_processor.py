import os
from functools import cache

import whisper


# "base" needs ~1 GB of RAM, "small" ~2 GB. Override with the WHISPER_MODEL env var.
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")


@cache
def get_model():
    """Load the Whisper model once, on first use."""

    return whisper.load_model(WHISPER_MODEL)


def transcribe_chunk(chunk_path):
    result = get_model().transcribe(str(chunk_path), fp16=False)

    return result["text"].strip()


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
