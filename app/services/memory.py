# app/services/memory.py
from langgraph.checkpoint.memory import MemorySaver

# We import the same checkpointer that ai_service.py uses
# so clearing a session actually wipes it from LangGraph's memory
from app.services.ai_service import _checkpointer

def clearSession(session_id: str) -> None:
    """
    Clears the chat history for a session.
    Call this when the user starts a new conversation.
    """
    # MemorySaver stores threads in a plain dict — we can delete directly
    if session_id in _checkpointer.storage:
        del _checkpointer.storage[session_id]