import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Make sure it is present in the root .env file."
    )


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    api_key=GEMINI_API_KEY,
    max_tokens=None,
    timeout=None,
    max_retries=5,
)


# --------------------------------------------------
# PARSER
# --------------------------------------------------

parser = JsonOutputParser()


# --------------------------------------------------
# TEXT SPLITTER
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,
    chunk_overlap=500
)


# --------------------------------------------------
# ANALYSIS PROMPT
# --------------------------------------------------

analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI meeting assistant.

Analyze the provided meeting transcript portion.

Extract exactly these four things:

1. SUMMARY
Summarize the important discussion, context, and key points.
Keep it concise and factual.

2. DECISIONS
Include only decisions that were actually made.
Do not include suggestions, opinions, possibilities, or discussions
that did not result in a decision.

3. ACTION ITEMS
Include tasks that someone is expected to perform.
Include the responsible person only when explicitly stated.
Include the deadline only when explicitly stated.

4. OPEN QUESTIONS
Include important questions that remain unanswered,
unresolved, or require follow-up.
Do not include questions that were clearly answered.

STRICT RULES:
- Do not invent information.
- Do not infer names.
- Do not infer deadlines.
- Do not convert suggestions into decisions.
- Do not convert normal conversation into action items.
- If a category has no valid information, return an empty list.
- Return valid JSON only.

Return exactly:

{{
    "summary": "",
    "decisions": [],
    "actions": [],
    "questions": []
}}

{format_instructions}
"""
    ),
    (
        "human",
        "Meeting transcript portion:\n\n{transcript}"
    )
])


analysis_chain = analysis_prompt | llm | parser


# --------------------------------------------------
# CONSOLIDATION PROMPT
# --------------------------------------------------

consolidation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI meeting assistant.

You are given analysis results from different portions of the
same meeting.

Create one final meeting analysis.

SUMMARY:
- Combine the important points.
- Remove repetition.
- Keep the summary concise and coherent.

DECISIONS:
- Preserve decisions that were actually made.
- Merge duplicate decisions.
- Never turn suggestions into decisions.
- Do not remove a valid decision simply because another chunk
  does not mention it.

ACTION ITEMS:
- Merge duplicate action items.
- Preserve explicitly mentioned responsible people.
- Preserve explicitly mentioned deadlines.
- Do not invent missing information.

OPEN QUESTIONS:
- Keep unresolved questions.
- Merge duplicate questions.
- Remove a question only when the provided results clearly show
  that it was answered.

STRICT RULES:
- Do not invent information.
- Do not lose valid information.
- Preserve all useful details from the analysis results.
- Return valid JSON only.

Return exactly:

{{
    "summary": "",
    "decisions": [],
    "actions": [],
    "questions": []
}}

{format_instructions}
"""
    ),
    (
        "human",
        "Meeting analysis results:\n\n{results}"
    )
])


consolidation_chain = consolidation_prompt | llm | parser


# --------------------------------------------------
# MAIN ANALYSIS FUNCTION
# --------------------------------------------------

def analyze_meeting(transcript):

    text_chunks = text_splitter.split_text(transcript)

    print(
        f"\nTranscript split into "
        f"{len(text_chunks)} text chunk(s)."
    )

    chunk_results = []

    # ----------------------------------------------
    # ANALYZE EACH TRANSCRIPT CHUNK
    # ----------------------------------------------

    for i, chunk in enumerate(text_chunks, start=1):

        print(
            f"Processing text chunk "
            f"{i}/{len(text_chunks)}..."
        )

        result = analysis_chain.invoke({
            "transcript": chunk,
            "format_instructions": parser.get_format_instructions()
        })

        # Ensure expected fields always exist
        result = {
            "summary": result.get("summary", ""),
            "decisions": result.get("decisions", []),
            "actions": result.get("actions", []),
            "questions": result.get("questions", [])
        }

        chunk_results.append(result)

    # ----------------------------------------------
    # IMPORTANT:
    # If there is only ONE transcript chunk,
    # return it directly.
    #
    # This avoids an unnecessary second LLM call
    # and prevents the consolidation step from
    # accidentally removing valid information.
    # ----------------------------------------------

    if len(chunk_results) == 1:

        print("\nSingle chunk detected.")
        print("Skipping consolidation.")

        return chunk_results[0]

    # ----------------------------------------------
    # MULTI-CHUNK CONSOLIDATION
    # ----------------------------------------------

    print("\nConsolidating meeting analysis...")

    results_text = json.dumps(
        chunk_results,
        ensure_ascii=False,
        indent=2
    )

    final_result = consolidation_chain.invoke({
        "results": results_text,
        "format_instructions": parser.get_format_instructions()
    })

    # Ensure final structure is consistent
    final_result = {
        "summary": final_result.get("summary", ""),
        "decisions": final_result.get("decisions", []),
        "actions": final_result.get("actions", []),
        "questions": final_result.get("questions", [])
    }

    return final_result