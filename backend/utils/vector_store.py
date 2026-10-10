from uuid import uuid4

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.utils.config import VECTOR_DB_DIR


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={"normalize_embeddings": True},
)

rag_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)


def create_vector_store(transcript):
    """
    Split a transcript into chunks, embed them, and store them
    in a dedicated Chroma collection for this meeting.
    """

    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    text_chunks = rag_splitter.split_text(transcript)
    meeting_id = uuid4().hex

    vector_store = Chroma(
        collection_name=f"meeting_{meeting_id}",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
    )

    vector_store.add_texts(
        texts=text_chunks,
        metadatas=[
            {"meeting_id": meeting_id, "chunk_index": index}
            for index in range(len(text_chunks))
        ],
    )

    print(f"Vector store created with {len(text_chunks)} chunk(s).")

    return vector_store, meeting_id
