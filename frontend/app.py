import streamlit as st
import requests
from datetime import datetime
import time

BACKEND_URL = "http://localhost:8000"

st.title("🤖 Smart Personal Agent")

# Initialize session
if "session_id" not in st.session_state:
    try:
        response = requests.post(f"{BACKEND_URL}/start_session")
        if response.status_code == 200:
            st.session_state.session_id = response.json()["session_id"]
            st.session_state.document_processed = False
            st.success("New session started successfully!")
        else:
            st.error(f"Failed to start session: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
            st.stop()
    except requests.exceptions.ConnectionError as e:
        st.error(f"Could not connect to the backend. Please ensure the backend is running at {BACKEND_URL}. Error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while starting the session: {e}")
        st.stop()

with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT", 
        type=["pdf", "txt"],
        accept_multiple_files=False
    )
    if uploaded_file:
        with st.spinner("Processing document..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {"session_id": st.session_state.session_id}
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/upload",
                    files=files,
                    data=data
                )
                if response.status_code == 200:
                    st.session_state.document_processed = True
                    st.success("Document processed successfully!")
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Error {response.status_code}: {error_detail}")
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection error: Could not connect to backend for upload. Error: {e}")
            except Exception as e:
                st.error(f"An error occurred during file upload: {str(e)}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your personal assistant. How can I help you today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "text": prompt, 
                    "session_id": st.session_state.session_id
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["response"]
            else:
                ai_response = f"Sorry, I'm having trouble getting a response. Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}"
        except requests.exceptions.ConnectionError as e:
            ai_response = f"Sorry, I'm having trouble connecting to the backend. Please check if the backend server is running. Error: {e}"
        except Exception as e:
            ai_response = f"An unexpected error occurred: {str(e)}"
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)
        
    # Add visual indicator if document is processed
    if st.session_state.get('document_processed', False):
        st.sidebar.success("Document is available for queries")