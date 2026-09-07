# RCA Agent — AI-Powered Root Cause Analysis

An intelligent Root Cause Analysis (RCA) assistant powered by OpenAI GPT-4o-mini and LangGraph. Paste an error log or stack trace and get a structured RCA report. Ask general or technical questions and get concise answers.

---

## How It Works

When a user sends a message, the backend automatically detects the type of input and routes it accordingly:

```
User Input
    │
    ├── Greeting / Simple Question ──► Direct LLM response
    │
    └── Error Log / Stack Trace ──► LangGraph RCA Pipeline
                                          │
                                    1. Analyze Logs
                                          │
                                    2. Generate Hypothesis
                                          │
                                    3. Choose Diagnostic Tool
                                          │
                                    4. Validate (run tool)
                                          │
                                    5. Suggest Fix (RCA Report)
```

### LangGraph Agent Pipeline

| Step | Node | Description |
|------|------|-------------|
| 1 | `analyze` | LLM analyzes the error log and identifies what went wrong |
| 2 | `hypothesis` | LLM generates one specific root cause hypothesis |
| 3 | `choose_tool` | LLM selects and calls the best diagnostic tool from the registry |
| 4 | `validate` | Tool is executed; result determines if hypothesis is confirmed |
| 5 | `fix` | LLM generates the final structured RCA report |

If the hypothesis is not validated and attempts < 3, the agent retries from step 2 with a new hypothesis.

### Diagnostic Tools (`tools.py`)

| Tool | Description |
|------|-------------|
| `check_network_port` | Checks TCP connectivity to a host and port |
| `check_http_endpoint` | Sends a GET request to verify an HTTP endpoint |
| `inspect_file_or_log` | Checks if a file exists and returns its size |
| `check_system_process` | Checks if a process is running on the OS |

---

## RCA Report Format

For every error log, the agent outputs a structured report:

```
RCA REPORT [No Incident ID provided]

## INCIDENT SUMMARY
## TIMELINE OF EVENTS
## ROOT CAUSE
## CONTRIBUTING FACTORS
## IMMEDIATE FIX
## PERMANENT FIX
## DETECTION GAPS
## PREVENTION
```

---

## Project Structure

```
rca-agent/
├── backend_main.py       # FastAPI backend — API routes, message routing, serves frontend
├── rca_agent.py          # LangGraph agent pipeline (analyze → hypothesis → tool → validate → fix)
├── tools.py              # Diagnostic tool registry (network, HTTP, file, process checks)
├── static/
│   └── index.html        # HTML/JS chat frontend
├── knowledge_base/       # Upload .txt/.log/.md files to give the agent extra context
├── requirements.txt
├── .env
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | OpenAI GPT-4o-mini |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| Backend | FastAPI + Uvicorn |
| Frontend | HTML + CSS + JavaScript (Vanilla) |
| Deployment | Render |

---

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key — get one at [platform.openai.com](https://platform.openai.com)

### Installation

```bash
git clone https://github.com/your-username/rca-agent.git
cd rca-agent
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in your API key:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Run

```bash
python backend_main.py
```

Open `http://localhost:8000` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the chat UI (`index.html`) |
| `GET` | `/health` | Health check — returns model and config status |
| `POST` | `/execute` | Main chat endpoint — routes to agent or LLM |
| `POST` | `/knowledge-base/upload` | Upload `.txt`, `.log`, `.md` files to knowledge base |
| `GET` | `/knowledge-base` | List files currently in the knowledge base |

### POST `/execute` — Request / Response

**Request:**
```json
{
  "message": "java.lang.NullPointerException: Cannot invoke Order.getShippingAddress()"
}
```

**Response:**
```json
{
  "response": "RCA REPORT [No Incident ID provided]\n\n## INCIDENT SUMMARY\n...",
  "message_type": "error_log"
}
```

---

## Knowledge Base

You can upload reference documents (runbooks, architecture docs, past incident reports) to the `knowledge_base/` folder. The agent will include this context when generating responses for non-error-log queries.

Supported formats: `.txt`, `.log`, `.md`

Upload via API:
```bash
curl -X POST http://localhost:8000/knowledge-base/upload \
  -F "files=@runbook.md"
```

---

## Deploying to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repository
4. Set the following:

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python backend_main.py` |
| Environment Variable | `OPENAI_API_KEY` = `sk-...` |

5. Deploy — your app will be live at `https://your-app.onrender.com`

The frontend and backend are served from the same service — no separate deployment needed.

---

## Message Type Detection

The backend automatically classifies incoming messages:

| Type | Trigger | Handled By |
|------|---------|------------|
| `greeting` | "hi", "hello", "hey" (< 20 chars) | Direct LLM |
| `simple_question` | "what is", "how to", "why is", etc. | Direct LLM |
| `complex_question` | Contains `?` and > 50 chars | Direct LLM |
| `error_log` | Stack trace keywords, log patterns, or > 200 chars | LangGraph Agent |
| `general` | Everything else | Direct LLM |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `PORT` | No | Port to run the server on (default: `8000`, auto-set by Render) |
