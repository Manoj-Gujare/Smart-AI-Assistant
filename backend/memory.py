from langchain_community.chat_message_histories import RedisChatMessageHistory


session_store = {}

def get_session(session_id):
    return session_store.get(session_id)

def update_session(session_id, agent):
    session_store[session_id] = agent