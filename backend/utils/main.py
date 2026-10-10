from backend.utils.audio_processor import (
    chunk_audio,
    download_audio,
    normalize_audio,
)
from backend.utils.summarizer import analyze_meeting
from backend.utils.whisper_processor import transcribe_chunks


def print_header(title, char="="):
    print("\n" + char * 60)
    print(title)
    print(char * 60)


def print_section(title, items):
    """Print a titled list, or a placeholder when it's empty."""

    print_header(title)

    if not items:
        print("None found.")
        return

    for item in items:
        print(f"- {item}")


def print_analysis(analysis):
    print_header("MORROW — MEETING ANALYSIS", "#")

    print_header("MEETING SUMMARY")
    print(analysis["summary"] or "No summary available.")

    print_section("DECISIONS", analysis["decisions"])
    print_section("ACTION ITEMS", analysis["actions"])
    print_section("OPEN QUESTIONS", analysis["questions"])


def run_pipeline(url):
    print("\n[1/4] Downloading audio...")
    audio_file = download_audio(url)
    print(f"Downloaded: {audio_file}")

    print("\n[2/4] Processing audio...")
    normalized_file = normalize_audio(audio_file)
    chunks = chunk_audio(normalized_file)
    print(f"Created {len(chunks)} audio chunk(s).")

    print("\n[3/4] Transcribing audio...")
    transcript = transcribe_chunks(chunks)

    if not transcript.strip():
        raise RuntimeError("No transcript was generated.")

    print("\n[4/4] Analyzing meeting...")
    return analyze_meeting(transcript)


def main():
    print_header("MORROW — AI MEETING ASSISTANT")

    url = input("\nEnter YouTube URL: ").strip()

    if not url:
        print("\nError: YouTube URL cannot be empty.")
        return

    try:
        analysis = run_pipeline(url)
    except Exception as error:
        print_header("ERROR")
        print(f"{type(error).__name__}: {error}")
        return

    print_analysis(analysis)
    print_header("Morrow analysis completed successfully.", "#")


if __name__ == "__main__":
    main()
