"""
Morrow HTTP API.

Run from the project root:
    uvicorn backend.api:app --reload
"""

import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.utils.audio_processor import (
    CHUNKS_DIR,
    chunk_audio,
    download_audio,
    normalize_audio,
    youtube_setup,
)
from backend.utils.config import DOWNLOAD_DIR
from backend.utils.rag_engine import ask_meeting
from backend.utils.summarizer import analyze_meeting
from backend.utils.vector_store import create_vector_store
from backend.utils.whisper_processor import transcribe_chunks


UPLOAD_DIR = DOWNLOAD_DIR / "uploads"

MEDIA_SUFFIXES = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus", ".weba",
    ".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v",
}

# Whisper is CPU/GPU heavy, so meetings are processed one at a time.
executor = ThreadPoolExecutor(max_workers=1)

# Browser origins allowed to call the API directly (comma-separated).
# Needed when the frontend sets VITE_API_URL instead of using a same-origin proxy.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://trymorrow.vercel.app")

app = FastAPI(title="Morrow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# MEETING STATE
# --------------------------------------------------

@dataclass
class Meeting:
    id: str
    title: str
    source: str
    status: str = "queued"
    detail: str = "Waiting to start..."
    transcript: str | None = None
    result: dict | None = None
    error: str | None = None
    vector_store: Any = field(default=None, repr=False)

    def update(self, status, detail):
        self.status = status
        self.detail = detail
        print(f"[{self.id[:8]}] {status}: {detail}")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "status": self.status,
            "detail": self.detail,
            "transcript": self.transcript,
            "result": self.result,
            "error": self.error,
        }


# Kept in memory: meetings are lost when the server restarts.
meetings: dict[str, Meeting] = {}


def link_title(url):
    """A readable placeholder title until the real video title is known."""

    host = urlparse(url).netloc.removeprefix("www.")
    return f"Video from {host}" if host else "Video link"


def get_meeting(meeting_id):
    meeting = meetings.get(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    return meeting


# --------------------------------------------------
# PIPELINE
# --------------------------------------------------

BOT_CHECK_ERROR = (
    "YouTube blocked this download because it came from a cloud server. "
    "Download the video yourself and use \"Upload a file\" instead."
)


def describe_error(error):
    """Turn known pipeline failures into messages a user can act on."""

    message = str(error)

    if "confirm you" in message and "not a bot" in message:
        return BOT_CHECK_ERROR

    return f"{type(error).__name__}: {message}"

def process_meeting(meeting, url=None, upload_path=None):
    """Run the full pipeline for one meeting, recording progress as it goes."""

    try:
        if url:
            meeting.update("downloading", "Downloading audio...")
            audio_file = download_audio(url)
            meeting.title = audio_file.stem
        else:
            audio_file = upload_path

        meeting.update("preparing", "Normalizing and chunking audio...")
        normalized_file = normalize_audio(audio_file)
        chunks = chunk_audio(normalized_file, output_dir=CHUNKS_DIR / meeting.id)

        meeting.update("transcribing", f"Transcribing chunk 1 of {len(chunks)}...")
        transcript = transcribe_chunks(
            chunks,
            on_progress=lambda done, total: meeting.update(
                "transcribing",
                f"Transcribed {done} of {total} chunk(s)...",
            ),
        )

        if not transcript.strip():
            raise RuntimeError("No speech was detected in this recording.")

        meeting.transcript = transcript

        meeting.update("analyzing", "Extracting summary, decisions and actions...")
        meeting.result = analyze_meeting(transcript)

        meeting.update("indexing", "Preparing the meeting chat...")
        meeting.vector_store, _ = create_vector_store(transcript)

        meeting.update("ready", "Analysis complete.")

    except Exception as error:
        traceback.print_exc()
        meeting.error = describe_error(error)
        meeting.update("failed", "Something went wrong while processing this meeting.")

    finally:
        shutil.rmtree(CHUNKS_DIR / meeting.id, ignore_errors=True)


# --------------------------------------------------
# ROUTES
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    """Uptime check that also shows whether YouTube downloads are set up."""

    return {"status": "ok", "youtube": youtube_setup()}


@app.post("/api/meetings", status_code=202)
def create_meeting(url: str | None = Form(None), file: UploadFile | None = File(None)):
    """Start processing a meeting from a video link or an uploaded file."""

    url = (url or "").strip()

    if not url and not file:
        raise HTTPException(status_code=400, detail="Provide a video link or upload a file.")

    if url and file:
        raise HTTPException(status_code=400, detail="Provide either a link or a file, not both.")

    meeting_id = uuid4().hex

    if url:
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Please enter a valid http(s) link.")

        meeting = Meeting(id=meeting_id, title=link_title(url), source="link")
        meetings[meeting_id] = meeting
        executor.submit(process_meeting, meeting, url=url)

    else:
        suffix = Path(file.filename or "").suffix.lower()

        if suffix not in MEDIA_SUFFIXES:
            raise HTTPException(status_code=400, detail="Please upload an audio or video file.")

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        upload_path = UPLOAD_DIR / f"{meeting_id}{suffix}"

        with upload_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

        meeting = Meeting(id=meeting_id, title=Path(file.filename).stem, source="upload")
        meetings[meeting_id] = meeting
        executor.submit(process_meeting, meeting, upload_path=upload_path)

    return meeting.to_dict()


@app.get("/api/meetings/{meeting_id}")
def read_meeting(meeting_id: str):
    return get_meeting(meeting_id).to_dict()


@app.post("/api/meetings/{meeting_id}/questions")
def ask_question(meeting_id: str, request: QuestionRequest):
    """Answer a question using only this meeting's transcript."""

    meeting = get_meeting(meeting_id)

    if meeting.status != "ready":
        raise HTTPException(status_code=409, detail="This meeting is still being processed.")

    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    return {"answer": ask_meeting(meeting.vector_store, question)}
