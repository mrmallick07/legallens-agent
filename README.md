# LegalLens — AI Legal Clause Simplifier & Negotiation Assistant

An AI agent built with **Google ADK** and **Gemini 2.0 Flash**, deployed on **Google Cloud Run**.

## What it does

Paste any dense legal clause and get:
- ✅ **Plain English explanation** — no jargon, 2-sentence summary
- 🚨 **AI-powered risk assessment** — HIGH / MEDIUM / LOW with reason
- ⚖️ **Clause type detection** — Indemnification, NDA, Non-Compete, etc.
- 💬 **Sentiment analysis** — Aggressive, Predatory, Standard, Fair, etc.
- ✏️ **Auto-generated fair rewrite** — for HIGH/MEDIUM risk clauses

### Additional Capabilities
- 🔍 **Compare two clauses** — see which is more favorable and why
- 📄 **Extract clauses from contracts** — paste a full contract, get each clause identified and labeled

## Live Demo
🔗 https://legal-clause-simplifier-114195605527.europe-west1.run.app

## Example

**Input:**
> Employee shall not engage in any competing business within 100 miles for 2 years after termination.

**Output:**
> 📝 **Explanation:** After you leave this job, you cannot work for or start a competing business within 100 miles for 2 years.
>
> ⚖️ **Clause Type:** Non-Compete
>
> 🚨 **Risk Level:** HIGH — This severely restricts your future employment options with a wide geographic and time scope.
>
> 💬 **Tone:** Aggressive
>
> ✏️ **Suggested Revision:** "Employee agrees not to engage in directly competing business within 25 miles for a period of 6 months after termination, limited to the specific line of work performed."

## Tech Stack
- **Google ADK** 1.14.0 — Agent Development Kit
- **Gemini 2.0 Flash** — via Vertex AI
- **Google Cloud Run** — serverless deployment
- **Google Cloud Logging** — production logging

## Project Structure
```
legallens-agent/
├── agent.py          # ADK agent + 3 Gemini-powered tools
├── __init__.py       # Package init
├── requirements.txt  # Dependencies
├── .env.example      # Environment variable template
└── README.md
```

## Tools

| Tool | Description |
|------|-------------|
| `analyze_clause` | Analyzes a clause with Gemini — returns explanation, type, risk, sentiment, and suggested revision |
| `compare_clauses` | Compares two clauses side-by-side — identifies which is more favorable |
| `extract_clauses` | Extracts individual clauses from a block of contract text |

## Setup & Deploy
```bash
# Set environment variables
cp .env.example .env
# Edit .env with your GCP project details

# Deploy to Cloud Run
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=legal-clause-simplifier \
  --with_ui \
  .
```

## Environment Variables
| Variable | Description |
|----------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Region (e.g. europe-west1) |
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to TRUE |
| `MODEL` | e.g. gemini-2.0-flash |