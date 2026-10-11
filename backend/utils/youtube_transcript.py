"""
YouTube transcripts via the Supadata API.

YouTube blocks audio downloads from cloud servers, so on hosted deployments
YouTube links use the video's captions instead. Requires SUPADATA_API_KEY.
"""

import os
import time
from urllib.parse import urlparse

import httpx


SUPADATA_URL = "https://api.supadata.ai/v1/transcript"
OEMBED_URL = "https://www.youtube.com/oembed"

YOUTUBE_HOSTS = {"youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}

# "native" uses captions already on YouTube (including auto-generated ones) and
# costs 1 credit per video. "auto" falls back to AI transcription, which costs
# 2 credits per minute of video.
SUPADATA_MODE = os.getenv("SUPADATA_MODE", "native")

POLL_INTERVAL_SECONDS = 2
POLL_TIMEOUT_SECONDS = 15 * 60


class TranscriptError(Exception):
    """A transcript couldn't be fetched, with a message safe to show users."""


def captions_enabled():
    return bool(os.getenv("SUPADATA_API_KEY"))


def is_youtube_url(url):
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host in YOUTUBE_HOSTS


def fetch_video_title(url):
    """Best-effort video title from YouTube's public oEmbed endpoint."""

    try:
        response = httpx.get(OEMBED_URL, params={"url": url, "format": "json"}, timeout=10)
        response.raise_for_status()
        return response.json().get("title")
    except (httpx.HTTPError, ValueError):
        return None


def _content_to_text(content):
    """Supadata returns plain text, or a list of timed segments."""

    if isinstance(content, str):
        return content.strip()

    return " ".join(segment.get("text", "").strip() for segment in content or []).strip()


def _raise_for_status(response):
    if response.status_code == 206:
        raise TranscriptError(
            "This video has no captions, so Morrow can't read it from the link. "
            "Download it and use \"Upload a file\" instead."
        )

    if response.status_code in (401, 403):
        raise TranscriptError("The Supadata API key is missing or invalid.")

    if response.status_code == 429:
        raise TranscriptError("The YouTube captions service limit was reached. Try again later.")

    response.raise_for_status()


def _wait_for_job(client, job_id):
    """Long videos are processed as background jobs; poll until done."""

    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_SECONDS)

        response = client.get(f"{SUPADATA_URL}/{job_id}")
        _raise_for_status(response)
        job = response.json()
        status = job.get("status")

        if status == "completed" and job.get("content"):
            return job

        if status in ("completed", "failed"):
            raise TranscriptError("The captions service couldn't get a transcript for this video.")

    raise TranscriptError("Fetching the YouTube captions timed out. Try again later.")


def fetch_youtube_transcript(url, client=None):
    """Return the transcript text for a YouTube video."""

    api_key = os.getenv("SUPADATA_API_KEY")

    if not api_key:
        raise TranscriptError("SUPADATA_API_KEY is not set.")

    client = client or httpx.Client(timeout=120)
    client.headers["x-api-key"] = api_key

    with client:
        response = client.get(SUPADATA_URL, params={"url": url, "text": "true", "mode": SUPADATA_MODE})
        _raise_for_status(response)
        data = response.json()

        if response.status_code == 202:
            data = _wait_for_job(client, data["jobId"])

    transcript = _content_to_text(data.get("content"))

    if not transcript:
        raise TranscriptError("This video's captions are empty.")

    return transcript
