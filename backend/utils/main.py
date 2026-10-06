from pathlib import Path

from backend.utils.audio_processor import (
    download_audio,
    normalize_audio,
    chunk_audio,
)

from backend.utils.whisper_processor import (
    transcribe_all_chunks,
)

from backend.utils.summarizer import (
    analyze_meeting,
)


def print_section(title, items):
    """Print a formatted section for list-based results."""

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    if not items:
        print("None found.")
        return

    for item in items:
        print(f"- {item}")


def main():
    print("\n" + "=" * 60)
    print("MORROW — AI MEETING ASSISTANT")
    print("=" * 60)

    url = input("\nEnter YouTube URL: ").strip()

    if not url:
        print("\nError: YouTube URL cannot be empty.")
        return

    try:
        # --------------------------------------------------
        # 1. DOWNLOAD AUDIO
        # --------------------------------------------------

        print("\n[1/4] Downloading audio...")
        audio_file = download_audio(url)

        print(f"Downloaded: {audio_file}")

        # --------------------------------------------------
        # 2. NORMALIZE + CHUNK AUDIO
        # --------------------------------------------------

        print("\n[2/4] Processing audio...")

        normalized_file = normalize_audio(audio_file)

        print(f"Normalized: {normalized_file}")

        chunks = chunk_audio(normalized_file)

        print(f"Created {len(chunks)} audio chunk(s).")

        # --------------------------------------------------
        # 3. TRANSCRIPTION
        # --------------------------------------------------

        print("\n[3/4] Transcribing audio...")

        transcript = transcribe_all_chunks(
            normalized_file.parent / "chunks"
        )

        if not transcript.strip():
            print("\nError: No transcript was generated.")
            return

        print("Transcription completed.")

        # --------------------------------------------------
        # 4. MEETING ANALYSIS
        # --------------------------------------------------

        print("\n[4/4] Analyzing meeting...")

        analysis_result = analyze_meeting(transcript)

        # --------------------------------------------------
        # FINAL OUTPUT
        # --------------------------------------------------

        print("\n" + "#" * 60)
        print("MORROW — MEETING ANALYSIS")
        print("#" * 60)

        print("\n" + "=" * 60)
        print("MEETING SUMMARY")
        print("=" * 60)
        print(
            analysis_result.get(
                "summary",
                "No summary available."
            )
        )

        print_section(
            "DECISIONS",
            analysis_result.get("decisions", [])
        )

        print_section(
            "ACTION ITEMS",
            analysis_result.get("actions", [])
        )

        print_section(
            "OPEN QUESTIONS",
            analysis_result.get("questions", [])
        )

        print("\n" + "#" * 60)
        print("Morrow analysis completed successfully.")
        print("#" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()