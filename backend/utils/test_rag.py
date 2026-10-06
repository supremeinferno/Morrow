from backend.utils.vector_store import create_vector_store
from backend.utils.rag_engine import ask_meeting


def main():

    test_transcript = """
    The team discussed the upcoming product release.

    Pranav will complete the authentication API by Friday.
    The team decided to use PostgreSQL for the production database.

    The frontend work will begin after the authentication API is completed.

    One unresolved question is whether the first release should include
    email notifications.
    """

    print("\nCreating vector store...")
    vector_store, meeting_id = create_vector_store(test_transcript)

    print("\nVector store ready.")
    print(f"Meeting ID: {meeting_id}")

    question = input("\nAsk a question about the meeting: ").strip()

    answer = ask_meeting(
        vector_store,
        question
    )

    print("\n" + "=" * 60)
    print("MORROW")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()