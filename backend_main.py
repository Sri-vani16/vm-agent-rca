from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from rca_agent import run_rca
import os
from pathlib import Path

load_dotenv(override=True)

app = FastAPI(title="RCA Chat API", version="1.0.0")
KB_DIR = Path("knowledge_base")
ALLOWED_KB_EXTENSIONS = {".txt", ".log", ".md"}
KB_DIR.mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY").strip(),
    model="gpt-4o-mini",
    temperature=0.3
)

class ChatRequest(BaseModel):
    message: str = None
    query: str = None
    message_type: str = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.query and not self.message:
            self.message = self.query

class ChatResponse(BaseModel):
    response: str
    message_type: str

def load_knowledge_base():
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
    text_lower = text.lower()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(g in text_lower for g in greetings) and len(text) < 20:
        return "greeting"

    # Check for error log indicators first — before simple question check
    error_log_indicators = [
        "traceback", "stack trace", "exception in thread", "caused by",
        "errno", "exit code", "segmentation fault", "core dumped",
        "nullpointerexception", "null pointer", "error:", "exception:",
        "failed:", "warn ", "info ", "debug ", "fatal",
        "at com.", "at org.", "at java.", "at sun.",
        "internal server error", "connection refused", "timeout",
        "order not found", "shipment creation aborted"
    ]
    has_error_indicator = any(kw in text_lower for kw in error_log_indicators)
    looks_like_log = len(text) > 200
    if has_error_indicator or looks_like_log:
        return "error_log"

    simple_questions = ["what is", "what are", "how to", "can you", "do you", "is it", "why is", "when is", "who is"]
    if any(q in text_lower for q in simple_questions):
        return "simple_question"

    if "?" in text and len(text) > 50:
        return "complex_question"

    return "general"

def get_system_prompt(message_type):
    prompts = {
        "greeting": "You are a friendly RCA assistant. Respond warmly but briefly in 1-2 sentences. Offer to help with error analysis or technical questions.",
        "simple_question": "You are a helpful technical assistant. Answer concisely in 1-3 sentences. Be direct and practical.",
        "complex_question": "You are a helpful technical assistant. Answer concisely and directly.",
        "error_log": (
            "You are an RCA report generator. "
            "You MUST output ONLY the following report structure. "
            "Do NOT greet the user. Do NOT add tables. Do NOT add any text before 'RCA REPORT'. "
            "Do NOT add any sections other than the 8 listed below. "
            "Your entire response must follow this exact format:\n\n"
            "RCA REPORT [No Incident ID provided]\n\n"
            "## INCIDENT SUMMARY\n"
            "<content>\n\n"
            "## TIMELINE OF EVENTS\n"
            "<content>\n\n"
            "## ROOT CAUSE\n"
            "<content>\n\n"
            "## CONTRIBUTING FACTORS\n"
            "<content>\n\n"
            "## IMMEDIATE FIX\n"
            "<content>\n\n"
            "## PERMANENT FIX\n"
            "<content>\n\n"
            "## DETECTION GAPS\n"
            "<content>\n\n"
            "## PREVENTION\n"
            "<content>"
        ),
        "general": "You are a helpful AI assistant specializing in system troubleshooting. Keep responses conversational and helpful."
    }
    return prompts.get(message_type, prompts["general"])

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "gpt-4o-mini",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "knowledge_base_files": len([f for f in KB_DIR.glob("*") if f.suffix.lower() in ALLOWED_KB_EXTENSIONS])
    }

@app.post("/execute", response_model=ChatResponse)
async def execute(request: ChatRequest):
    try:
        message_type = request.message_type or get_message_type(request.message)

        # Route error logs through the LangGraph RCA agent
        if message_type == "error_log":
            result = run_rca(request.message)
            return ChatResponse(response=result["fix"], message_type=message_type)

        # Simple/general questions go directly to LLM
        system_prompt = get_system_prompt(message_type)
        kb_content = load_knowledge_base()
        if kb_content:
            system_prompt += f"\n\nKnowledge Base Context:\n{kb_content[:4000]}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.message)
        ]
        response = llm.invoke(messages)
        return ChatResponse(response=response.content, message_type=message_type)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge-base/upload")
async def upload_knowledge_base(files: list[UploadFile] = File(...)):
    saved = []
    for file in files:
        if not any(file.filename.endswith(ext) for ext in ALLOWED_KB_EXTENSIONS):
            continue
        content = await file.read()
        (KB_DIR / file.filename).write_bytes(content)
        saved.append(file.filename)
    return {"count": len(saved), "files": saved}

@app.get("/knowledge-base")
async def list_knowledge_base():
    files = [f.name for f in KB_DIR.glob("*") if f.suffix.lower() in ALLOWED_KB_EXTENSIONS]
    return {"files": files}

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
