from backend.utils.rag_engine import ask_meeting
from backend.utils.vector_store import create_vector_store


TEST_TRANSCRIPT = """
The team discussed the upcoming product release.

Pranav will complete the authentication API by Friday.
The team decided to use PostgreSQL for the production database.

The frontend work will begin after the authentication API is completed.

One unresolved question is whether the first release should include
email notifications.
"""


def main():
    print("\nCreating vector store...")
    vector_store, meeting_id = create_vector_store(TEST_TRANSCRIPT)
    print(f"Meeting ID: {meeting_id}")

    print("\nAsk questions about the meeting (blank line to quit).")

    while question := input("\nQuestion: ").strip():
        print("\n" + "=" * 60)
        print("MORROW")
        print("=" * 60)
        print(ask_meeting(vector_store, question))


if __name__ == "__main__":
    main()
