from functools import cache

import whisper


WHISPER_MODEL = "small"


@cache
def get_model():
    """Load the Whisper model once, on first use."""

    return whisper.load_model(WHISPER_MODEL)


def transcribe_chunk(chunk_path):
    result = get_model().transcribe(str(chunk_path), fp16=False)

    return result["text"].strip()


def transcribe_chunks(chunk_files):
    """Transcribe audio chunks in order and join them into one transcript."""

    transcripts = []

    for index, chunk_file in enumerate(chunk_files, start=1):
        print(f"Transcribing chunk {index}/{len(chunk_files)}: {chunk_file.name}")
        transcripts.append(transcribe_chunk(chunk_file))

    return "\n\n".join(transcripts)
