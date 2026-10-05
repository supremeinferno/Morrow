import json

from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
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

parser = JsonOutputParser()


# -------------------------
# Text Splitter
# -------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,
    chunk_overlap=500
)


# -------------------------
# Extraction Prompt
# -------------------------

extraction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI meeting assistant.

Analyze the following portion of a meeting transcript and extract:

1. DECISIONS
- Include only decisions that were actually made.
- Do not include suggestions, possibilities, or undecided ideas.

2. ACTION ITEMS
- Include tasks that someone needs to perform.
- Include the responsible person only if explicitly mentioned.
- Include the deadline only if explicitly mentioned.

3. OPEN QUESTIONS
- Include important questions that remain unanswered or require follow-up.
- Do not include questions that were clearly answered.

Rules:
- Do not invent information.
- Do not infer names, deadlines, decisions, or answers.
- If nothing relevant exists for a category, return an empty list.

Return the result as JSON.

{format_instructions}

Meeting transcript portion:

{transcript}"""
    )
])


# -------------------------
# Extraction Chain
# -------------------------

extraction_chain = extraction_prompt | llm | parser


# -------------------------
# Extract Meeting Details
# -------------------------

def extract_meeting_details(transcript):

    # Split large transcript into manageable chunks
    text_chunks = text_splitter.split_text(transcript)

    print(f"\nTranscript split into {len(text_chunks)} text chunks.")

    combined_results = {
        "decisions": [],
        "actions": [],
        "questions": []
    }

    # Process each transcript chunk
    for i, chunk in enumerate(text_chunks, start=1):

        print(
            f"Processing text chunk "
            f"{i}/{len(text_chunks)}..."
        )

        result = extraction_chain.invoke({
            "transcript": chunk,
            "format_instructions": parser.get_format_instructions()
        })

        combined_results["decisions"].extend(
            result.get("decisions", [])
        )

        combined_results["actions"].extend(
            result.get("actions", [])
        )

        combined_results["questions"].extend(
            result.get("questions", [])
        )

    # -------------------------
    # Prepare Extracted Results
    # -------------------------

    results_text = json.dumps(
        combined_results,
        ensure_ascii=False,
        indent=2
    )

    # -------------------------
    # Reduction Splitter
    # -------------------------

    reduction_chunks = reduction_splitter.split_text(
        results_text
    )

    print(
        f"\nExtracted information split into "
        f"{len(reduction_chunks)} reduction chunk(s)."
    )

    # -------------------------
    # Single Reduction Chunk
    # -------------------------

    if len(reduction_chunks) == 1:

        print(
            "\nConsolidating extracted information..."
        )

        final_result = consolidation_chain.invoke({
            "results": reduction_chunks[0],
            "format_instructions": parser.get_format_instructions()
        })

        return final_result

    # -------------------------
    # Multiple Reduction Chunks
    # -------------------------

    intermediate_results = []

    for i, chunk in enumerate(reduction_chunks, start=1):

        print(
            f"Consolidating reduction chunk "
            f"{i}/{len(reduction_chunks)}..."
        )

        result = consolidation_chain.invoke({
            "results": chunk,
            "format_instructions": parser.get_format_instructions()
        })

        intermediate_results.append(result)

    # -------------------------
    # Final Global Consolidation
    # -------------------------

    intermediate_text = json.dumps(
        intermediate_results,
        ensure_ascii=False,
        indent=2
    )

    print(
        "\nPerforming final global consolidation..."
    )

    final_result = consolidation_chain.invoke({
        "results": intermediate_text,
        "format_instructions": parser.get_format_instructions()
    })

    return final_result


# -------------------------
# Reduction Splitter
# -------------------------

reduction_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,
    chunk_overlap=0
)


# -------------------------
# Consolidation Prompt
# -------------------------

consolidation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI meeting assistant.

You are given extracted information from different portions of the same meeting.

Consolidate the information into one accurate result.

DECISIONS:
- Keep only decisions that were actually made.
- Merge duplicate or semantically identical decisions.
- Do not turn suggestions into decisions.

ACTION ITEMS:
- Merge duplicate or semantically identical action items.
- Preserve the responsible person when explicitly available.
- Preserve the deadline when explicitly available.
- Do not invent missing information.

OPEN QUESTIONS:
- Keep only questions that remain unresolved or require follow-up.
- Merge duplicate or semantically identical questions.
- Remove questions that were answered elsewhere in the provided information.

Rules:
- Do not invent information.
- Do not lose important information.
- Prefer specific information over vague duplicates.
- Return only the final structured JSON.

Return exactly this structure:

{{
    "decisions": [],
    "actions": [],
    "questions": []
}}

{format_instructions}

Extracted meeting information:

{results}"""
    )
])


# -------------------------
# Consolidation Chain
# -------------------------

consolidation_chain = consolidation_prompt | llm | parser