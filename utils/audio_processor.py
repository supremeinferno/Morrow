import yt_dlp
from pathlib import Path
import subprocess
# import whisper
# from pydub import AudioSegment
import yt_dlp
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def download_audio(url):
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
    input_file = Path(input_file)

    output_file = DOWNLOAD_DIR / f"{input_file.stem}_normalized.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", str(input_file),
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        str(output_file)
    ]

    subprocess.run(command, check=True)

    return output_file



def chunk_audio(input_file, chunk_length=600, overlap=5):
    input_file = Path(input_file)

    chunks_dir = DOWNLOAD_DIR / "chunks"
    chunks_dir.mkdir(exist_ok=True)

    # Get duration
    duration_command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_file)
    ]

    duration = float(
        subprocess.check_output(duration_command).decode().strip()
    )

    chunks = []
    start = 0
    chunk_number = 1

    while start < duration:
        output_file = chunks_dir / f"chunk_{chunk_number:03d}.wav"

        command = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", str(input_file),
            "-t", str(chunk_length),
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "pcm_s16le",
            str(output_file)
        ]

        subprocess.run(command, check=True)

        chunks.append(output_file)

        start += chunk_length - overlap
        chunk_number += 1

    return chunks

