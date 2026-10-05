from backend.utils.audio_processor import (
    download_audio,
    normalize_audio,
    chunk_audio
)

from backend.utils.whisper_processor import transcribe_all_chunks
from backend.utils.summarizer import analyze_meeting
from backend.utils.extractor import extract_meeting_details


def main():

    # -------------------------
    # Get YouTube URL
    # -------------------------

    url = input("Enter YouTube URL: ")

    # -------------------------
    # Audio Processing
    # -------------------------

    print("\nDownloading audio...")

    audio_file = download_audio(url)

    print(f"Downloaded: {audio_file}")

    print("\nNormalizing audio...")

    normalized_file = normalize_audio(audio_file)

    print(f"Normalized: {normalized_file}")

    print("\nCreating audio chunks...")

    chunks = chunk_audio(normalized_file)

    print(f"Created {len(chunks)} audio chunks.")

    # -------------------------
    # Transcription
    # -------------------------

    print("\nStarting transcription...")

    transcript = transcribe_all_chunks(
        normalized_file.parent / "chunks"
    )

    print("\nTranscription completed.")

    # -------------------------
    # Summarization
    # -------------------------

    print("\nGenerating meeting summary...")

    summary_result = analyze_meeting(transcript)

    # -------------------------
    # Extraction
    # -------------------------

    print("\nExtracting meeting details...")

    extraction_result = extract_meeting_details(
        transcript
    )

    # -------------------------
    # Final Output
    # -------------------------

    print("\n" + "=" * 60)
    print("MEETING SUMMARY")
    print("=" * 60)

    print(summary_result["summary"])

    print("\n" + "=" * 60)
    print("DECISIONS")
    print("=" * 60)

    for decision in extraction_result["decisions"]:
        print("-", decision)

    print("\n" + "=" * 60)
    print("ACTION ITEMS")
    print("=" * 60)

    for action in extraction_result["actions"]:
        print("-", action)

    print("\n" + "=" * 60)
    print("OPEN QUESTIONS")
    print("=" * 60)

    for question in extraction_result["questions"]:
        print("-", question)


if __name__ == "__main__":
    main()