# RCA Chat Agent - Marketplace Listing

## 📋 Agent Overview

**RCA Chat Agent** is an AI-powered Root Cause Analysis system that intelligently analyzes error logs, troubleshoots technical issues, and provides expert guidance. It combines conversational AI with an agentic workflow that dynamically selects validation tools and generates hypothesis-based solutions.

### Key Differentiators
- **Agentic Intelligence**: Uses LangGraph for multi-step reasoning with tool selection and validation loops
- **Intelligent Message Routing**: Auto-detects query type (error log, greeting, simple/complex question) and tailors responses
- **Error Log Expertise**: Performs deep RCA analysis with structured output (hypothesis → tool validation → fix recommendations)
- **Knowledge Base Integration**: Contextualizes responses with uploaded documentation
- **Dynamic Tool Selection**: Agent autonomously chooses appropriate diagnostic tools (Kafka, API, file checks)

---

## 🎯 Core Capabilities

### 1. **Error Log Analysis** 🔴
- Analyzes stack traces, exceptions, and error messages
- Performs root cause hypothesis generation
- Validates hypotheses using dynamic tool selection
- Provides structured fix recommendations with prevention tips

### 2. **Conversational Assistance** 💬
- Greetings and friendly responses
- Simple Q&A with direct answers (1-3 sentences)
- Complex technical questions with detailed explanations
- General conversational support with knowledge base context

### 3. **Knowledge Base Integration** 📚
- Uploads custom documentation (.txt, .log, .md files)
- Contextualizes responses with internal knowledge
- Admin panel for knowledge management
- Automatic context injection into LLM prompts

### 4. **Agentic Workflow** 🤖
```
Error Input → Analyze → Generate Hypothesis → Choose Tool → Validate → Generate Fix
                                              ↓
                                        If invalid & attempts < 3 → Retry
```

---

## 📊 Technical Specifications

### Backend
- **Framework**: FastAPI
- **LLM**: Groq API (openai/gpt-oss-20b)
- **Agent Framework**: LangGraph
- **Knowledge Base**: Local filesystem (upgradeable to cloud storage)

### Frontend
- **Framework**: Streamlit
- **Features**: Multi-session chat history, admin panel, real-time streaming

### API Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/chat` | Send message & receive RCA analysis |

### Dependencies
- `langchain` & `langchain-groq`: LLM integration
- `langgraph`: Agent orchestration
- `fastapi` & `uvicorn`: Backend server
- `streamlit`: Frontend UI
- `python-dotenv`: Configuration management
- `psutil`: System diagnostics

---

## 🚀 Getting Started

### Prerequisites
1. **Groq API Key**: Get free from https://console.groq.com
2. **Python 3.8+**
3. **Git** (for deployment)

### Local Development
```bash
# Clone repository
git clone <your-repo-url>
cd rca-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r backend_requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Start backend (Terminal 1)
uvicorn backend_main:app --host 0.0.0.0 --port 8000

# Start frontend (Terminal 2)
streamlit run main.py

# Access at http://localhost:8501
```

### Render Deployment
See `DEPLOY_RENDER.md` for step-by-step instructions using `render.yaml`

---

## 📝 API Examples

### Example 1: Error Log Analysis
**Request:**
```json
{
  "message": "Error: Connection refused on localhost:9092\nException: java.net.ConnectException: Failed to connect to Kafka broker"
}
```

**Response:**
```json
{
  "response": "### 🔍 Analysis\nKafka broker is unreachable on localhost:9092...\n\n### ✅ Recommended Fix\n1. Verify Kafka is running...",
  "message_type": "error_log"
}
```

### Example 2: Simple Question
**Request:**
```json
{
  "message": "What is a timeout error?"
}
```

**Response:**
```json
{
  "response": "A timeout error occurs when a system waits too long for a response from another service or resource and gives up. This usually means the other system isn't responding fast enough or at all.",
  "message_type": "simple_question"
}
```

### Example 3: Complex Question
**Request:**
```json
{
  "message": "How do I implement circuit breaker pattern in a microservices architecture?"
}
```

**Response:**
```json
{
  "response": "## Circuit Breaker Pattern\n\n### Purpose\nPrevents cascading failures in distributed systems...\n\n### Implementation Steps\n1. Monitor service calls...\n2. Track failure rates...",
  "message_type": "complex_question"
}
```

---

## 🔧 Configuration

### Environment Variables
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=openai/gpt-oss-20b
BACKEND_URL=https://rca-chat-backend.onrender.com  # For production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_strong_password
```

### Message Type Detection Rules
| Type | Triggers | Response Style |
|------|----------|-----------------|
| `greeting` | "hello", "hi", "hey", length < 20 | Brief & friendly (1-2 sentences) |
| `error_log` | Contains error keywords OR length > 150 | Detailed RCA with fix steps |
| `simple_question` | "what is", "how to", etc., length < 50 | Concise (1-3 sentences) |
| `complex_question` | Contains "?" AND length > 50 | Comprehensive explanation |
| `general` | Default | Conversational assistance |

---

## 🛡️ Security

- ✅ CORS enabled for cross-origin requests
- ✅ Admin panel authentication (username/password)
- ✅ Groq API key stored as environment variable (never in code)
- ✅ Input validation on all endpoints
- ✅ Error messages don't leak sensitive information

### Future Enhancements
- API key authentication for rate limiting
- Role-based access control (RBAC)
- Encrypted knowledge base storage
- Audit logging for admin actions

---

## 📈 Performance & Scalability

| Metric | Value |
|--------|-------|
| API Response Time | ~5-30 seconds (depends on LLM latency) |
| Max Message Length | 10,000 characters |
| Concurrent Users | Unlimited (scales with Render plan) |
| Knowledge Base Size | Unlimited (file-based storage) |
| Message History | 50 items per session |

**Note on Scaling:**
- Free tier Render services may spin down after 15 min inactivity
- For production, upgrade to paid Render plan with persistent resources
- For large-scale deployments, migrate knowledge base to S3/cloud storage

---

## 🔄 Deployment Information

### Current Deployment
- **Backend**: Render (FastAPI service)
- **Frontend**: Render (Streamlit service)
- **Production URL**: https://rca-chat-backend.onrender.com

### Deployment Architecture
```
User Browser
     ↓
Streamlit Frontend (Render Web Service)
     ↓
FastAPI Backend (Render Web Service)
     ↓
Groq API (LLM inference)
     ↓
Knowledge Base (mounted disk or cloud storage)
```

---

## 📚 Use Cases

1. **DevOps/SRE Teams**: Rapid incident response for production errors
2. **Backend Developers**: Debug application logs and exceptions
3. **Support Engineers**: Provide technical guidance with knowledge base context
4. **System Administrators**: Diagnose system-level connectivity issues
5. **Training Programs**: Educational tool for learning troubleshooting methodology

---

## 🎓 Supported Message Types

- **Greeting**: "Hi", "Hello", "How are you?"
- **Error Analysis**: Stack traces, exception logs, system errors
- **Simple Questions**: "What is X?", "How to do Y?"
- **Complex Questions**: In-depth technical explanations
- **General Chat**: Conversational troubleshooting

---

## 📞 Support & Documentation

- **Spec Files**: 
  - `openapi.yaml` - Complete API specification
  - `ui_preferences.json` - UI configuration for marketplace
- **Deployment Guide**: `DEPLOY_RENDER.md`
- **README**: Detailed setup and usage instructions

---

## 📊 Marketplace Metadata

| Property | Value |
|----------|-------|
| **Agent Type** | Agentic Conversational AI |
| **Category** | Troubleshooting & Diagnostics |
| **Sub-categories** | Error Analysis, Log Analysis, RCA, DevOps |
| **Target Users** | DevOps, SRE, Backend Developers, System Admins |
| **Pricing Tier** | Free |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-06-08 |

---

## ✨ What Makes This an Agent?

Unlike simple chatbots, this is a true **agentic system** because it:

1. **Perceives**: Auto-detects query type and context
2. **Reasons**: Generates hypotheses and tests them
3. **Acts**: Selects and executes appropriate tools dynamically
4. **Decides**: Uses conditional logic to retry or move forward
5. **Learns**: Refines next steps based on validation results

The LangGraph workflow enables autonomous decision-making without explicit user commands for each step.

---

Generated for AI Agent Marketplace Onboarding | v1.0.0
