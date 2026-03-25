import os
import json
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google import genai
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext

# --- Setup Logging and Environment ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.0-flash")

# --- Gemini Client ---
gemini_client = genai.Client()

# --- Tool: Analyze a legal clause with Gemini ---
def analyze_clause(tool_context: ToolContext, clause: str) -> dict:
    """Analyzes a legal clause using Gemini AI. Returns a structured JSON with plain-English explanation,
    clause type, risk level, risk reason, sentiment, and a suggested fair revision if risky."""

    tool_context.state["CLAUSE"] = clause
    logging.info(f"[State updated] Clause saved for analysis.")

    prompt = f"""You are an elite legal simplification and negotiation expert for non-lawyers.
Analyze the following legal clause and return a structured JSON.
Never include legal advice disclaimers inside the JSON.
Flag anything with uncapped liability, one-sided terms, or vague obligations as HIGH risk.

Return exactly this JSON structure (no markdown fences, just raw JSON):
{{
  "explanation": "<plain English explanation (max 2 sentences)>",
  "clause_type": "<type of clause (e.g., Indemnification, NDA, Non-Compete, Termination, Liability, Confidentiality)>",
  "risk_level": "<LOW or MEDIUM or HIGH>",
  "risk_reason": "<one sentence explaining the risk>",
  "sentiment": "<one word descriptor of the clause tone, e.g., Aggressive, Standard, Predatory, Protective, Fair>",
  "suggested_revision": "<if the clause is HIGH or MEDIUM risk, write a fair, balanced, plain-English version. Otherwise, return 'N/A'>"
}}

Clause to analyze:
{clause}
"""
    try:
        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        result = json.loads(text)
        tool_context.state["ANALYSIS"] = result
        logging.info(f"[Analysis complete] Risk: {result.get('risk_level', 'UNKNOWN')}")
        return result
    except Exception as e:
        logging.error(f"[Analysis error] {str(e)}")
        return {
            "explanation": "Failed to parse analysis.",
            "clause_type": "Unknown",
            "risk_level": "HIGH",
            "risk_reason": f"System error during analysis: {str(e)}",
            "sentiment": "Error",
            "suggested_revision": "N/A"
        }


# --- Tool: Compare two clauses ---
def compare_clauses(clause_a: str, clause_b: str) -> dict:
    """Compares two legal clauses side-by-side. Useful for comparing an original clause vs. a revised version,
    or two different contract terms. Returns which is more favorable and why."""

    prompt = f"""You are a legal clause comparison expert for non-lawyers.
Compare these two legal clauses and return a structured JSON analysis.

Return exactly this JSON structure (no markdown fences, just raw JSON):
{{
  "clause_a_summary": "<1-sentence summary of Clause A>",
  "clause_b_summary": "<1-sentence summary of Clause B>",
  "key_differences": ["<difference 1>", "<difference 2>", "<difference 3>"],
  "more_favorable": "<A or B or EQUAL>",
  "recommendation": "<1-2 sentences explaining which clause is better for the reader and why>"
}}

Clause A:
{clause_a}

Clause B:
{clause_b}
"""
    try:
        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        logging.error(f"[Compare error] {str(e)}")
        return {"error": f"Comparison failed: {str(e)}"}


# --- Tool: Extract individual clauses from contract text ---
def extract_clauses(contract_text: str) -> dict:
    """Extracts and lists individual clauses from a block of contract or legal text.
    Useful when a user pastes an entire contract or a large section with multiple clauses."""

    prompt = f"""You are a legal document parser for non-lawyers.
Extract all distinct clauses from this contract text. For each clause, provide a short label and the clause text.

Return exactly this JSON structure (no markdown fences, just raw JSON):
{{
  "total_clauses_found": <number>,
  "clauses": [
    {{
      "clause_number": 1,
      "label": "<short label, e.g., Indemnification, Payment Terms>",
      "text": "<the exact clause text>"
    }}
  ]
}}

Contract text:
{contract_text}
"""
    try:
        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        logging.error(f"[Extract error] {str(e)}")
        return {"error": f"Extraction failed: {str(e)}"}


# --- Agent ---
root_agent = Agent(
    name="legal_clause_simplifier",
    model=model_name,
    description="LegalLens — AI-powered legal clause simplifier, risk analyzer, and negotiation assistant for freelancers, founders, and SMEs.",
    instruction="""
    You are LegalLens, an AI-powered legal clause simplifier and negotiation assistant.
    You help freelancers, founders, and SMEs understand contracts they're about to sign.

    **CAPABILITIES** (use the right tool for each request):

    1. **Analyze a clause** → Use `analyze_clause` tool.
       Present the result clearly with:
       📝 **Explanation:** [plain English]
       ⚖️ **Clause Type:** [type]
       🚨 **Risk Level:** [HIGH/MEDIUM/LOW] — [reason]
       💬 **Tone:** [sentiment]
       ✏️ **Suggested Revision:** [if applicable]

    2. **Compare two clauses** → Use `compare_clauses` tool.
       Present which is more favorable and why.

    3. **Extract clauses from a contract** → Use `extract_clauses` tool.
       Show each extracted clause with its label and number.

    **BEHAVIOR:**
    - If the user greets you, introduce yourself briefly and ask them to paste a clause.
    - If no clause is provided, ask them to share one.
    - Be direct, helpful, and friendly.
    - Never claim to be a lawyer. You help people understand what they're signing.
    - Format your responses clearly with emojis and sections.
    """,
    tools=[analyze_clause, compare_clauses, extract_clauses]
)
