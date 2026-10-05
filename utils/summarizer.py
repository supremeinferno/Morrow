from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


# -------------------------
# LLM
# -------------------------

llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)


# -------------------------
# Parser
# -------------------------

parser = StrOutputParser()


# -------------------------
# Text Splitter
# -------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,
    chunk_overlap=500
)


# -------------------------
# Partial Summary
# -------------------------

summary_chunk_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI meeting assistant. "
        "Summarize the following portion of a meeting. "
        "Capture the important discussion, decisions, and context. "
        "Do not invent information."
    ),
    (
        "human",
        "Meeting transcript portion:\n\n{transcript}"
    )
])

summary_chunk_chain = summary_chunk_prompt | llm | parser


# -------------------------
# Final Summary
# -------------------------

final_summary_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI meeting assistant. "
        "Combine the provided partial summaries into one clear, "
        "concise and accurate final meeting summary. "
        "Remove repetition and preserve important information. "
        "Do not invent information."
    ),
    (
        "human",
        "Partial meeting summaries:\n\n{summaries}"
    )
])

final_summary_chain = final_summary_prompt | llm | parser


# -------------------------
# Analyze Meeting
# -------------------------

def analyze_meeting(transcript):

    # Split the large transcript into manageable text chunks
    text_chunks = text_splitter.split_text(transcript)

    print(f"\nTranscript split into {len(text_chunks)} text chunks.")

    # Summarize each chunk
    partial_summaries = []

    for i, chunk in enumerate(text_chunks, start=1):

        print(f"Processing text chunk {i}/{len(text_chunks)}...")

        summary = summary_chunk_chain.invoke({
            "transcript": chunk
        })

        partial_summaries.append(summary)

    # Combine partial summaries
    combined_summaries = "\n\n".join(partial_summaries)

    final_summary = final_summary_chain.invoke({
        "summaries": combined_summaries
    })

    return {
        "summary": final_summary
    }