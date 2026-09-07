# RCA Chat Assistant

A professional  Root Cause Analysis (RCA) agent built with Streamlit, LangChain, and Groq API. Analyze error logs, troubleshoot technical issues, and get intelligent responses tailored to your query type.

## 🎯 Features

- ** User Interface**: Modern, intuitive chat UI with fixed header and scrollable message area
- **Chat History Management**: Create, switch between, and manage multiple chat sessions
- **Intelligent Response Generation**: LLM automatically detects message type and tailors response length:
  - **Greetings**: Brief, friendly responses (1-2 sentences)
  - **Error Logs**: Detailed analysis with root cause, solution, and prevention steps
  - **Simple Questions**: Concise, direct answers (1-3 sentences)
  - **Complex Questions**: Comprehensive, well-structured explanations
  - **General Messages**: Conversational, helpful responses


## 📋 Prerequisites

- Python 3.8+
- Streamlit
- LangChain
- Groq API Key
- Required Python packages (see Installation)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd rca-agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=openai/gpt-oss-20b
```

Get your Groq API key from: https://console.groq.com

### 5. Create Knowledge Base Directory
```bash
mkdir knowledge_base
```

## 📁 Project Structure

```
rca-agent/
├── main.py                 # Landing page with navigation
├── pages/
│   ├── admin.py           # Admin panel for document upload
│   └── user.py            # Main chat interface
├── rca_agent.py           # LangGraph RCA pipeline (optional)
├── knowledge_base/        # Directory for uploaded documents
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎮 Usage

### Starting the Application

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

### Navigation

1. **Landing Page** (`main.py`):
   - Welcome screen with navigation cards
   - Links to User Chat and Admin Panel

2. **User Chat** (`pages/user.py`):
   - Main chat interface
   - Type messages or paste error logs
   - View chat history in sidebar
   - Create new chat sessions

3. **Admin Panel** (`pages/admin.py`):
   - Upload documents to knowledge base
   - Manage RCA analysis documents
   - Documents are used as context for responses

### Sidebar Controls

- **☰ Hamburger Menu**: Toggle sidebar open/closed
- **💬 Chat History**: View all previous conversations
- **🆕 New Chat**: Start a fresh conversation
- **Chat Items**: Click any chat to switch between conversations


## 📚 Knowledge Base

### Adding Documents

1. Go to **Admin Panel** (`pages/admin.py`)
2. Upload `.txt`, `.log`, or `.md` files
3. Documents are stored in `knowledge_base/` directory
4. Automatically referenced in chat responses

### Supported Formats

- `.txt` - Plain text files
- `.log` - Log files
- `.md` - Markdown files

## 🎨 UI/UX Design

### Color Scheme
- **Primary**: Navy (#1a2332)
- **Accent**: Gold (#c9b99a)
- **Background**: Light Gray (#f4f6f9)
- **Text**: White (#f5f0e8) on dark, Navy on light

### Layout
- **Fixed Header**: Navy gradient header with title
- **Scrollable Chat Area**: Messages with custom scrollbar
- **Fixed Input**: Chat input at bottom
- **Collapsible Sidebar**: Chat history and navigation

## 🔧 Configuration

### Environment Variables

```env
GROQ_API_KEY=your_api_key          # Required: Groq API key
MODEL_NAME=openai/gpt-oss-20b # Optional: LLM model name
```

### Customization

Edit `pages/user.py` to customize:
- **Colors**: Modify hex values in CSS
- **Model**: Change `MODEL_NAME` in `.env`
- **Response Prompts**: Edit system prompts in `chat_response()` function
- **Message Types**: Add/modify detection logic in `get_message_type()` function

## 📝 Message Type Detection

The system automatically classifies messages:

| Type | Detection | Response Style |
|------|-----------|-----------------|
| Greeting | Contains: hi, hello, hey (< 20 chars) | Brief, friendly |
| Error Log | Contains: error, exception, failed, etc. OR (> 150 chars) | Detailed analysis |
| Simple Question | Contains: what is, how to, can you, etc. (< 50 chars) | Concise (1-3 sentences) |
| Complex Question | Contains: ? AND (> 50 chars) | Comprehensive |
| General | Default | Conversational |

## 🐛 Troubleshooting

### Sidebar Not Showing
- Click the hamburger menu (☰) button to toggle
- Check browser console for JavaScript errors
- Clear browser cache and refresh

### Chat Not Responding
- Verify Groq API key in `.env`
- Check internet connection
- Ensure `GROQ_API_KEY` is set correctly
- Check Groq API status: https://console.groq.com

### Knowledge Base Not Working
- Ensure `knowledge_base/` directory exists
- Upload documents via Admin Panel
- Supported formats: `.txt`, `.log`, `.md`
- Check file permissions

### Layout Issues
- Use modern browser (Chrome, Firefox, Safari, Edge)
- Clear browser cache
- Disable browser extensions
- Try different screen resolution

## 📦 Dependencies

```
streamlit>=1.28.0
langchain>=0.1.0
langchain-groq>=0.0.1
python-dotenv>=1.0.0
```

See `requirements.txt` for complete list.

## 🔐 Security

- **API Keys**: Never commit `.env` file to version control
- **Knowledge Base**: Keep sensitive documents in `knowledge_base/` directory
- **Session State**: Chat history stored locally in browser session
- **No Data Logging**: Responses not logged externally

## 📖 Example Queries

### Error Log Analysis
```
Paste your error log here:
[Error stack trace...]
```
Response: Detailed analysis with root cause, solution, and prevention

### Simple Question
```
What is a 404 error?
```
Response: Brief, direct explanation

### Complex Question
```
How do I optimize database queries for better performance in a high-traffic application?
```
Response: Comprehensive guide with examples


## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages in browser console
3. Check Groq API documentation: https://console.groq.com/docs
4. Open an issue in the repository

## 🚀 Future Enhancements

- [ ] Multi-language support
- [ ] Export chat history as PDF
- [ ] Advanced search in chat history
- [ ] Custom LLM model selection
- [ ] Real-time collaboration
- [ ] Voice input support
- [ ] Integration with ticketing systems
- [ ] Analytics dashboard

