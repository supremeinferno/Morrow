import whisper
from pathlib import Path

model = whisper.load_model("small")


def transcribe_chunk(chunk_path):
    result = model.transcribe(
        str(chunk_path),
        fp16=False
    )

    return result["text"].strip()


def transcribe_all_chunks(chunks_dir):
    chunks_dir = Path(chunks_dir)

    chunk_files = sorted(chunks_dir.glob("chunk_*.wav"))

    transcripts = []

    for chunk_file in chunk_files:
        print(f"Transcribing: {chunk_file.name}")

        text = transcribe_chunk(chunk_file)

        transcripts.append(text)

    return "\n\n".join(transcripts)

