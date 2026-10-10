# Morrow

> **Turn conversations into what comes next.**

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![React](https://img.shields.io/badge/frontend-React%2019-61dafb)
![Three.js](https://img.shields.io/badge/3D-Three.js-black)
![Whisper](https://img.shields.io/badge/ASR-Whisper-black)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)

Morrow is an AI meeting assistant. Paste a meeting link or upload a recording, and Morrow returns the **summary**, the **decisions**, the **action items** and the **open questions**. You can then **chat with the meeting**: the assistant answers only from what was actually said.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Using Morrow](#using-morrow)
- [Deployment](#deployment)
- [Limitations](#limitations)
- [Roadmap](#roadmap)

---

## Features

| Feature | Description |
| --- | --- |
| **Link or upload** | Paste a YouTube (or other video site) link, or drag and drop an audio or video file. |
| **Local transcription** | Speech-to-text with OpenAI Whisper, running on your own machine. |
| **Meeting summary** | A concise overview of the key discussion and context. |
| **Decisions** | Only decisions that were actually made. Suggestions stay out. |
| **Action items** | Tasks with owners and deadlines, but only when they were stated. |
| **Open questions** | Unresolved questions that need follow-up. |
| **Meeting chatbot** | A RAG chatbot that answers from the transcript, and says so when the answer isn't there. |
| **Live progress** | Step-by-step status while the meeting is processed. Refreshing the page picks up where it left off. |

Morrow is designed to **stay grounded**. It never invents names, deadlines or decisions that weren't in the conversation.

---

## How It Works

```text
          ┌──────────────────────────────┐
          │   Web app (React + Three.js) │
          │   link / file · report · chat│
          └──────────────┬───────────────┘
                         │  /api
          ┌──────────────▼───────────────┐
          │        FastAPI backend       │
          └──────────────┬───────────────┘
                         │
   Download (yt-dlp) ─► Normalize + chunk (FFmpeg) ─► Transcribe (Whisper)
                                                            │
                                         ┌──────────────────┴──────────────────┐
                                         ▼                                     ▼
                              LLM analysis (Groq)                   Embeddings (MiniLM)
                     summary · decisions · actions · questions      Chroma vector store
                                                                               │
                                                                     RAG chatbot (Groq)
```

1. **Ingest.** The audio is downloaded from the link, or taken from the uploaded file.
2. **Prepare.** FFmpeg converts it to 16 kHz mono, levels the loudness and splits it into overlapping 11-minute chunks.
3. **Transcribe.** Whisper transcribes each chunk locally.
4. **Analyze.** Groq extracts the summary, decisions, action items and open questions. Long meetings are analyzed in parts and then merged.
5. **Index.** The transcript is embedded into a Chroma collection that belongs to that meeting.
6. **Chat.** Each question retrieves the most relevant passages, and the LLM answers using only those passages.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, Vite, Three.js via React Three Fiber |
| API | FastAPI, Uvicorn |
| Audio | yt-dlp, FFmpeg |
| Speech-to-text | OpenAI Whisper (`small`, local) |
| LLM | Groq (`openai/gpt-oss-120b`) via LangChain |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector database | Chroma |

---

## Repository Structure

```text
Morrow/
├── backend/            # FastAPI server and the meeting pipeline → see backend/README.md
│   ├── api.py
│   └── utils/
├── frontend/           # React + Three.js web app → see frontend/README.md
│   └── src/
├── chroma_db/          # Persisted vector store (created at runtime)
├── downloads/          # Audio, uploads and chunks (git-ignored)
├── requirements.txt    # Python dependencies
└── .env                # API keys (git-ignored)
```

| Part | Docs |
| --- | --- |
| Backend: API, pipeline, configuration | [backend/README.md](backend/README.md) |
| Frontend: components, 3D scene, development | [frontend/README.md](frontend/README.md) |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 20.19+ or 22.12+** (required by Vite 8)
- **FFmpeg** on your `PATH` (`brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Ubuntu)
- A free **Groq API key** from [console.groq.com](https://console.groq.com/keys)

### 1. Clone and configure

```bash
git clone https://github.com/supremeinferno/Morrow.git
cd Morrow
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Start the backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m uvicorn backend.api:app --reload
```

The API runs at `http://localhost:8000`, and interactive API docs are at `http://localhost:8000/docs`.

### 3. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The dev server forwards `/api` requests to the backend.

> **First run:** Whisper and the embedding model download on first use (a few hundred MB). Later runs use the cached copies.

---

## Using Morrow

1. **Add a meeting.** Paste a link, or switch to **Upload a file** and drop in a recording (MP4, MOV, MKV, WebM, MP3, WAV, M4A and more).
2. **Watch it process.** The workspace shows each step: downloading, preparing, transcribing, extracting insights and building the chat. The meeting ID is kept in the URL, so you can refresh or come back later.
3. **Read the report.** You get the summary, decisions, action items (with owner and deadline when they were stated) and open questions. Use **Copy** to paste it anywhere, or expand the full transcript.
4. **Ask questions.** Chat with the meeting: *"Who is responsible for what?"*, *"What was decided about pricing?"* If the meeting doesn't cover something, Morrow says so instead of guessing.

Prefer the terminal? The pipeline also runs as a CLI. See [backend/README.md](backend/README.md#command-line-usage).

---

## Deployment

| Part | Platform | How |
| --- | --- | --- |
| Backend | Render (Docker) | Uses the root `Dockerfile`. Set `GROQ_API_KEY`, plus `WHISPER_MODEL=base` on small instances |
| Frontend | Vercel | Root Directory `frontend`. `/api` goes to the backend via `vercel.json`, or directly via `VITE_API_URL` |

Full steps: [backend deployment](backend/README.md#deployment-docker--render) · [frontend production build](frontend/README.md#production-build).

---

## Limitations

- **Meetings are stored in memory.** Restarting the API clears processed meetings, though the vector data stays in `chroma_db/`.
- **One meeting at a time.** Transcription is CPU/GPU heavy, so meetings are queued and processed one after another.
- **No authentication.** Morrow is built for local use. Add auth and rate limiting before exposing it publicly.
- **YouTube on cloud hosts.** YouTube often bot-blocks downloads from servers like Render. Uploading the file always works, and links can be re-enabled with cookies or a proxy ([details](backend/README.md#deployment-docker--render)).
- **Processing time.** It scales with recording length and your hardware. A one-hour meeting can take several minutes to transcribe on a CPU.

---

## Roadmap

- [x] Local transcription with Whisper
- [x] Summary, decisions, action items and open questions
- [x] RAG chatbot over meeting transcripts
- [x] Web app with link and file upload
- [ ] Persistent meeting history (database)
- [ ] Export reports as PDF
- [ ] Speaker identification
- [ ] Authentication for hosted deployments
