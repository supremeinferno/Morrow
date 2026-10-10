# Morrow

> **Turn conversations into what comes next.**

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![Whisper](https://img.shields.io/badge/ASR-Whisper-black)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)

Morrow is an AI meeting assistant that turns long meeting recordings into structured, actionable information.

You don't have to rewatch the whole meeting. Morrow shows what matters: **what was discussed, what was decided, what needs to be done, and what still needs an answer.** You can then ask it questions about the meeting in plain English.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Roadmap](#roadmap)

---

## Features

| Feature | Description |
| --- | --- |
| **Transcription** | Converts meeting audio to text with OpenAI Whisper, running locally on your machine. |
| **Meeting Summary** | A concise summary of the key discussion points and context. |
| **Decisions** | Lists only decisions that were actually made. Suggestions and undecided ideas are left out. |
| **Action Items** | Extracts tasks, with the responsible person and deadline when they are explicitly stated. |
| **Open Questions** | Lists unresolved questions that need follow-up. |
| **Ask Your Meeting** | A retrieval-augmented (RAG) Q&A that answers only from the transcript. When the answer isn't in the meeting, it says so instead of guessing. |

Morrow is designed to **stay grounded**. It never invents names, deadlines or decisions that weren't in the conversation.

---

## How It Works

```text
YouTube URL / Meeting Recording
              │
              ▼
     Audio Extraction (yt-dlp)
              │
              ▼
  Normalization (16 kHz mono, loudnorm)
              │
              ▼
   Chunking (11-min overlapping segments)
              │
              ▼
     Local Transcription (Whisper)
              │
              ▼
        Meeting Transcript
         │              │
         ▼              ▼
   LLM Analysis     Vector Store
     (Groq)      (Chroma + MiniLM)
         │              │
         ▼              ▼
  Summary · Decisions   RAG Q&A
  Actions · Questions
```

**Long meetings** are split into text chunks. Each chunk is analyzed on its own, and the results are then merged into one final report with duplicates removed. Short meetings skip the merge step, so no details are lost.

**Q&A**: the transcript is embedded into a Chroma collection that belongs to that meeting. For each question, Morrow retrieves the most relevant passages, and the LLM answers using only those passages.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Audio download | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Audio processing | [FFmpeg](https://ffmpeg.org/) |
| Speech-to-text | [OpenAI Whisper](https://github.com/openai/whisper) (`small`, local) |
| LLM | [Groq](https://groq.com/) via `langchain-groq` |
| Orchestration | [LangChain](https://www.langchain.com/) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector database | [Chroma](https://www.trychroma.com/) |

---

## Project Structure

```text
Morrow/
├── backend/
│   └── utils/
│       ├── config.py             # Paths, environment, shared Groq LLM
│       ├── audio_processor.py    # Download, normalize and chunk audio
│       ├── whisper_processor.py  # Local Whisper transcription
│       ├── summarizer.py         # Summary, decisions, actions, questions
│       ├── vector_store.py       # Transcript embeddings in Chroma
│       ├── rag_engine.py         # Question answering over a meeting
│       ├── main.py               # End-to-end pipeline (CLI)
│       └── test_rag.py           # Interactive RAG demo
├── chroma_db/                    # Persisted vector store
├── downloads/                    # Downloaded audio and chunks (git-ignored)
├── requirements.txt
└── .env                          # API keys (git-ignored)
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **FFmpeg**, installed and on your `PATH`
  ```bash
  # macOS
  brew install ffmpeg

  # Ubuntu / Debian
  sudo apt install ffmpeg
  ```
- A **Groq API key**, free from [console.groq.com](https://console.groq.com/keys)

### Installation

```bash
# Clone the repository
git clone https://github.com/supremeinferno/Morrow.git
cd Morrow

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> The first run downloads the Whisper and embedding models, which takes a few minutes. Later runs use the cached copies.

---

## Usage

Run all commands from the project root.

### Analyze a meeting

```bash
python -m backend.utils.main
```

Paste a YouTube URL when prompted. Morrow downloads the audio, transcribes it and prints a report:

```text
############################################################
MORROW — MEETING ANALYSIS
############################################################

============================================================
MEETING SUMMARY
============================================================
The team discussed the upcoming product release, the backend
timeline and the production database.

============================================================
DECISIONS
============================================================
- Use PostgreSQL for the production database.

============================================================
ACTION ITEMS
============================================================
- Pranav will complete the authentication API by Friday.

============================================================
OPEN QUESTIONS
============================================================
- Should the first release include email notifications?
```

### Ask questions about a meeting

```bash
python -m backend.utils.test_rag
```

```text
Question: When can the frontend work start?
After the authentication API is completed, which is expected by Friday.

Question: How much budget was allocated?
I couldn't find that information in the meeting.
```

Enter a blank line to quit.

---

## Configuration

| Setting | Location | Default |
| --- | --- | --- |
| LLM model | `GROQ_MODEL` in `config.py` | `openai/gpt-oss-120b` |
| Whisper model size | `WHISPER_MODEL` in `whisper_processor.py` | `small` |
| Audio chunk length / overlap | `chunk_audio()` in `audio_processor.py` | 660 s / 5 s |
| Analysis chunk size | `text_splitter` in `summarizer.py` | 6000 chars / 500 overlap |
| RAG chunk size | `rag_splitter` in `vector_store.py` | 1000 chars / 150 overlap |
| Retrieved passages per question | `k` in `ask_meeting()` | 4 |

**Tip:** for better accuracy on noisy audio, use a larger Whisper model (`medium`, `large`). It runs slower.

---

## Roadmap

- [x] Local transcription with Whisper
- [x] Summary, decisions, action items and open questions
- [x] RAG-based Q&A over meeting transcripts
- [ ] Upload local audio and video files
- [ ] Web interface (Streamlit)
- [ ] Export reports as PDF
- [ ] Speaker identification
