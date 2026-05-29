import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.db.database import executeQuery

load_dotenv()

# MemorySaver stores chat history per thread_id automatically
# This replaces our manual memory.py completely
_checkpointer = MemorySaver()

def buildAgent():
    """
    Builds a LangGraph ReAct agent.
    - create_react_agent replaces create_tool_calling_agent + AgentExecutor
    - MemorySaver handles chat history automatically via thread_id
    - The agent can call executeQuery, see results/errors, and retry
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True
    )

    agent = create_react_agent(
        model=llm,
        tools=[executeQuery],
        checkpointer=_checkpointer,   # plugs in memory automatically
        prompt="""You are a MySQL expert for a voter registration database.

            Rules:
            - Generate only SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or ALTER.
            - Always add LIMIT 500 unless the user specifies a different count.
            - If your query returns a SQL Error, fix it and try again.
            - After getting results, summarise them in a clear readable format."""
        )

    return agent

# Build once when server starts
_agent = buildAgent()


def runAgent(userPrompt: str, schema: dict, session_id: str) -> str:
    """
    Runs the agent and returns the full response as a string.
    session_id maps to thread_id — LangGraph uses this to recall history.
    """
    schemaText = "\n".join(
        f"Table: {table}, Columns: {', '.join(columns)}"
        for table, columns in schema.items()
    )

    fullPrompt = f"""Database schema:
        {schemaText}

        User request: {userPrompt}"""

    config = {"configurable": {"thread_id": session_id}}

    result = _agent.invoke(
        {"messages": [HumanMessage(content=fullPrompt)]},
        config=config
    )

    # LangGraph returns all messages — the last one is the agent's final answer
    return result["messages"][-1].content


async def streamAgent(userPrompt: str, schema: dict, session_id: str):
    """
    Streams the agent response token by token.
    Yields plain string chunks — query.py wraps them in SSE format.
    """
    schemaText = "\n".join(
        f"Table: {table}, Columns: {', '.join(columns)}"
        for table, columns in schema.items()
    )

    fullPrompt = f"""Database schema:
        {schemaText}

        User request: {userPrompt}"""

    config = {"configurable": {"thread_id": session_id}}

    async for event in _agent.astream_events(
        {"messages": [HumanMessage(content=fullPrompt)]},
        config=config,
        version="v2"
    ):
        kind = event["event"]

        # Stream LLM text tokens as they arrive
        if kind == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token:
                yield token

        # Let the frontend know when the agent is running SQL
        elif kind == "on_tool_start":
            yield "\n[Executing SQL...]\n"

        # Let the frontend know if the agent is retrying after an error
        elif kind == "on_tool_end":
            output = event["data"].get("output", "")
            if "SQL Error" in str(output):
                yield "\n[Error found, retrying...]\n"