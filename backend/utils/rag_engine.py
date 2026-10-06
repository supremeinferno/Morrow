import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in the root .env file."
    )


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    api_key=GEMINI_API_KEY,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


# --------------------------------------------------
# PROMPT
# --------------------------------------------------

rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are Morrow, an AI meeting assistant.

Answer the user's question using only the provided
meeting transcript context.

Rules:
- Use only information present in the context.
- Do not invent or assume facts.
- If the answer is not present in the context, say:
  "I couldn't find that information in the meeting."
- Keep the answer clear and concise.

Meeting context:

{context}
"""
    ),
    (
        "human",
        "{question}"
    )
])


# --------------------------------------------------
# RAG CHAIN
# --------------------------------------------------

rag_chain = rag_prompt | llm | StrOutputParser()


# --------------------------------------------------
# ASK A QUESTION
# --------------------------------------------------

def ask_meeting(vector_store, question, k=4):
    """
    Retrieve relevant transcript chunks and answer
    the user's question using Gemini.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    retriever = vector_store.as_retriever(
        search_kwargs={"k": k}
    )

    documents = retriever.invoke(question)

    if not documents:
        return "I couldn't find that information in the meeting."

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    answer = rag_chain.invoke({
        "context": context,
        "question": question
    })

    return answer
