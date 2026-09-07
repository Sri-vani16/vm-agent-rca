# RCA Chat Agent - Implementation Guide

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [API Reference](#api-reference)
8. [Usage Examples](#usage-examples)
9. [Knowledge Base Management](#knowledge-base-management)
10. [Troubleshooting](#troubleshooting)
11. [Performance & Scaling](#performance--scaling)
12. [Security Best Practices](#security-best-practices)

---

## Overview

### What is RCA Chat Agent?

**RCA Chat Agent** is an AI-powered Root Cause Analysis system designed to intelligently analyze error logs, troubleshoot technical issues, and provide expert guidance. It combines conversational AI with agentic workflows powered by LangGraph, enabling autonomous decision-making and dynamic tool selection.

### Key Features

- ✅ **Intelligent Message Routing**: Auto-detects query type and tailors responses
- ✅ **Error Log Expertise**: Deep RCA analysis with structured output
- ✅ **Agentic Workflow**: Multi-step reasoning with hypothesis validation
- ✅ **Dynamic Tool Selection**: Autonomous choice of diagnostic tools
- ✅ **Knowledge Base Integration**: Context-aware responses from uploaded documents
- ✅ **Conversational Interface**: Natural language chat with multi-session history
- ✅ **Production-Ready**: Deployed on Render with health monitoring

### Use Cases

| Use Case | Description | Example |
|----------|-------------|---------|
| **Incident Response** | Rapid RCA for production errors | "Connection timeout to Kafka broker on port 9092" |
| **Technical Support** | Help desk support with knowledge base | FAQ-based answers with custom documentation |
| **System Diagnostics** | Troubleshoot connectivity and process issues | "API returning 500 errors" |
| **Developer Assistance** | Debug application errors and exceptions | Stack trace analysis with fix recommendations |
| **Training & Education** | Learn troubleshooting methodology | Complex technical explanations with examples |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER BROWSER                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          FRONTEND (Streamlit Web App)                            │
│  - Chat Interface (pages/💬_chat_interface.py)                  │
│  - Admin Panel (pages/📊_admin_panel.py)                        │
│  - Landing Page (main.py)                                        │
│  - Session Management & Chat History                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│        BACKEND API (FastAPI Server)                              │
│  - Route Detection & Dispatching                                │
│  - Knowledge Base Loading                                        │
│  - Message Type Classification                                   │
│  - Integration Layer                                             │
└────────────────────────────┬────────────────────────────────────┘
                    ┌────────┴────────┐
                    │                 │
           (for error logs)   (for other queries)
                    │                 │
                    ▼                 ▼
        ┌──────────────────┐  ┌──────────────────┐
        │  LangGraph Agent │  │  Direct LLM Call │
        │  Workflow        │  │  with KB Context │
        │                  │  │                  │
        │ 1. Analyze       │  │  System Prompts: │
        │ 2. Hypothesize   │  │  - Greeting      │
        │ 3. Choose Tool   │  │  - Simple Q&A    │
        │ 4. Validate      │  │  - Complex Q&A   │
        │ 5. Generate Fix  │  │  - General Chat  │
        └────────┬─────────┘  └────────┬─────────┘
                 │                     │
                 └──────────┬──────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  Groq API (LLM Inference)            │
        │  Model: openai/gpt-oss-20b      │
        └──────────────────────────────────────┘
```

### Component Breakdown

#### Frontend Layer
- **main.py**: Landing page with navigation
- **pages/💬_chat_interface.py**: Multi-session chat interface
- **pages/📊_admin_panel.py**: Knowledge base management and authentication
- **State Management**: Streamlit session state for chat history

#### Backend Layer
- **backend_main.py**: FastAPI server with routing logic
- **rca_agent.py**: LangGraph workflow orchestration
- **tools.py**: Dynamic tool registry for diagnostics

#### External Dependencies
- **Groq API**: LLM inference (fast, cost-effective)
- **LangChain**: LLM integration and message handling
- **LangGraph**: Agentic workflow orchestration

#### Data Storage
- **Knowledge Base**: Local filesystem (mounted disk on Render)
- **Chat History**: Streamlit session state (ephemeral)

---

## Prerequisites

### System Requirements

- **Python Version**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB RAM minimum (1GB recommended)
- **Disk Space**: 1GB for dependencies + logs
- **Network**: Outbound HTTPS for Groq API calls

### Required Services & Accounts

1. **Groq API Account**
   - Get free API key: https://console.groq.com
   - Create account and generate API key
   - Keep key secure (never commit to Git)

2. **Version Control**
   - Git installed locally
   - GitHub/GitLab/Bitbucket account for repository hosting

3. **Deployment Platform** (for production)
   - Render.com account (recommended, free tier available)
   - Or any platform supporting Python web services (Heroku, Railway, etc.)

### Local Development Tools

```bash
# Required
python3 --version      # 3.8+
pip --version          # Package manager
git --version          # Version control

# Optional but recommended
virtualenv             # Environment isolation
uvicorn --version      # ASGI server (auto-installed)
streamlit --version    # Frontend (auto-installed)
```

---

## Installation & Setup

### Step 1: Clone Repository

```bash
# Clone from GitHub (replace with your repo URL)
git clone https://github.com/yourusername/rca-agent.git
cd rca-agent

# Verify project structure
ls -la
# Expected:
# backend_main.py
# backend_requirements.txt
# rca_agent.py
# requirements.txt
# tools.py
# pages/
# openapi.yaml
# ui_preferences.json
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python     # Linux/macOS
where python     # Windows
```

### Step 3: Install Dependencies

```bash
# Install all dependencies
pip install --upgrade pip

# Install backend dependencies
pip install -r backend_requirements.txt

# Install frontend dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|streamlit|langchain|langgraph|groq"
```

### Step 4: Create Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env    # or use your preferred editor

# Required variables:
# GROQ_API_KEY=your_actual_groq_api_key_here
# MODEL_NAME=openai/gpt-oss-20b
```

### Step 5: Create Knowledge Base Directory

```bash
# Create knowledge base directory
mkdir -p knowledge_base

# Optionally add sample documentation
echo "Sample documentation for testing" > knowledge_base/sample.md
```

### Step 6: Test Local Setup

```bash
# Terminal 1: Start backend server
uvicorn backend_main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend (in new terminal, venv activated)
streamlit run main.py --server.port 8501

# Open browser to http://localhost:8501
# You should see the landing page with navigation options
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# ============================================
# GROQ API Configuration (REQUIRED)
# ============================================
GROQ_API_KEY=your_groq_api_key_from_console.groq.com
MODEL_NAME=openai/gpt-oss-20b

# ============================================
# Backend Configuration
# ============================================
# For local development:
BACKEND_URL=http://localhost:8000

# For production (Render):
# BACKEND_URL=https://rca-chat-backend.onrender.com

# ============================================
# Frontend Configuration
# ============================================
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=false

# ============================================
# Admin Panel Configuration
# ============================================
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_strong_password_here

# ============================================
# Optional: LLM Settings
# ============================================
# Temperature controls response randomness (0.0-1.0)
# LLM_TEMPERATURE=0.7

# Max tokens per response
# LLM_MAX_TOKENS=2048
```

### Message Type Detection Configuration

The backend automatically classifies incoming messages. You can customize detection rules:

**Current Rules** (in `backend_main.py` `get_message_type()` function):

| Type | Triggers | Response Style |
|------|----------|-----------------|
| `greeting` | Contains "hello", "hi", "hey" AND length < 20 | Brief & friendly |
| `error_log` | Contains error keywords OR length > 150 | Detailed RCA analysis |
| `simple_question` | Contains "what is", "how to", etc. AND length < 50 | Concise (1-3 sentences) |
| `complex_question` | Contains "?" AND length > 50 | Comprehensive explanation |
| `general` | Default | Conversational assistance |

**Error Keywords Triggering Analysis:**
- error, exception, failed, traceback, stack trace
- connection refused, timeout, null pointer
- (Add more to `error_keywords` list in code)

### Customizing System Prompts

Edit `backend_main.py` `get_system_prompt()` function:

```python
def get_system_prompt(message_type):
    prompts = {
        "greeting": "Your custom greeting prompt here...",
        "simple_question": "Your custom simple Q&A prompt...",
        "complex_question": "Your custom expert explanation prompt...",
        "general": "Your custom general chat prompt..."
    }
    return prompts.get(message_type, prompts["general"])
```

---

## Deployment

### Deployment Architecture

The RCA Chat Agent is designed to run on Render.com using two separate services:

1. **Backend Service** (FastAPI)
   - Runtime: Python 3
   - Framework: FastAPI/Uvicorn
   - Port: 8000

2. **Frontend Service** (Streamlit)
   - Runtime: Python 3
   - Framework: Streamlit
   - Port: 8501

### Render Deployment Steps

#### Step 1: Prepare Repository

```bash
# Ensure all files are committed
git status

# Add and commit changes
git add .
git commit -m "Prepare for Render deployment"

# Push to GitHub (replace main with your branch)
git push origin main

# Verify .env is in .gitignore (DO NOT COMMIT SECRETS)
cat .gitignore | grep .env
```

#### Step 2: Deploy via Blueprint

1. **Open Render Dashboard**
   - Go to https://render.com
   - Sign in to your account

2. **Create Blueprint**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render auto-detects `render.yaml`

3. **Configure Environment Variables**
   - When prompted, enter:
     - `GROQ_API_KEY`: Your Groq API key
     - `ADMIN_PASSWORD`: Strong password for admin panel
   - Keep defaults for:
     - `MODEL_NAME`: openai/gpt-oss-20b
     - `ADMIN_USERNAME`: admin
     - `BACKEND_URL`: Will be auto-set by Render

4. **Deploy**
   - Click "Create Resources"
   - Render will create both services
   - Wait 3-5 minutes for deployment

#### Step 3: Verify Deployment

```bash
# Test health endpoint
curl https://rca-chat-backend.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "RCA Chat API",
#   "groq_configured": true,
#   "knowledge_base_files": 0
# }

# Open frontend in browser
# https://rca-chat-frontend.onrender.com
```

#### Step 4: Post-Deployment Testing

1. **Test Greeting**
   - In chat: "Hello!"
   - Expect: Friendly greeting response

2. **Test Error Analysis**
   - In chat: Paste a sample error log
   - Expect: Detailed RCA with hypothesis and fix

3. **Test Admin Panel**
   - Go to Admin Panel
   - Login: admin / your_password
   - Upload a `.txt` or `.md` file
   - In chat, ask a question related to uploaded file
   - Expect: Response includes knowledge base context

### Troubleshooting Deployment

| Issue | Cause | Solution |
|-------|-------|----------|
| `502 Bad Gateway` | Backend crashed | Check build logs in Render dashboard |
| `GROQ_API_KEY not found` | Missing env var | Add `GROQ_API_KEY` in Render environment |
| `socket-client error` | Invalid package in requirements | Use provided `backend_requirements.txt` |
| `/execute endpoint 404` | Endpoint mismatch | Ensure endpoint is `/execute` not `/chat` |
| `Knowledge base not persisting` | Render ephemeral filesystem | Attach persistent disk or use cloud storage |

---

## API Reference

### Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://rca-chat-backend.onrender.com`

### Endpoints

#### 1. GET `/`
**Description**: API information and metadata

**Response**:
```json
{
  "message": "RCA Chat API",
  "version": "1.0.0",
  "description": "Root Cause Analysis Chat Assistant API"
}
```

#### 2. GET `/health`
**Description**: Health check and service status

**Response**:
```json
{
  "status": "healthy",
  "service": "RCA Chat API",
  "groq_configured": true,
  "knowledge_base_files": 3
}
```

#### 3. POST `/execute`
**Description**: Send message and receive RCA analysis

**Request**:
```json
{
  "message": "Error: Connection refused on localhost:9092",
  "message_type": "error_log"  // optional
}
```

**Response**:
```json
{
  "response": "### 🔍 Analysis\nKafka broker is unreachable...\n\n### ✅ Recommended Fix\n1. Check broker status...",
  "message_type": "error_log"
}
```

**Message Types**:
- `greeting`: Brief, friendly response
- `error_log`: Detailed RCA with fix recommendations
- `simple_question`: Concise answer (1-3 sentences)
- `complex_question`: Comprehensive explanation
- `general`: Conversational response (auto-detected)

---

## Usage Examples

### Example 1: Error Log Analysis

**Input:**
```
Error: Connection timeout to MongoDB
Exception: MongoNetworkError: connect ECONNREFUSED 127.0.0.1:27017
Stack trace:
  at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:14)
```

**API Call:**
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Error: Connection timeout to MongoDB\nException: MongoNetworkError: connect ECONNREFUSED 127.0.0.1:27017\nStack trace:\n  at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:14)"
  }'
```

**Response:**
```json
{
  "response": "### 🔍 Analysis\nMongoDB connection refused on localhost:27017. Server is either not running or not listening on the expected port.\n\n### 💡 Validated Hypothesis\nMongoDB process crashed or failed to start due to configuration issues.\n\n### 🛠️ Diagnostics Performed\nUsed tool `check_network_port` with parameters: {\"host\": \"127.0.0.1\", \"port\": 27017}\n\n### ✅ Recommended Fix\n1. Check MongoDB status: `systemctl status mongod`\n2. Check logs: `tail -f /var/log/mongodb/mongod.log`\n3. Restart MongoDB: `systemctl restart mongod`\n4. Verify connection: `mongo --eval 'db.adminCommand(\"ping\")'`\n5. Check firewall: `sudo ufw status`",
  "message_type": "error_log"
}
```

### Example 2: Simple Question

**Input:**
```
What is a timeout error?
```

**Response:**
```json
{
  "response": "A timeout error occurs when a system waits too long for a response from another service or resource and gives up. This usually means the other system isn't responding fast enough or at all.",
  "message_type": "simple_question"
}
```

### Example 3: Complex Question

**Input:**
```
How do I implement circuit breaker pattern in a distributed microservices architecture to prevent cascading failures?
```

**Response:**
```json
{
  "response": "## Circuit Breaker Pattern\n\n### Purpose\nPrevents cascading failures by stopping requests to failing services.\n\n### States\n1. **Closed**: Normal operation, requests pass through\n2. **Open**: Too many failures detected, block requests immediately\n3. **Half-Open**: Test if service recovered\n\n### Implementation (Node.js example):\n```javascript\nclass CircuitBreaker {\n  constructor(fn, options = {}) {\n    this.fn = fn;\n    this.failureThreshold = options.threshold || 5;\n    this.resetTimeout = options.timeout || 60000;\n    this.state = 'CLOSED';\n    this.failureCount = 0;\n  }\n  // ...\n}\n```\n\n### Best Practices\n1. Set appropriate thresholds\n2. Monitor circuit breaker state\n3. Implement fallback strategies\n4. Use exponential backoff",
  "message_type": "complex_question"
}
```

---

## Knowledge Base Management

### Uploading Documents

1. **Via Admin Panel** (Recommended for users)
   - Open Admin Panel from landing page
   - Login with admin credentials
   - Click "Upload Document"
   - Select `.txt`, `.log`, or `.md` file
   - File saved to `knowledge_base/` directory

2. **Programmatically** (For automation)
   ```bash
   # Copy file to knowledge_base directory
   cp my_documentation.md knowledge_base/
   
   # On Render, attach persistent disk at /knowledge_base
   # Or implement S3/cloud storage integration
   ```

### Supported File Formats

| Format | Extensions | Use Case |
|--------|-----------|----------|
| Markdown | `.md` | Documentation, guides |
| Text | `.txt` | Configuration files, logs |
| Logs | `.log` | Application logs, system logs |

### Knowledge Base Context Integration

When answering questions, the backend:
1. Loads all files from `knowledge_base/` directory
2. Concatenates content (first 4000 chars)
3. Includes as context in system prompt
4. LLM uses context to provide informed answers

### Best Practices

- **Organization**: Use clear filenames (e.g., `api-documentation.md`)
- **Size**: Keep individual files < 1MB for performance
- **Content**: Use markdown formatting for better context parsing
- **Updates**: Delete old versions before uploading new ones

### Data Persistence Note

**Important**: On Render's free tier, files are lost on redeploy!

**Solutions for production**:
1. **Render Persistent Disk**
   - Attach disk to backend service
   - Mount at `/knowledge_base`
   - Persists across redeployments

2. **Cloud Storage** (S3, Supabase, etc.)
   - Modify `backend_main.py` to use cloud SDK
   - More scalable for large deployments

---

## Troubleshooting

### Common Issues

#### 1. GROQ_API_KEY Not Found

**Error:**
```
langchain_groq.exceptions.APIError: Invalid API key
```

**Solutions**:
- Verify `.env` file exists and has valid key
- Restart backend: `Ctrl+C` then `uvicorn backend_main:app --reload`
- On Render: Check environment variables in dashboard
- Generate new key: https://console.groq.com

#### 2. Connection Refused to Backend

**Error:**
```
Error connecting to backend: 404 Client Error: Not Found
```

**Solutions**:
- Verify backend is running: `http://localhost:8000/health`
- Check port 8000 is not in use: `lsof -i :8000`
- Verify `BACKEND_URL` environment variable
- On Render: Check backend service logs

#### 3. Message Type Not Detected

**Issue**: Wrong response type (e.g., error logs treated as greetings)

**Solution**:
- Adjust detection thresholds in `get_message_type()`
- Explicitly specify `message_type` in request:
  ```json
  {
    "message": "Your error log here",
    "message_type": "error_log"
  }
  ```

#### 4. Knowledge Base Files Not Loading

**Issue**: Uploaded files not included in responses

**Solution**:
- Verify files in `knowledge_base/` directory
- Check file permissions: `ls -la knowledge_base/`
- Verify supported format: `.txt`, `.log`, `.md`
- Check file size (< 10MB recommended)

### Debug Mode

Enable verbose logging:

```python
# In backend_main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log requests
@app.post("/execute")
async def chat(request: ChatRequest):
    logger.debug(f"Received message: {request.message}")
    logger.debug(f"Message type: {message_type}")
    # ... rest of function
```

### Performance Monitoring

```bash
# Monitor backend resource usage
watch -n 1 'curl -s http://localhost:8000/health | jq .'

# Check response time
time curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# View Streamlit logs
# They're printed to terminal running streamlit
```

---

## Performance & Scaling

### Response Times

| Message Type | Typical Time | Factors |
|--------------|-------------|---------|
| Greeting | 2-3 seconds | LLM inference only |
| Simple Question | 3-5 seconds | LLM inference + KB search |
| Error Log (no KB) | 10-20 seconds | LLM analysis + validation |
| Error Log (with KB) | 15-30 seconds | Multiple LLM calls + tools |

### Optimization Tips

1. **Reduce Knowledge Base Size**
   - Delete unused documents
   - Limit context to 4000 chars (edit `load_knowledge_base()`)

2. **Cache Responses**
   - Implement Redis for frequently asked questions
   - Cache knowledge base content

3. **Load Balancing**
   - Run multiple backend instances on Render
   - Frontend automatically distributes requests

4. **Database Integration** (Future)
   - Store knowledge base in database instead of files
   - Implement full-text search for faster retrieval

### Scaling Architecture

**For increased load**:

```
                    ┌─────────────────────┐
                    │  Load Balancer      │
                    └──┬──────────────┬───┘
                       │              │
          ┌────────────┴──┐      ┌────┴──────────────┐
          │                │      │                   │
    ┌─────▼─────┐   ┌──────▼──┐  ┌──────────────┐  ┌────▼─────┐
    │Backend #1 │   │Backend#2│  │Backend #3    │  │Backend #4│
    └─────┬─────┘   └──────┬──┘  └──────┬───────┘  └────┬─────┘
          │              │              │              │
          └──────────────┼──────────────┼──────────────┘
                         │
                    ┌────▼─────┐
                    │Shared KB  │
                    │(S3/Cloud) │
                    └───────────┘
```

---

## Security Best Practices

### API Security

1. **API Key Protection**
   - Never commit `.env` to Git
   - Use `.gitignore` to exclude secrets
   - Rotate keys regularly

2. **Input Validation**
   - Message length limit: 10,000 characters
   - File type restrictions: `.txt`, `.log`, `.md` only
   - Sanitize user input

3. **CORS Configuration**
   - Currently allows all origins (for development)
   - For production, restrict:
     ```python
     CORSMiddleware(
         allow_origins=["https://yourdomain.com"],
         allow_methods=["POST"],
         allow_headers=["Content-Type"],
     )
     ```

### Admin Panel Security

1. **Authentication**
   - Username/password required for admin panel
   - Change default password in production
   - Implement session timeouts

2. **File Uploads**
   - Only allow specific file types
   - Scan files for malware
   - Implement file size limits

3. **Access Control**
   - Log admin actions
   - Implement role-based access
   - Monitor for unauthorized access

### Deployment Security

1. **Environment Variables**
   - Use Render's secure environment variable storage
   - Never log sensitive values
   - Rotate credentials regularly

2. **Network Security**
   - Use HTTPS (auto-enabled on Render)
   - Configure firewall rules
   - Monitor for DDoS attacks

3. **Data Privacy**
   - Don't store user messages long-term
   - Implement data retention policies
   - Comply with GDPR/privacy regulations

---

## Appendix: Quick Reference

### Common Commands

```bash
# Development
uvicorn backend_main:app --reload --port 8000
streamlit run main.py --server.port 8501

# Testing
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'

# Git
git add .
git commit -m "Your message"
git push origin main

# Environment
source venv/bin/activate          # Activate venv
pip install -r backend_requirements.txt
pip list
```

### File Structure

```
rca-agent/
├── backend_main.py              # FastAPI backend
├── backend_requirements.txt      # Backend dependencies
├── rca_agent.py                 # LangGraph workflow
├── tools.py                     # Diagnostic tools
├── main.py                      # Streamlit landing page
├── requirements.txt             # Frontend dependencies
├── pages/
│   ├── 💬_chat_interface.py    # Chat UI
│   └── 📊_admin_panel.py        # Admin panel
├── knowledge_base/              # Document storage
├── .env                         # Secrets (not in Git)
├── .env.example                 # Template
├── openapi.yaml                 # API specification
├── ui_preferences.json          # UI configuration
├── render.yaml                  # Render deployment config
├── DEPLOY_RENDER.md             # Deployment guide
└── README.md                    # Project README
```

### Support & Resources

- **Groq Documentation**: https://console.groq.com/docs
- **LangChain Docs**: https://python.langchain.com
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Streamlit Docs**: https://docs.streamlit.io
- **Render Docs**: https://render.com/docs

---

**Document Version**: 1.0.0  
**Last Updated**: June 9, 2026  
**Compatibility**: RCA Chat Agent v1.0.0
