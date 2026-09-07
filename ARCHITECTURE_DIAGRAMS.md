# RCA Chat Agent - Architecture Visual Diagrams

This document contains comprehensive visual diagrams for the RCA Chat Agent system architecture, data flow, and deployment topology.

---

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph Client["🌐 Client Layer"]
        Browser["User Browser"]
        Mobile["Mobile App<br/>(Future)"]
    end

    subgraph Frontend["🎨 Frontend Layer - Streamlit"]
        Landing["Landing Page<br/>main.py"]
        Chat["Chat Interface<br/>💬_chat_interface.py"]
        Admin["Admin Panel<br/>📊_admin_panel.py"]
    end

    subgraph Backend["⚙️ Backend Layer - FastAPI"]
        Router["Request Router<br/>Message Type Detection"]
        KB["Knowledge Base<br/>Loader"]
        SystemPrompt["System Prompt<br/>Generator"]
    end

    subgraph Agent["🤖 Agent Orchestration - LangGraph"]
        Analyze["1. Analyze Logs"]
        Hypothesis["2. Generate Hypothesis"]
        ToolSelect["3. Select Tool"]
        Validate["4. Validate"]
        Fix["5. Generate Fix"]
        Decision["Decision Logic<br/>Retry or Complete"]
    end

    subgraph Tools["🔧 Diagnostic Tools"]
        PortCheck["Check Network Port"]
        APICheck["Check HTTP Endpoint"]
        FileCheck["Inspect File/Log"]
        ProcessCheck["Check System Process"]
    end

    subgraph LLM["🧠 LLM Service"]
        Groq["Groq API<br/>llama-3.1-70b"]
    end

    subgraph Storage["💾 Storage Layer"]
        KB_Dir["Knowledge Base<br/>Local/Cloud"]
        SessionState["Session State<br/>Streamlit"]
    end

    Browser --> Landing
    Mobile --> Chat
    
    Landing --> Chat
    Landing --> Admin
    
    Chat --> Router
    Admin --> Router
    
    Router --> KB
    Router --> SystemPrompt
    
    Router -->|Error Logs| Analyze
    Router -->|Other Messages| SystemPrompt
    
    Analyze --> Hypothesis
    Hypothesis --> ToolSelect
    ToolSelect --> Validate
    Validate --> Decision
    Decision -->|Invalid & Retries < 3| Hypothesis
    Decision -->|Valid or Max Retries| Fix
    Fix --> Groq
    
    Hypothesis --> Groq
    Groq --> Fix
    Groq --> SystemPrompt
    
    ToolSelect --> Tools
    Tools --> Validate
    
    KB --> KB_Dir
    SessionState --> Chat
    
    SystemPrompt --> Groq
    
    Fix --> Chat
    
    style Client fill:#e1f5ff
    style Frontend fill:#fff3e0
    style Backend fill:#f3e5f5
    style Agent fill:#e8f5e9
    style Tools fill:#ffe0b2
    style LLM fill:#c8e6c9
    style Storage fill:#b3e5fc
```

---

## 2. Request Flow Diagram (Error Log Analysis)

```mermaid
sequenceDiagram
    participant User as User Browser
    participant Frontend as Streamlit Frontend
    participant Backend as FastAPI Backend
    participant Detector as Message Detector
    participant Agent as LangGraph Agent
    participant Tools as Diagnostic Tools
    participant LLM as Groq LLM
    participant Storage as Knowledge Base

    User->>Frontend: Paste error log
    Frontend->>Backend: POST /execute {message, type}
    
    Backend->>Detector: Detect message type
    Detector->>Backend: Type = "error_log"
    
    Backend->>Agent: Invoke LangGraph workflow
    
    Agent->>LLM: Analyze error: analyze_logs()
    LLM->>Agent: Return analysis
    
    Agent->>LLM: Generate hypothesis: generate_hypothesis()
    LLM->>Agent: Return hypothesis
    
    Agent->>LLM: Choose tool: choose_tool()
    LLM->>Agent: Tool = "kafka"
    
    Agent->>Tools: Execute: check_network_port("localhost", 9092)
    Tools->>Agent: Result: false (not reachable)
    
    Agent->>Agent: Validate: is_valid = true
    
    Agent->>LLM: Generate fix: suggest_fix()
    LLM->>Agent: Return fix recommendations
    
    Agent->>Backend: Return final result
    
    Backend->>Storage: Load knowledge base context
    Storage->>Backend: Return KB content
    
    Backend->>Frontend: Return formatted response
    Frontend->>User: Display analysis with fix

```

---

## 3. Message Type Routing Flow

```mermaid
graph LR
    Input["User Input"]
    
    Input --> Detector{"Message Type<br/>Detector"}
    
    Detector -->|Contains 'hello/hi'<br/>& len < 20| Greeting["🎯 GREETING<br/>Type = greeting"]
    Detector -->|Error Keywords<br/>OR len > 150| ErrorLog["🎯 ERROR LOG<br/>Type = error_log"]
    Detector -->|'what/how' keywords<br/>& len < 50| SimpleQ["🎯 SIMPLE Q<br/>Type = simple_question"]
    Detector -->|'?' present<br/>& len > 50| ComplexQ["🎯 COMPLEX Q<br/>Type = complex_question"]
    Detector -->|Default| General["🎯 GENERAL<br/>Type = general"]
    
    Greeting --> GreetingHandler["Brief Friendly Response<br/>1-2 sentences"]
    ErrorLog --> AgentHandler["LangGraph Agent<br/>Multi-step RCA"]
    SimpleQ --> SimpleHandler["Concise Answer<br/>1-3 sentences"]
    ComplexQ --> ComplexHandler["Comprehensive Explanation<br/>Detailed & Examples"]
    General --> GeneralHandler["Conversational Response<br/>with KB Context"]
    
    GreetingHandler --> LLM["LLM Response"]
    SimpleHandler --> LLM
    GeneralHandler --> LLM
    ComplexHandler --> LLM
    AgentHandler --> LLM
    
    LLM --> User["Send to User"]
    
    style Greeting fill:#e3f2fd
    style ErrorLog fill:#ffebee
    style SimpleQ fill:#fff8e1
    style ComplexQ fill:#f3e5f5
    style General fill:#e0f2f1
    style AgentHandler fill:#c8e6c9
```

---

## 4. LangGraph Agent Workflow (Error Logs)

```mermaid
stateDiagram-v2
    [*] --> Analyze: error_log input
    
    Analyze: Analyze Error\n↓\nExtract key information\nIdentify error type
    
    Analyze --> Hypothesis: Analysis complete
    
    Hypothesis: Generate Hypothesis\n↓\nSuggest root cause\nbased on analysis
    
    Hypothesis --> ChooseTool: Hypothesis ready
    
    ChooseTool: Choose Tool\n↓\nDecide which diagnostic\ntool to use (Kafka/API/File)
    
    ChooseTool --> Validate: Tool selected
    
    Validate: Validate Hypothesis\n↓\nRun diagnostic tool\nCheck if hypothesis correct
    
    Validate --> Decision: Validation complete
    
    Decision: is_valid?\nOR attempts >= 3?
    
    Decision -->|NO & attempts < 3| Hypothesis: Retry with new hypothesis\nIncrement attempts
    
    Decision -->|YES or Max Retries| GenerateFix: Proceed to fix
    
    GenerateFix: Generate Fix\n↓\nCreate solution steps\nPrevent future issues
    
    GenerateFix --> [*]: Return structured RCA\n• Analysis\n• Hypothesis\n• Tool used\n• Fix recommendations
    
    style Analyze fill:#bbdefb
    style Hypothesis fill:#c5e1a5
    style ChooseTool fill:#ffccbc
    style Validate fill:#f0f4c3
    style Decision fill:#ffccbc
    style GenerateFix fill:#c8e6c9
```

---

## 5. Frontend Architecture (Streamlit)

```mermaid
graph TB
    subgraph Frontend["Streamlit App Structure"]
        MainPage["main.py<br/>Landing Page"]
        
        subgraph Pages["Pages/"]
            ChatPage["💬_chat_interface.py<br/>Chat & History"]
            AdminPage["📊_admin_panel.py<br/>Admin & KB"]
        end
        
        subgraph State["Session State"]
            ChatSessions["chat_sessions:<br/>Dict of conversations"]
            CurrentChat["current_chat_id:<br/>Active chat UUID"]
            Messages["messages:<br/>Array of messages"]
            AuthState["admin_authenticated:<br/>Boolean flag"]
        end
        
        subgraph Components["UI Components"]
            Sidebar["Sidebar<br/>• Chat history<br/>• New chat button<br/>• Settings"]
            ChatArea["Chat Display Area<br/>• Messages<br/>• User avatars<br/>• Markdown support"]
            InputBox["Input Box<br/>• Text textarea<br/>• Send button"]
            AuthForm["Auth Form<br/>• Username field<br/>• Password field<br/>• Login button"]
        end
    end
    
    MainPage --> ChatPage
    MainPage --> AdminPage
    
    ChatPage --> Sidebar
    ChatPage --> ChatArea
    ChatPage --> InputBox
    ChatPage --> State
    
    AdminPage --> AuthForm
    AdminPage --> AuthForm
    AdminPage --> State
    
    Sidebar --> State
    ChatArea --> State
    InputBox --> State
    
    State --> Backend["Backend API<br/>POST /execute"]
    
    style Frontend fill:#fff3e0
    style State fill:#f3e5f5
    style Components fill:#e8f5e9
```

---

## 6. Backend Architecture (FastAPI)

```mermaid
graph TB
    subgraph FastAPI["FastAPI Application"]
        
        subgraph Routes["API Routes"]
            Root["GET /<br/>API Info"]
            Health["GET /health<br/>Status Check"]
            Execute["POST /execute<br/>Chat Endpoint"]
        end
        
        subgraph Logic["Business Logic"]
            TypeDetector["get_message_type()<br/>Classify query"]
            SystemPromptGen["get_system_prompt()<br/>Generate instructions"]
            KBLoader["load_knowledge_base()<br/>Load docs"]
        end
        
        subgraph Integration["Integration Layer"]
            ErrorLogRoute["Error Log Path<br/>→ LangGraph Agent"]
            OtherRoute["Other Query Path<br/>→ Direct LLM"]
        end
        
        subgraph Response["Response Formatting"]
            RCAFormatter["Format RCA Result<br/>• Analysis<br/>• Hypothesis<br/>• Tools used<br/>• Fix steps"]
            LLMFormatter["Format LLM Result<br/>• Response content<br/>• Message type"]
        end
        
        subgraph Middleware["Middleware & Config"]
            CORS["CORS Handler<br/>Allow all origins"]
            ErrorHandler["Error Handler<br/>500 responses"]
        end
    end
    
    Routes --> Logic
    Logic --> Integration
    Integration --> ErrorLogRoute
    Integration --> OtherRoute
    
    ErrorLogRoute --> RCAFormatter
    OtherRoute --> LLMFormatter
    
    RCAFormatter --> Response["ChatResponse<br/>JSON"]
    LLMFormatter --> Response
    
    Middleware --> Routes
    
    style Routes fill:#bbdefb
    style Logic fill:#c5e1a5
    style Integration fill:#ffccbc
    style Response fill:#c8e6c9
```

---

## 7. Deployment Architecture (Render)

```mermaid
graph LR
    subgraph Internet["🌍 Internet"]
        User["User<br/>Browser"]
    end
    
    subgraph RenderEdge["Render Edge Network"]
        CDN["CDN &<br/>SSL/TLS"]
    end
    
    subgraph Services["Render Services"]
        FrontendService["🎨 Frontend Service<br/>Service: rca-chat-frontend<br/>Runtime: Python 3<br/>Framework: Streamlit<br/>Port: 8501<br/>Build: requirements.txt<br/>Start: streamlit run main.py"]
        
        BackendService["⚙️ Backend Service<br/>Service: rca-chat-backend<br/>Runtime: Python 3<br/>Framework: FastAPI<br/>Port: 8000<br/>Build: backend_requirements.txt<br/>Start: uvicorn backend_main:app"]
    end
    
    subgraph Storage["💾 Storage"]
        PersistentDisk["Persistent Disk<br/>/knowledge_base<br/>(Optional)"]
        EnvVars["Environment Variables<br/>GROQ_API_KEY<br/>ADMIN_PASSWORD<br/>ADMIN_USERNAME<br/>MODEL_NAME"]
    end
    
    subgraph External["🔗 External Services"]
        GroqAPI["Groq API<br/>LLM Inference<br/>openai/gpt-oss-20b"]
        GitHub["GitHub Repository<br/>Source Code<br/>Auto-deploy on push"]
    end
    
    User -->|HTTPS| CDN
    CDN -->|Route /| FrontendService
    CDN -->|Route /api| BackendService
    
    FrontendService -->|REST API| BackendService
    BackendService -->|HTTPS| GroqAPI
    
    FrontendService --> EnvVars
    BackendService --> EnvVars
    BackendService --> PersistentDisk
    
    GitHub -->|Webhook| FrontendService
    GitHub -->|Webhook| BackendService
    
    style Internet fill:#e1f5ff
    style RenderEdge fill:#fff3e0
    style Services fill:#f3e5f5
    style Storage fill:#b3e5fc
    style External fill:#c8e6c9
```

---

## 8. Data Flow Diagram

```mermaid
graph TB
    User["User<br/>Message"]
    
    User -->|Text Input| Frontend["Frontend<br/>Streamlit"]
    
    Frontend -->|HTTP POST<br/>/execute| Backend["Backend<br/>FastAPI"]
    
    Backend -->|Classify| TypeDetector["Message Type<br/>Detector"]
    
    TypeDetector -->|error_log| Agent["LangGraph<br/>Agent"]
    TypeDetector -->|other types| LLM["Direct LLM<br/>Call"]
    
    Backend -->|Load Files| Storage["Knowledge Base<br/>Directory"]
    Storage -->|File Content| Backend
    
    Agent -->|Step 1| LLM
    Agent -->|Step 2| LLM
    Agent -->|Step 3| Tools["Diagnostic<br/>Tools"]
    Tools -->|Tool Result| Agent
    Agent -->|Step 4| LLM
    Agent -->|Step 5| LLM
    
    LLM -->|Query| Groq["Groq API<br/>LLM Inference"]
    Groq -->|Response| LLM
    
    Agent -->|Final Output| Response["Response<br/>Formatter"]
    LLM -->|Final Output| Response
    
    Response -->|JSON| Backend
    Backend -->|HTTP 200| Frontend
    Frontend -->|Render HTML| Browser["User<br/>Browser"]
    
    Browser -->|Display| User
    
    style User fill:#e3f2fd
    style Frontend fill:#fff3e0
    style Backend fill:#f3e5f5
    style Agent fill:#e8f5e9
    style LLM fill:#c8e6c9
    style Tools fill:#ffe0b2
    style Storage fill:#b3e5fc
    style Groq fill:#c8e6c9
    style Response fill:#f8bbd0
    style Browser fill:#e3f2fd
```

---

## 9. Component Interaction Matrix

```mermaid
graph TB
    subgraph Components["Core Components"]
        Frontend
        Backend
        Agent
        LLM
        Tools
        KB
    end
    
    Frontend <-->|REST API| Backend
    Backend <-->|Invoke| Agent
    Backend <-->|Call| LLM
    Agent <-->|Call| LLM
    Agent <-->|Execute| Tools
    Backend <-->|Load| KB
    LLM <-->|Query/Response| Tools
    
    Frontend -->|Session State| Frontend
    Backend -->|Knowledge Base| KB
    Agent -->|State Machine| Agent
    
    style Frontend fill:#fff3e0
    style Backend fill:#f3e5f5
    style Agent fill:#e8f5e9
    style LLM fill:#c8e6c9
    style Tools fill:#ffe0b2
    style KB fill:#b3e5fc
```

---

## 10. Error Log Analysis Flow (Detailed)

```mermaid
graph TD
    Input["📝 Error Log Input"]
    
    Input --> Step1["<b>Step 1: Analyze</b><br/>Extract error type<br/>Identify patterns<br/>Locate stack trace"]
    
    Step1 --> Step2["<b>Step 2: Hypothesis</b><br/>Generate root cause theory<br/>Based on error patterns<br/>ML-informed suggestions"]
    
    Step2 --> Step3["<b>Step 3: Tool Selection</b><br/>Kafka? ❌<br/>API? ❌<br/>File? ✓<br/>Process? ❌"]
    
    Step3 --> Step4["<b>Step 4: Validation</b><br/>Execute: check_file(config.yaml)<br/>Result: File not found<br/>Hypothesis: VALID ✓"]
    
    Step4 --> Decision{"Validation<br/>Result?"}
    
    Decision -->|Valid| Step5["<b>Step 5: Fix</b><br/>Generate solution<br/>Provide steps<br/>Suggest prevention"]
    
    Decision -->|Invalid<br/>& Retries < 3| Step2
    
    Decision -->|Max Retries| Step5
    
    Step5 --> Output["✅ Output<br/>• Root Cause Analysis<br/>• Solution Steps<br/>• Prevention Tips"]
    
    Output --> User["👤 Send to User<br/>Formatted & Readable"]
    
    style Input fill:#ffebee
    style Step1 fill:#bbdefb
    style Step2 fill:#c5e1a5
    style Step3 fill:#ffccbc
    style Step4 fill:#f0f4c3
    style Decision fill:#ffccbc
    style Step5 fill:#c8e6c9
    style Output fill:#a5d6a7
    style User fill:#e3f2fd
```

---

## 11. Knowledge Base Integration Flow

```mermaid
graph LR
    Admin["👤 Admin User"]
    AdminPanel["📊 Admin Panel<br/>Upload UI"]
    Backend["Backend<br/>API Handler"]
    Storage["💾 Knowledge Base<br/>Directory"]
    Chat["💬 Chat<br/>Interface"]
    LLM["LLM<br/>Inference"]
    
    Admin -->|Click Upload| AdminPanel
    AdminPanel -->|Select File| AdminPanel
    AdminPanel -->|POST /upload| Backend
    Backend -->|Save File| Storage
    Backend -->|Success Response| AdminPanel
    
    Chat -->|User Question| Backend
    Backend -->|Load Files| Storage
    Storage -->|File Content| Backend
    Backend -->|Inject Context| LLM
    LLM -->|Generate Response<br/>Using KB| LLM
    LLM -->|Response| Backend
    Backend -->|Return| Chat
    Chat -->|Display to User| Chat
    
    style Admin fill:#e1f5ff
    style AdminPanel fill:#fff3e0
    style Backend fill:#f3e5f5
    style Storage fill:#b3e5fc
    style Chat fill:#fff3e0
    style LLM fill:#c8e6c9
```

---

## 12. Security Architecture

```mermaid
graph TB
    subgraph Security["🔒 Security Layers"]
        
        subgraph Network["Network Security"]
            HTTPS["HTTPS/TLS<br/>Encrypted transmission"]
            CORS["CORS Configuration<br/>Restrict origins"]
            RateLimit["Rate Limiting<br/>Prevent abuse"]
        end
        
        subgraph Auth["Authentication & Authorization"]
            APIKey["API Key Mgmt<br/>Future: Bearer tokens"]
            AdminAuth["Admin Auth<br/>Username/Password"]
            SessionMgmt["Session Management<br/>Timeouts & validation"]
        end
        
        subgraph Data["Data Protection"]
            EnvVar["Environment Variables<br/>Secrets never in code"]
            InputVal["Input Validation<br/>Sanitization"]
            FileRestrict["File Type Restrictions<br/>Only .txt/.log/.md"]
        end
        
        subgraph Monitoring["Monitoring & Logging"]
            ErrorLog["Error Logging<br/>No sensitive data leaked"]
            AuditLog["Audit Logging<br/>Track admin actions"]
            HealthCheck["Health Monitoring<br/>Service status"]
        end
    end
    
    Request["Incoming<br/>Request"]
    Request --> HTTPS
    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> APIKey
    APIKey --> AdminAuth
    AdminAuth --> SessionMgmt
    SessionMgmt --> InputVal
    InputVal --> FileRestrict
    
    HTTPS --> ErrorLog
    AdminAuth --> AuditLog
    Request --> HealthCheck
    
    style Security fill:#ffebee
    style Network fill:#ffccbc
    style Auth fill:#fff9c4
    style Data fill:#c8e6c9
    style Monitoring fill:#b3e5fc
```

---

## 13. Deployment Stages

```mermaid
graph LR
    Dev["💻 Development<br/>Local Machine<br/>localhost:8000<br/>localhost:8501"]
    
    Git["📦 Git Repository<br/>GitHub<br/>Commit & Push"]
    
    Render["🚀 Render<br/>Build Stage<br/>• Install deps<br/>• Run tests<br/>• Create image"]
    
    Deploy["📡 Deploy Stage<br/>• Start services<br/>• Mount disks<br/>• Set env vars"]
    
    Prod["✅ Production<br/>Live Services<br/>https://backend<br/>https://frontend"]
    
    Monitor["📊 Monitoring<br/>Health checks<br/>Error tracking<br/>Performance"]
    
    Dev -->|git push| Git
    Git -->|Webhook trigger| Render
    Render -->|Build success| Deploy
    Deploy -->|Services started| Prod
    Prod -->|Continuous monitoring| Monitor
    Monitor -->|Alerts| Dev
    
    style Dev fill:#e3f2fd
    style Git fill:#fff3e0
    style Render fill:#f3e5f5
    style Deploy fill:#e8f5e9
    style Prod fill:#c8e6c9
    style Monitor fill:#ffe0b2
```

---

## Quick Reference Legend

### Colors Used

| Color | Meaning |
|-------|---------|
| 🔵 Blue | User/Client Layer |
| 🟠 Orange | Frontend/UI |
| 🟣 Purple | Backend/Processing |
| 🟢 Green | AI/LLM & Agents |
| 🟡 Yellow | Logic & Decision |
| 🔴 Red | Error/Security |
| 🔵 Light Blue | Storage/Data |

### Diagram Types

| Type | Use | Files |
|------|-----|-------|
| Graph TB | System components & flow | All diagrams |
| Sequence | Message interactions | Request Flow, Data Flow |
| State | Workflow states | LangGraph Agent |
| LR Flow | Linear processes | Deployment Stages |

---

**Note**: These diagrams can be rendered in:
- GitHub (markdown with mermaid blocks)
- VS Code (mermaid extension)
- Online viewers (mermaid.live)
- Confluence, Notion, Obsidian, etc.

**Last Updated**: June 9, 2026
