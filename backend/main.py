from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.agent import SmartAgent
from backend.rag import process_document
from backend.memory import get_session, update_session
from pydantic import BaseModel
import os
import mlflow
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
mlflow.set_tracking_uri("mlflow_logs")
mlflow.set_experiment("chat_conversations")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    session_id: str

@app.post("/start_session", include_in_schema=False)
@app.post("/start_Session")
def start_session():
    session_id = str(uuid.uuid4())
    agent = SmartAgent(session_id)
    update_session(session_id, agent)
    logger.info(f"Started new session: {session_id}")
    return {"session_id": session_id}

@app.post("/upload")
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        logger.info(f"Upload request: session={session_id}, file={file.filename}")
        
        agent = get_session(session_id)
        if not agent:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ["pdf", "txt"]:
            logger.warning(f"Invalid file format: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF/TXT files are allowed"
            )
        
        temp_dir = "/tmp/uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            logger.info(f"Saved {len(content)} bytes to {file_path}")
        
        process_document(agent, file_path)
        agent.document_processed = True  # Mark document as processed
        logger.info(f"Processed document: {file.filename}")
        
        return {"message": f"Document '{file.filename}' processed successfully"}
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Document processing failed: {str(e)}"}
        )

@app.post("/chat")
def chat(message: Message):
    agent = get_session(message.session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Session not found")
    
    with mlflow.start_run():
        mlflow.log_param("session_id", message.session_id)
        mlflow.log_param("user_input", message.text)
        mlflow.log_param("timestamp", datetime.now().isoformat())
        mlflow.log_param("document_processed", agent.document_processed)
        
        response = agent.generate_response(message.text)
        
        mlflow.log_param("agent_response", response)
        mlflow.log_metric("response_length", len(response))
    
    return {"response": response}

@app.get("/health")
def health_check():
    return {"status": "healthy"}