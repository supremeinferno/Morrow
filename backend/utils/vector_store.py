from functools import cache
from uuid import uuid4

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.utils.config import VECTOR_DB_DIR


class MiniLMEmbeddings(Embeddings):
    """
    all-MiniLM-L6-v2 run through ONNX Runtime (bundled with Chroma), which
    needs far less memory than loading it with PyTorch.
    """

    def __init__(self):
        self.model = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts):
        return [[float(value) for value in vector] for vector in self.model(texts)]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


@cache
def get_embeddings():
    """Load the embedding model once, on first use."""

    return MiniLMEmbeddings()


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
        embedding_function=get_embeddings(),
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
