import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.utils.config import get_llm


# --------------------------------------------------
# SETUP
# --------------------------------------------------

llm = get_llm()
parser = JsonOutputParser()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,
    chunk_overlap=500,
)

OUTPUT_FORMAT = """Return exactly:

{{
    "summary": "",
    "decisions": [],
    "actions": [],
    "questions": []
}}"""


# --------------------------------------------------
# PROMPTS
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

""" + OUTPUT_FORMAT,
    ),
    ("human", "Meeting transcript portion:\n\n{transcript}"),
])

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

""" + OUTPUT_FORMAT,
    ),
    ("human", "Meeting analysis results:\n\n{results}"),
])

analysis_chain = analysis_prompt | llm | parser
consolidation_chain = consolidation_prompt | llm | parser


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

def normalize_result(result):
    """Make sure every expected field exists, even if the LLM omitted it."""

    return {
        "summary": result.get("summary", ""),
        "decisions": result.get("decisions", []),
        "actions": result.get("actions", []),
        "questions": result.get("questions", []),
    }


def analyze_meeting(transcript):
    """Analyze each transcript chunk, then merge the results into one."""

    text_chunks = text_splitter.split_text(transcript)
    total = len(text_chunks)

    print(f"Transcript split into {total} text chunk(s).")

    chunk_results = []

    for index, chunk in enumerate(text_chunks, start=1):
        print(f"Analyzing text chunk {index}/{total}...")
        result = analysis_chain.invoke({"transcript": chunk})
        chunk_results.append(normalize_result(result))

    # A single chunk needs no merging, and skipping the extra call
    # stops consolidation from accidentally dropping valid details.
    if total == 1:
        return chunk_results[0]

    print("Consolidating meeting analysis...")

    final_result = consolidation_chain.invoke({
        "results": json.dumps(chunk_results, ensure_ascii=False, indent=2),
    })

    return normalize_result(final_result)
