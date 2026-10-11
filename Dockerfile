# Morrow API: FastAPI + FFmpeg. Transcription and the LLM run on Groq, so the
# image stays small enough for low-memory hosts like Render's free plan.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# FFmpeg (and ffprobe) for audio extraction, normalization and chunking.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Deno: the JavaScript runtime yt-dlp uses to solve YouTube's player challenges.
COPY --from=denoland/deno:bin-2.1.4 /deno /usr/local/bin/deno

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Download the embedding model at build time so the first meeting doesn't wait for it.
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()(['warm up'])"

COPY backend ./backend

EXPOSE 8000

# Render provides $PORT; fall back to 8000 locally.
CMD ["sh", "-c", "python -m uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
