from pathlib import Path
from uuid import uuid4

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
VECTOR_DB_DIR = BASE_DIR / "chroma_db"

VECTOR_DB_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={
        "normalize_embeddings": True
    }
)


# --------------------------------------------------
# TEXT SPLITTER
# --------------------------------------------------

rag_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)


# --------------------------------------------------
# CREATE VECTOR STORE
# --------------------------------------------------

def create_vector_store(transcript):
    """
    Split a transcript into smaller chunks, generate embeddings,
    and store them in a dedicated Chroma collection.
    """

    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    text_chunks = rag_splitter.split_text(transcript)

    if not text_chunks:
        raise ValueError("No text chunks were created.")

    meeting_id = uuid4().hex

    documents = [
        {
            "text": chunk,
            "metadata": {
                "meeting_id": meeting_id,
                "chunk_index": index,
            }
        }
        for index, chunk in enumerate(text_chunks)
    ]

    vector_store = Chroma(
        collection_name=f"meeting_{meeting_id}",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
    )

    vector_store.add_texts(
        texts=[document["text"] for document in documents],
        metadatas=[document["metadata"] for document in documents],
    )

    print(
        f"\nVector store created."
        f"\nMeeting ID: {meeting_id}"
        f"\nRAG chunks: {len(text_chunks)}"
    )

    return vector_store, meeting_id
