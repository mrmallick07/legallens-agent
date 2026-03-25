import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext

# --- Setup Logging and Environment ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

# --- Tool: Save clause to state ---
def save_clause(tool_context: ToolContext, clause: str) -> dict:
    """Saves the user's legal clause to state."""
    tool_context.state["CLAUSE"] = clause
    logging.info(f"[State updated] Clause saved: {clause}")
    return {"status": "success"}

# --- Tool: Flag risk level ---
def flag_risk(clause: str) -> dict:
    """Analyzes a legal clause and returns risk_level as HIGH, MEDIUM, or LOW with a reason."""
    clause_lower = clause.lower()

    high_keywords = ["non-compete", "non compete", "indemnif", "unlimited liability",
                     "perpetual", "irrevocable", "waive all", "sole discretion",
                     "terminate immediately", "intellectual property assign"]
    medium_keywords = ["confidential", "exclusiv", "automatic renewal",
                       "liquidated damages", "arbitration", "governing law", "force majeure"]

    for kw in high_keywords:
        if kw in clause_lower:
            return {"risk_level": "HIGH", "risk_reason": f"Contains '{kw}' — limits your rights or exposes you to major liability."}
    for kw in medium_keywords:
        if kw in clause_lower:
            return {"risk_level": "MEDIUM", "risk_reason": f"Contains '{kw}' — review carefully before signing."}

    return {"risk_level": "LOW", "risk_reason": "No high-risk keywords detected. Standard clause — still read carefully."}


# --- Agent ---
root_agent = Agent(
    name="legal_clause_simplifier",
    model=model_name,
    description="Simplifies dense legal clauses into plain English and flags risk.",
    instruction="""
    You are LegalLens, a legal clause simplifier assistant for freelancers, founders, and SMEs.

    When the user pastes a legal clause:
    1. Call 'save_clause' tool to save it to state.
    2. Call 'flag_risk' tool with the clause text to determine risk level.
    3. Explain the clause in plain English — 2 to 3 sentences, zero jargon.
    4. End your response with:
       🚨 RISK LEVEL: [HIGH/MEDIUM/LOW] — [risk_reason from tool]

    Be direct, helpful, and friendly. You are not a lawyer but you help people understand what they're signing.
    """,
    tools=[save_clause, flag_risk]
)
