import json

from dotenv import load_dotenv
from pathlib import Path

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

parser = JsonOutputParser()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,
    chunk_overlap=500
)


analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI meeting assistant.

Analyze the following portion of a meeting transcript.

Extract all of the following:

1. SUMMARY
- Summarize the important discussion and context.
- Keep it concise.
- Do not invent information.

2. DECISIONS
- Include only decisions that were actually made.
- Do not include suggestions or possibilities.

3. ACTION ITEMS
- Include tasks that someone needs to perform.
- Include the responsible person only if explicitly mentioned.
- Include the deadline only if explicitly mentioned.

4. OPEN QUESTIONS
- Include important questions that remain unanswered.
- Do not include questions that were clearly answered.

Rules:
- Do not invent information.
- Do not infer names, deadlines, decisions, or answers.
- If nothing exists for a category, return an empty list.

Return exactly this JSON structure:

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


consolidation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI meeting assistant.

You are given analysis results from different portions of the same meeting.

Create one final accurate meeting analysis.

SUMMARY:
- Combine the important information.
- Remove repetition.
- Keep the final summary concise and coherent.

DECISIONS:
- Keep only decisions that were actually made.
- Merge duplicate decisions.
- Do not turn suggestions into decisions.

ACTION ITEMS:
- Merge duplicate action items.
- Preserve responsible people when explicitly available.
- Preserve deadlines when explicitly available.

OPEN QUESTIONS:
- Keep only unresolved questions.
- Merge duplicate questions.
- Remove questions that were answered elsewhere.

Rules:
- Do not invent information.
- Do not lose important information.
- Prefer specific information over vague duplicates.

Return exactly this JSON structure:

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


def analyze_meeting(transcript):

    text_chunks = text_splitter.split_text(transcript)

    print(
        f"\nTranscript split into "
        f"{len(text_chunks)} text chunks."
    )

    combined_results = {
        "summary": [],
        "decisions": [],
        "actions": [],
        "questions": []
    }

    for i, chunk in enumerate(text_chunks, start=1):

        print(
            f"Processing text chunk "
            f"{i}/{len(text_chunks)}..."
        )

        result = analysis_chain.invoke({
            "transcript": chunk,
            "format_instructions": parser.get_format_instructions()
        })

        combined_results["summary"].append(
            result.get("summary", "")
        )

        combined_results["decisions"].extend(
            result.get("decisions", [])
        )

        combined_results["actions"].extend(
            result.get("actions", [])
        )

        combined_results["questions"].extend(
            result.get("questions", [])
        )

    results_text = json.dumps(
        combined_results,
        ensure_ascii=False,
        indent=2
    )

    print("\nConsolidating meeting analysis...")

    final_result = consolidation_chain.invoke({
        "results": results_text,
        "format_instructions": parser.get_format_instructions()
    })

    return final_result