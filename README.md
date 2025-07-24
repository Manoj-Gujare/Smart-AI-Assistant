
# 🤖 Smart Personal Agent

A conversational AI assistant with document processing capabilities, built with FastAPI, Streamlit, and LangChain.

## Features
- **Conversational AI** with memory retention
- **Document processing** for PDF and TXT files
- **Retrieval-Augmented Generation (RAG)** for document queries
- **Session management** with unique IDs
- **Reminder system** for important tasks
- **MLflow integration** for conversation logging

## Project Structure
```
smart-agent/
├── backend/
│   ├── agent.py         # AI agent core logic
│   ├── rag.py           # Document processing
│   ├── memory.py        # Session management
│   └── utils.py         # Helper functions
├── frontend/
│   └── app.py           # Streamlit UI
├── main.py              # FastAPI server
└── requirements.txt     # Dependencies
```

## System Architecture

### How It Works

#### 1. Session Initialization
- User starts application
- Frontend calls `/start_session` endpoint
- Backend creates new agent with unique session ID
- Session stored in memory store

#### 2. Document Processing
_(Diagram or code snippet placeholder)_

#### 3. Chat Interaction
```python
# Simplified agent processing
def generate_response(user_input):
    doc_status = "Document available" if document_processed else "No document"
    modified_input = f"{doc_status}\n{user_input}"
    return agent.process(modified_input)
```

#### 4. Tools

**Document Retrieval Tool:**
```python
def rag_tool(query):
    if rag_chain:
        return rag_chain.invoke({"query": query})
    return "No documents available"
```

**Reminder Tool:**
```python
def reminder_tool(reminder_text):
    reminders.append(reminder_text)
    return f"Reminder set: {reminder_text}"
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Groq API key (create at [console.groq.com](https://console.groq.com))

### 2. Installation
```bash
# Clone repository
git clone https://github.com/yourusername/smart-personal-agent.git
cd smart-personal-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env
```

### 3. Running the Application
```bash
# Start backend server
uvicorn main:app --reload --port 8000

# In separate terminal, start frontend
cd frontend
streamlit run app.py
```

## Configuration Options

| Component | Parameter           | Location   | Default                               |
|-----------|---------------------|------------|---------------------------------------|
| Agent     | Memory window size  | agent.py   | 6 messages                            |
| RAG       | Chunk size          | rag.py     | 1000 characters                       |
| RAG       | Chunk overlap       | rag.py     | 200 characters                        |
| LLM       | Model               | agent.py   | meta-llama/llama-4-scout-17b-16e-instruct |
| LLM       | Temperature         | agent.py   | 0.7                                   |

## API Endpoints

| Endpoint        | Method | Description               |
|-----------------|--------|---------------------------|
| /start_session  | POST   | Create new session        |
| /upload         | POST   | Process uploaded document |
| /chat           | POST   | Send message to agent     |
| /health         | GET    | Service health check      |

## Dependencies

- Core: FastAPI, Streamlit, LangChain
- LLM: Groq API
- Embeddings: HuggingFace Transformers
- Vector Store: FAISS
- Logging: MLflow

## Troubleshooting
```bash
# Common issues:
# 1. Backend connection failed
#    - Ensure uvicorn is running on port 8000
# 2. Document processing fails
#    - Check file is PDF/TXT and <10MB
# 3. Missing GROQ_API_KEY
#    - Verify .env file exists in root directory

# View logs:
tail -f $(find . -name '*.log')
```
This README provides:
1. Comprehensive overview of the system architecture  
2. Clear setup and installation instructions  
3. Explanation of core functionality  
4. Configuration options  
5. API documentation  
6. Troubleshooting guide  
