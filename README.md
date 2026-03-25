# LegalLens — AI Legal Clause Simplifier

An AI agent built with **Google ADK** and **Gemini 2.0 Flash**, deployed on **Cloud Run**.

## What it does
Paste any dense legal clause and get:
- ✅ Plain English explanation
- 🚨 Risk flag (HIGH / MEDIUM / LOW) with reason

## Live Demo
🔗 https://legal-clause-simplifier-114195605527.europe-west1.run.app

## Example
**Input:**
> Employee shall not engage in any competing business within 100 miles for 2 years after termination.

**Output:**
> After you leave this job, you cannot work for or start a competing business within 100 miles for 2 years.
> 🚨 RISK LEVEL: HIGH — Contains 'non-compete' — limits your rights or exposes you to major liability.

## Tech Stack
- Google ADK 1.14.0
- Gemini 2.0 Flash (via Vertex AI)
- Google Cloud Run
- Google Cloud Logging

## Project Structure
```
legal_agent/
├── agent.py          # ADK agent + risk flagging tool
├── requirements.txt  # Dependencies
├── .env.example      # Environment variable template
└── README.md
```

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