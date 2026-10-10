import os
import shutil
import subprocess
from pathlib import Path

import yt_dlp

from backend.utils.config import DOWNLOAD_DIR


CHUNKS_DIR = DOWNLOAD_DIR / "chunks"


def network_options():
    """
    yt-dlp settings for YouTube, which bot-checks anonymous downloads:

    YTDLP_COOKIES_FILE          path to a Netscape-format cookies.txt exported from a browser
    YTDLP_COOKIES_FROM_BROWSER  read cookies from a local browser instead (e.g. brave, chrome)
    YTDLP_PROXY                 proxy URL, e.g. http://user:pass@host:port
    """

    # YouTube needs a JavaScript runtime to solve its player challenges.
    options = {"js_runtimes": {"deno": {}, "node": {}}}

    cookies_file = os.getenv("YTDLP_COOKIES_FILE")
    cookies_browser = os.getenv("YTDLP_COOKIES_FROM_BROWSER")
    proxy = os.getenv("YTDLP_PROXY")

    if cookies_file:
        if Path(cookies_file).is_file():
            # yt-dlp writes cookies back on exit, and secret files are often
            # read-only, so work from a writable copy.
            DOWNLOAD_DIR.mkdir(exist_ok=True)
            writable_copy = DOWNLOAD_DIR / "yt-cookies.txt"
            shutil.copyfile(cookies_file, writable_copy)
            options["cookiefile"] = str(writable_copy)
        else:
            print(f"Warning: YTDLP_COOKIES_FILE not found at {cookies_file}")

    elif cookies_browser:
        options["cookiesfrombrowser"] = (cookies_browser,)

    if proxy:
        options["proxy"] = proxy

    return options


def youtube_setup():
    """Report which YouTube workarounds are configured (no secrets)."""

    cookies_file = os.getenv("YTDLP_COOKIES_FILE")

    return {
        "cookies": bool(
            (cookies_file and Path(cookies_file).is_file())
            or os.getenv("YTDLP_COOKIES_FROM_BROWSER")
        ),
        "proxy": bool(os.getenv("YTDLP_PROXY")),
        "js_runtime": next((name for name in ("deno", "node") if shutil.which(name)), None),
    }


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
        **network_options(),
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


def chunk_audio(input_file, chunk_length=660, overlap=5, output_dir=CHUNKS_DIR):
    """Split audio into overlapping chunks and return their paths in order."""

    # Clear chunks from earlier runs so they don't leak into this transcript.
    output_dir = Path(output_dir)
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True)

    duration = get_duration(input_file)

    chunks = []
    start = 0

    while start < duration:
        output_file = output_dir / f"chunk_{len(chunks) + 1:03d}.wav"

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
