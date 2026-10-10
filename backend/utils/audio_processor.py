import shutil
import subprocess
from pathlib import Path

import yt_dlp

from backend.utils.config import DOWNLOAD_DIR


CHUNKS_DIR = DOWNLOAD_DIR / "chunks"


def download_audio(url):
    """Download a video's audio track as a WAV file."""

    DOWNLOAD_DIR.mkdir(exist_ok=True)

    options = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return Path(filename).with_suffix(".wav")


def normalize_audio(input_file):
    """Convert audio to 16 kHz mono and normalize loudness for Whisper."""

    input_file = Path(input_file)
    output_file = DOWNLOAD_DIR / f"{input_file.stem}_normalized.wav"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(input_file),
            "-ac", "1",
            "-ar", "16000",
            "-sample_fmt", "s16",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            str(output_file),
        ],
        check=True,
        capture_output=True,
    )

    return output_file


def get_duration(input_file):
    """Return the duration of an audio file in seconds."""

    output = subprocess.check_output([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_file),
    ])

    return float(output.decode().strip())


def chunk_audio(input_file, chunk_length=660, overlap=5):
    """Split audio into overlapping chunks and return their paths in order."""

    # Clear chunks from earlier runs so they don't leak into this transcript.
    shutil.rmtree(CHUNKS_DIR, ignore_errors=True)
    CHUNKS_DIR.mkdir(parents=True)

    duration = get_duration(input_file)

    chunks = []
    start = 0

    while start < duration:
        output_file = CHUNKS_DIR / f"chunk_{len(chunks) + 1:03d}.wav"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", str(input_file),
                "-t", str(chunk_length),
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                str(output_file),
            ],
            check=True,
            capture_output=True,
        )

        chunks.append(output_file)
        start += chunk_length - overlap

    return chunks
