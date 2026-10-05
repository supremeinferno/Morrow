from backend.utils.audio_processor import (
    download_audio,
    normalize_audio,
    chunk_audio
)

from backend.utils.whisper_processor import (
    transcribe_all_chunks
)

from backend.utils.summarizer import (
    analyze_meeting
)


def main():

    url = input("Enter YouTube URL: ")

    print("\nDownloading audio...")
    audio_file = download_audio(url)
    print(f"Downloaded: {audio_file}")

    print("\nNormalizing audio...")
    normalized_file = normalize_audio(audio_file)
    print(f"Normalized: {normalized_file}")

    print("\nCreating audio chunks...")
    chunks = chunk_audio(normalized_file)
    print(f"Created {len(chunks)} audio chunks.")

    print("\nStarting transcription...")
    transcript = transcribe_all_chunks(
        normalized_file.parent / "chunks"
    )
    print("\nTranscription completed.")

    print("\nAnalyzing meeting...")
    analysis_result = analyze_meeting(transcript)

    print("\n" + "=" * 60)
    print("MEETING SUMMARY")
    print("=" * 60)
    print(analysis_result["summary"])

    print("\n" + "=" * 60)
    print("DECISIONS")
    print("=" * 60)

    for decision in analysis_result["decisions"]:
        print("-", decision)

    print("\n" + "=" * 60)
    print("ACTION ITEMS")
    print("=" * 60)

    for action in analysis_result["actions"]:
        print("-", action)

    print("\n" + "=" * 60)
    print("OPEN QUESTIONS")
    print("=" * 60)

    for question in analysis_result["questions"]:
        print("-", question)


if __name__ == "__main__":
    main()