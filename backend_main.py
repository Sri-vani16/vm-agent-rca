from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(override=True)

app = FastAPI(title="RCA Chat API", version="1.0.0")
KB_DIR = Path("knowledge_base")
ALLOWED_KB_EXTENSIONS = {".txt", ".log", ".md"}
KB_DIR.mkdir(exist_ok=True)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY").strip(),
    model_name="llama3-8b-8192"
)

class ChatRequest(BaseModel):
    message: str = None
    query: str = None
    message_type: str = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Map 'query' to 'message' if query is provided
        if self.query and not self.message:
            self.message = self.query

class ChatResponse(BaseModel):
    response: str
    message_type: str

def load_knowledge_base():
    """Load uploaded knowledge base files from the backend service."""
    content = []
    for file_path in sorted(KB_DIR.glob("*")):
        if file_path.suffix.lower() not in ALLOWED_KB_EXTENSIONS:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            content.append(f"\n\n--- {file_path.name} ---\n{text}")
        except OSError:
            continue
    return "".join(content)

def get_message_type(text):
    """Detect message type to determine response style"""
    text_lower = text.lower()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(greeting in text_lower for greeting in greetings) and len(text) < 20:
        return "greeting"

    # Simple questions take priority over error log detection
    simple_questions = ["what is", "what are", "how to", "can you", "do you", "is it", "why is", "when is", "who is"]
    if any(q in text_lower for q in simple_questions):
        return "simple_question"

    # Only treat as error log if it looks like an actual log (multiline + keywords)
    error_log_indicators = ["traceback", "stack trace", "exception in thread", "caused by",
                            "errno", "exit code", "segmentation fault", "core dumped"]
    has_error_indicator = any(kw in text_lower for kw in error_log_indicators)
    looks_like_log = len(text) > 200 and "\n" in text
    if has_error_indicator or looks_like_log:
        return "error_log"

    if "?" in text and len(text) > 50:
        return "complex_question"

    return "general"

def get_system_prompt(message_type):
    """Get system prompt based on message type"""
    prompts = {
        "greeting": """You are a friendly RCA assistant. Respond to greetings warmly but briefly (1-2 sentences). Offer to help with error analysis or technical questions.""",
        "simple_question": """You are a helpful technical assistant. Answer the question concisely in 1-3 sentences. Be direct and practical.""",
        "complex_question": """You are a helpful technical assistant. Answer the question concisely. Be direct and practical.""",
        "error_log": """You are an expert Site Reliability Engineer performing a Root Cause Analysis. Analyze the provided log or error details and respond using exactly this format and heading order:

    RCA REPORT [No Incident ID provided]

## INCIDENT SUMMARY

    <brief description of what happened>

## TIMELINE OF EVENTS

<chronological sequence of events leading to the incident>

## ROOT CAUSE

<the primary root cause identified from the log>

## CONTRIBUTING FACTORS

<secondary factors that contributed to the issue>

## IMMEDIATE FIX

<steps to immediately resolve the issue>

## PERMANENT FIX

<long-term solution to prevent recurrence>

## DETECTION GAPS

<what monitoring or alerting was missing>

## PREVENTION

<steps to prevent this class of issue in future>

    Do not add other headings, an incident ID, or a preamble. Do not use fenced code blocks for ordinary values or one-line examples. Use a fenced code block only when a multi-line code or configuration example is necessary. Be specific and technical. Base your analysis strictly on the provided input.""",
        "general": """You are a helpful AI assistant specializing in system troubleshooting. Respond appropriately to the user's message. Keep it conversational and offer to help with technical issues."""
    }
    return prompts.get(message_type, prompts["general"])

@app.get("/")
async def root():
    return {
        "message": "RCA Chat API",
        "version": "1.0.0",
        "description": "Root Cause Analysis Chat Assistant API"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "RCA Chat API",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "knowledge_base_files": len([
            file_path for file_path in KB_DIR.glob("*")
            if file_path.suffix.lower() in ALLOWED_KB_EXTENSIONS
        ])
    }

@app.post("/execute", response_model=ChatResponse)
async def execute(request: ChatRequest):
    try:
        # Detect the message type
        message_type = request.message_type or get_message_type(request.message)
        
        # Get system prompt and load knowledge base
        system_prompt = get_system_prompt(message_type)
        system_prompt += (
            "\n\nResponse formatting: Do not wrap ordinary terms, values, or one-line examples "
            "in fenced code blocks. Use fenced code blocks only for actual multi-line code "
            "or when the user explicitly asks for code formatting."
        )
        kb_content = load_knowledge_base()
        if kb_content:
            system_prompt += f"\n\nKnowledge Base Context:\n{kb_content[:4000]}"
        
        # Call LLM
        messages = [HumanMessage(content=system_prompt + "\n\nUser message:\n" + request.message)]
        response = llm.invoke(messages)
        
        return ChatResponse(
            response=response.content,
            message_type=message_type
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
