from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.utils.config import get_llm


NOT_FOUND = "I couldn't find that information in the meeting."

rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""You are Morrow, an AI meeting assistant.

Answer the user's question using only the provided
meeting transcript context.

Rules:
- Use only information present in the context.
- Do not invent or assume facts.
- If the answer is not present in the context, say:
  "{NOT_FOUND}"
- Keep the answer clear and concise.

Meeting context:

{{context}}
""",
    ),
    ("human", "{question}"),
])

rag_chain = rag_prompt | get_llm() | StrOutputParser()


def ask_meeting(vector_store, question, k=4):
    """Retrieve relevant transcript chunks and answer the question."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    documents = vector_store.similarity_search(question, k=k)

    if not documents:
        return NOT_FOUND

    context = "\n\n".join(document.page_content for document in documents)

    return rag_chain.invoke({"context": context, "question": question})
