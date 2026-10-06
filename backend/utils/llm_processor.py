from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


# -------------------------
# LLM
# -------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.0,  
    max_tokens=None,
    timeout=None,
    max_retries=5,
)


# -------------------------
# Output Parser
# -------------------------

parser = StrOutputParser()


# -------------------------
# Summary
# -------------------------

summary_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI meeting assistant. "
        "Create a concise and accurate summary of the meeting."
    ),
    (
        "human",
        "Meeting transcript:\n\n{transcript}"
    )
])

summary_chain = summary_prompt | llm | parser


# -------------------------
# Key Decisions
# -------------------------

decision_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI meeting assistant. "
        "Extract the important decisions made during the meeting. "
        "If there are no clear decisions, say "
        "'No major decisions identified.'"
    ),
    (
        "human",
        "Meeting transcript:\n\n{transcript}"
    )
])

decision_chain = decision_prompt | llm | parser


# -------------------------
# Action Items
# -------------------------

action_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI meeting assistant. "
        "Extract all actionable tasks from the meeting. "
        "Mention the responsible person if explicitly stated. "
        "Do not invent names or deadlines."
    ),
    (
        "human",
        "Meeting transcript:\n\n{transcript}"
    )
])

action_chain = action_prompt | llm | parser


# -------------------------
# Meeting Analysis
# -------------------------

def analyze_meeting(transcript):
    summary = summary_chain.invoke({
        "transcript": transcript
    })

    decisions = decision_chain.invoke({
        "transcript": transcript
    })

    actions = action_chain.invoke({
        "transcript": transcript
    })

    return {
        "summary": summary,
        "decisions": decisions,
        "actions": actions
    }