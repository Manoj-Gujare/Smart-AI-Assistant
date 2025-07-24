# Smart Personal Agent

## Overview
This project is a conversational AI agent that processes user queries, understands uploaded documents (PDF/TXT), sets reminders, and maintains conversation context. The system consists of a Streamlit frontend, FastAPI backend, and a LangChain-powered AI agent.

## Architecture
```
Frontend (Streamlit)  <->  Backend (FastAPI)  <->  AI Agent (LangChain)
                                   |
                              Document Processing
                                  (RAG System)
```

## Key Features
- **Conversational AI**: Chat with an intelligent assistant
- **Document Processing**: Upload PDF/TXT files for contextual understanding
- **Session Management**: Maintains conversation context across sessions
- **Reminders**: Set reminders through natural language
- **Tracking**: MLflow integration for conversation logging

## How It Works

### 1. Session Initialization
- User starts a new session via `/start_session` endpoint
- Backend generates unique session ID
- SmartAgent instance is created with:
  - Conversation memory (last 6 messages)
  - Groq API integration (Llama 4 model)
  - Document processing flag
  - Toolset (document retrieval and reminders)

### 2. Document Processing
- User uploads PDF/TXT file through Streamlit interface
- File is sent to `/upload` endpoint
- Document processing workflow:
  - Loading
  - Splitting
  - Embedding
  - Vector storage (FAISS)

### 3. Conversation Flow
- User sends message through Streamlit interface
- Frontend sends to `/chat` endpoint with session ID
- Agent processes input:
  - Checks document availability status
  - Routes to appropriate tool:
    - `document_retrieval_tool` for document queries
    - `reminder_tool` for reminder requests
  - Response generated and returned
  - Conversation logged with MLflow

### 4. Memory Management
- Uses `ConversationBufferWindowMemory` to maintain context
- Redis integration available for persistent storage
- Session data stored in memory (server-side)

## File Structure

| File        | Purpose                                 |
|-------------|-----------------------------------------|
| `app.py`    | Streamlit frontend (UI and API calls)   |
| `main.py`   | FastAPI backend (routes and session)    |
| `agent.py`  | SmartAgent implementation               |
| `rag.py`    | Document processing module              |
| `memory.py` | Session storage management              |

## Setup Instructions

### Prerequisites
- Python 3.10+
- Groq API key
- Redis (optional for persistent storage)

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
Create `.env` file with:
```
GROQ_API_KEY=your_groq_api_key
```

### Running the Application
```bash
# Start backend
uvicorn main:app --reload --port 8000

# Start frontend (in separate terminal)
streamlit run app.py
```

## Usage Guide
- Access Streamlit UI at `http://localhost:8501`
- Start new session automatically initialized
- Upload documents via sidebar
- Chat with the assistant in main panel

Use natural language to:
- Ask about uploaded documents
- Set reminders (`"Remind me to call John at 3pm"`)
- Have general conversations

## Troubleshooting
- **Backend connection issues**: Ensure backend is running on port 8000
- **Document processing failures**: Check file format (PDF/TXT only)
- **Session errors**: Restart both frontend and backend
- **API errors**: Verify Groq API key in `.env` file

## Extending the System

### Add new tools
- Implement new functions in `agent.py`
- Register with `Tool()` class

### Enhance RAG
- Modify `rag.py` for different chunking strategies
- Try alternative embedding models

### Persistent Storage
- Enable Redis in `memory.py`
- Implement database integration

### Additional File Formats
- Add new loaders in `rag.py`

## Key Technical Components

### LangChain Agent
- Tool routing based on description
- Memory-augmented conversations
- Groq API integration

### RAG Pipeline
- Text splitting with overlap
- HuggingFace embeddings
- FAISS vector storage
- Context-aware retrieval

### MLflow Tracking
- Logs all conversations
- Tracks response quality
- Stores metadata (timestamps, session IDs)
