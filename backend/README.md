# Morrow Backend

The Python side of Morrow: a **FastAPI** server that turns a meeting link or recording into a transcript, a structured analysis and a RAG chatbot.

For the project overview, see the [main README](../README.md).

---

## Table of Contents

- [Setup](#setup)
- [Running the API](#running-the-api)
- [API Reference](#api-reference)
- [Pipeline](#pipeline)
- [Module Overview](#module-overview)
- [Configuration](#configuration)
- [Deployment (Docker / Render)](#deployment-docker--render)
- [Command-Line Usage](#command-line-usage)
- [Storage](#storage)
- [Troubleshooting](#troubleshooting)

---

## Setup

**Requirements:** Python 3.10+, FFmpeg on your `PATH`, and a [Groq API key](https://console.groq.com/keys).

All commands run from the **project root**, not from inside `backend/`.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the API

```bash
python -m uvicorn backend.api:app --reload
```

| URL | Purpose |
| --- | --- |
| `http://localhost:8000/api/...` | REST endpoints |
| `http://localhost:8000/docs` | Interactive Swagger UI |

The frontend dev server proxies `/api` to port `8000`, so no CORS setup is needed during development.

### `GET /api/health`

Returns `{"status": "ok"}`. Use it for uptime monitors or Render's health check path.

---

## API Reference

### `POST /api/meetings`

Starts processing a meeting. Send **either** a link **or** a file as `multipart/form-data`.

| Field | Type | Description |
| --- | --- | --- |
| `url` | string | A video link (YouTube or any site [yt-dlp](https://github.com/yt-dlp/yt-dlp) supports) |
| `file` | file | An audio or video file: `.mp4 .mov .mkv .webm .avi .m4v .mp3 .wav .m4a .aac .ogg .flac .opus .weba` |

```bash
# From a link
curl -F "url=https://www.youtube.com/watch?v=VIDEO_ID" http://localhost:8000/api/meetings

# From a file
curl -F "file=@standup.mp4" http://localhost:8000/api/meetings
```

**`202 Accepted`** returns the meeting object (see below), with `status` set to `queued` or the first pipeline step.
**`400 Bad Request`** means no input, both inputs, an invalid link, or an unsupported file type.

### `GET /api/meetings/{id}`

Returns the current state of a meeting. Poll this until `status` is `ready` or `failed`. The web app polls every 2 seconds.

```json
{
  "id": "4798be430f1142e99c5ce96f5d1faf31",
  "title": "release-sync",
  "source": "upload",
  "status": "ready",
  "detail": "Analysis complete.",
  "transcript": "Okay everyone, let's start the release sync...",
  "result": {
    "summary": "The team confirmed the beta launch for March 3rd...",
    "decisions": ["Launch the beta on March 3rd."],
    "actions": [
      { "task": "Write the onboarding documentation", "owner": "Priya", "deadline": "next Monday" },
      { "task": "Fix the login issue", "owner": "Sam" }
    ],
    "questions": ["Whether to charge for the premium plan."]
  },
  "error": null
}
```

Items in `decisions`, `actions` and `questions` come from the LLM. They may be plain strings or objects such as `{ task, owner, deadline }`, so clients should handle both.

| `status` | Meaning |
| --- | --- |
| `queued` | Waiting for an earlier meeting to finish |
| `downloading` | Fetching audio from the link (links only) |
| `preparing` | Normalizing and chunking the audio |
| `transcribing` | Sending chunks to Whisper on Groq. `detail` shows chunk progress |
| `analyzing` | Extracting summary, decisions, actions and questions |
| `indexing` | Embedding the transcript for the chatbot |
| `ready` | Done: `transcript` and `result` are filled in |
| `failed` | Something went wrong. See `error` |

**`404 Not Found`** means the ID is unknown or the server was restarted.

### `POST /api/meetings/{id}/questions`

Asks the RAG chatbot a question about a `ready` meeting.

```bash
curl -X POST http://localhost:8000/api/meetings/<id>/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is fixing the login bug?"}'
```

```json
{ "answer": "Sam is fixing the login bug." }
```

If the transcript doesn't contain the answer, the reply is `"I couldn't find that information in the meeting."`

**`409 Conflict`** means the meeting is still processing. **`400`** means the question is empty.

---

## Pipeline

```text
link ──► download_audio ─┐
                          ├─► normalize_audio ─► chunk_audio ─► transcribe_chunks
file ─────────────────────┘                                            │
                                                     ┌─────────────────┴─────────────────┐
                                                     ▼                                   ▼
                                              analyze_meeting                   create_vector_store
                                       (per-chunk analysis + merge)          (MiniLM embeddings → Chroma)
                                                                                         │
                                                                                   ask_meeting
```

- **Long transcripts** are split into ~6,000-character chunks. Each chunk is analyzed separately, then a consolidation step merges them and removes duplicates. Single-chunk meetings skip the merge, so no details are lost.
- **Each meeting** gets its own temporary audio-chunk folder and its own Chroma collection, so jobs never mix.
- **Processing** happens in a single background worker, one meeting at a time.
- **Transcription** uses Whisper large-v3 turbo on Groq. Audio chunks are encoded as FLAC so each stays under Groq's 25 MB upload limit.
- **Embeddings** use all-MiniLM-L6-v2 through ONNX Runtime (bundled with Chroma) instead of PyTorch. That keeps peak memory around 400 MB, small enough for Render's free plan.

---

## Module Overview

```text
backend/
├── api.py                   # FastAPI app: routes, job state, background pipeline
└── utils/
    ├── config.py            # Paths, .env loading, shared Groq LLM factory
    ├── audio_processor.py   # yt-dlp download, FFmpeg normalize + chunk
    ├── whisper_processor.py # Chunk transcription via Groq's Whisper API
    ├── youtube_transcript.py# YouTube captions via the Supadata API
    ├── summarizer.py        # Analysis + consolidation prompts (JSON output)
    ├── vector_store.py      # Transcript splitting, embeddings, Chroma
    ├── rag_engine.py        # Retrieval + grounded answer generation
    └── main.py              # Command-line version of the pipeline
```

---

## Configuration

### Environment variables

Set these in `.env` locally or in your host's dashboard (e.g. Render → Environment).

| Variable | Required | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | **Yes** | Groq API key for analysis and chat |
| `GROQ_TRANSCRIPTION_MODEL` | No | Groq speech-to-text model. Default `whisper-large-v3-turbo`; `whisper-large-v3` is slightly more accurate |
| `CORS_ORIGINS` | No | Comma-separated browser origins allowed to call the API directly. Default: `http://localhost:5173,https://trymorrow.vercel.app` |
| `SUPADATA_API_KEY` | No | Enables YouTube links on cloud hosts by reading the video's captions through [Supadata](https://supadata.ai) |
| `SUPADATA_MODE` | No | `native` (default: existing captions, 1 credit/video) or `auto` (falls back to AI transcription, 2 credits/minute) |
| `YTDLP_COOKIES_FILE` | No | Path to a browser-exported `cookies.txt`, used when YouTube blocks the server as a bot |
| `YTDLP_PROXY` | No | Proxy URL for downloads, e.g. `http://user:pass@host:port` |

### Code-level settings

| Setting | Location | Default |
| --- | --- | --- |
| LLM model | `GROQ_MODEL` in `utils/config.py` | `openai/gpt-oss-120b` |
| Audio chunk length / overlap | `chunk_audio()` in `utils/audio_processor.py` | 660 s / 5 s |
| Analysis chunk size | `text_splitter` in `utils/summarizer.py` | 6000 chars / 500 overlap |
| RAG chunk size | `rag_splitter` in `utils/vector_store.py` | 1000 chars / 150 overlap |
| Passages retrieved per question | `k` in `ask_meeting()` | 4 |
| Accepted upload types | `MEDIA_SUFFIXES` in `api.py` | common audio/video formats |

**Tip:** for difficult audio (heavy accents, noise), set `GROQ_TRANSCRIPTION_MODEL=whisper-large-v3`.

---

## Deployment (Docker / Render)

The repo root contains a `Dockerfile` that installs FFmpeg, Deno (for YouTube) and the Python dependencies, and downloads the embedding model at build time. There's no PyTorch or local Whisper, so the image is small and runs in about 400 MB of RAM.

**Run locally with Docker:**

```bash
docker build -t morrow-api .
docker run -p 8000:8000 --env-file .env morrow-api
```

**Deploy on Render:**

1. Create a **Web Service** from the repo with **Language: Docker**. The `Dockerfile` handles the build and start commands.
2. Add the `GROQ_API_KEY` environment variable. The free instance type is enough.
3. Optionally set the **Health Check Path** to `/api/health`.
4. If the frontend calls the API directly (via `VITE_API_URL`), make sure its origin is listed in `CORS_ORIGINS`.

**YouTube on cloud servers.** YouTube blocks audio downloads from data-center IPs ("Sign in to confirm you're not a bot"). The site hides the link tab until one of these is configured (see `links` in `/api/health`):

- **Captions API (recommended):** set `SUPADATA_API_KEY`. YouTube links then use the video's captions instead of downloading audio. This works reliably from servers, but videos without captions can't be read (users are told to upload instead). Other video sites still use the download path.
- **Cookies:** sign in to YouTube with a throwaway account in a private window, export `cookies.txt` (e.g. with the "Get cookies.txt LOCALLY" extension), and add it as a Render **Secret File**. Then set `YTDLP_COOKIES_FILE=/etc/secrets/cookies.txt`. Cookies expire, so refresh them if links start failing again.
- **Proxy:** set `YTDLP_PROXY` to a residential proxy. Data-center proxies are blocked too.

Cookies are fragile: YouTube often rejects them when they're used from a different IP ("The page needs to be reloaded"). Prefer the captions API.

---

## Command-Line Usage

The pipeline also runs without the web app:

```bash
python -m backend.utils.main
```

Paste a YouTube URL when prompted. The report prints to the terminal.

---

## Storage

| Path | Contents |
| --- | --- |
| `downloads/` | Downloaded audio and normalized WAV files |
| `downloads/uploads/` | Uploaded recordings, saved as `<meeting-id>.<ext>` |
| `downloads/chunks/<meeting-id>/` | Temporary audio chunks, deleted after each job |
| `chroma_db/` | Persisted Chroma collections, one per meeting |

All paths are relative to the **project root**, as set in `utils/config.py`. Meeting state (status, transcript, results) lives **in memory** inside the API process and is cleared on restart.

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `GROQ_API_KEY not found` | Add the key to `.env` in the project root, not in `backend/`. |
| `ffmpeg: command not found` | Install FFmpeg and make sure it's on your `PATH`. |
| `ModuleNotFoundError: backend` | Run commands from the project root, using `python -m ...`. |
| `.venv/bin/uvicorn: bad interpreter` | The virtualenv was copied from another location. Use `python -m uvicorn ...` or recreate `.venv`. |
| A link fails with `DownloadError` | The link isn't a supported video, or the video is private or region-locked. Try uploading the file instead. |
| "YouTube blocked this download" | The server's IP is being bot-checked. Set `SUPADATA_API_KEY`; see [YouTube on cloud servers](#deployment-docker--render). |
| "This video has no captions" | The video has no YouTube captions. Upload the file, or set `SUPADATA_MODE=auto`. |
| Browser shows a CORS error | Add the frontend's origin to `CORS_ORIGINS`. |
| Transcription fails with `413` or a file-size error | A chunk exceeded Groq's upload limit. Lower `chunk_length` in `chunk_audio()`. |
| Transcription fails with `429` | Groq rate limit reached. Wait, or upgrade your Groq plan. |
