# Morrow

> **Turn conversations into what comes next.**

Morrow is an AI-powered meeting assistant that transforms long meeting recordings into structured, actionable information.

Instead of going through an entire meeting again, Morrow processes the conversation and surfaces the things that matter — **what was discussed, what was decided, what needs to be done, and what still needs an answer.**

---

## What Morrow Does

Morrow takes a meeting recording or YouTube video and turns it into a concise meeting intelligence report.

### Transcription
Converts meeting audio into text using **OpenAI Whisper**, with local processing.

### Meeting Summary
Generates a concise summary of the important discussions and context.

### Action Items
Identifies tasks that need to be completed and extracts responsible people or deadlines when explicitly mentioned.

### Decisions
Detects decisions that were actually made during the meeting, while avoiding suggestions or undecided ideas.

### Open Questions
Surfaces important questions that remain unresolved and may require follow-up.

### Meeting Intelligence
Morrow is being built to allow users to ask questions about their meetings and retrieve answers directly from the conversation.

---

## How It Works

```text
Meeting / YouTube Video
          ↓
      Audio Extraction
          ↓
   Audio Normalization
          ↓
      Audio Chunking
          ↓
    Local Whisper ASR
          ↓
     Meeting Transcript
          ↓
       LLM Analysis
       ↙    ↓    ↘
   Summary Decisions Actions
              ↓
       Open Questions
              ↓
      Meeting Knowledge Base
              ↓
         RAG / Chat
