from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.ai_service import runAgent, streamAgent
from app.services.sql_safety import validateSQL
from app.db.database import executeQuery, fetchSchema
from app.utils.prompt_builder import buildPrompt, cleanSQL
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import json
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Load schema
with open("app/schema/ai_schema.json") as f:
    schema = json.load(f)
    
# Fetch schema once when the server starts — cached in this module
# If you add a new table/column to your DB, just restart the server
_dynamicSchema = fetchSchema()

class QueryRequest(BaseModel):
    prompt: str
    session_id: str | None = None
    
@router.post("/voterResponse")
async def queryData(body: QueryRequest):
    session_id = body.session_id or str(uuid.uuid4())

    try:
        response = runAgent(body.prompt, _dynamicSchema, session_id)

        return {
            "session_id": session_id,
            "response": response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/query/stream")
async def streamQuery(body: QueryRequest):
    session_id = body.session_id or str(uuid.uuid4())

    async def eventGenerator():
        # Send session_id first so frontend can store it
        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

        try:
            async for chunk in streamAgent(body.prompt, _dynamicSchema, session_id):
                yield f"data: {json.dumps({'type': 'token', 'value': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        eventGenerator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

# @router.post("/voterResponse")
# async def voterResponse(body: QueryRequest):
#     if not body.prompt:
#         raise HTTPException(status_code=400, detail="Prompt is required")

#     try:
#         # Step 1: Build prompt with live schema
#         aiPrompt = buildPrompt(body.prompt, _dynamicSchema)
        
#         # Step 2: Generate SQL via LangChain
#         rawSQL = generateSQL(aiPrompt)
#         cleanedSQL = cleanSQL(rawSQL)
        
#         print("cleanedSQL==>", cleanedSQL)
        
#         # Step 3: Validate SQL safety
#         safeSQL = validateSQL(cleanedSQL)
#         print("safeSQL-->", safeSQL)
        
#         # Step 4: Execute
#         result = executeQuery(safeSQL)
        
#         return {
#             "sql": safeSQL,
#             "data": result
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/query")
# async def queryData(payload: dict):
#     userPrompt = payload.get("prompt")

#     if not userPrompt:
#         raise HTTPException(status_code=400, detail="Prompt is required")

#     try:
#         # Step 1: Build prompt
#         aiPrompt = buildPrompt(userPrompt, schema)

#         # Step 2: Generate SQL
#         sql = generateSQL(aiPrompt)
#         cleanedQeury = cleanSQL(sql)
#         print("Generated SQL:", cleanedQeury)

#         # Step 3: Execute SQL
#         result = executeQuery(cleanedQeury)

#         return {
#             "sql": cleanedQeury,
#             "data": result
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/practiceOneConnection")
async def practiceOneConnection(payload: dict):
    userPrompt = payload.get("prompt")
    
    if not userPrompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)
        
        response = llm.invoke([HumanMessage(userPrompt)])
        
        return {
            "result" : response.content 
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/practiceTwoChatHistory")
async def practiceOnLangChain(payload: dict):
    userPrompt = payload.get("prompt")

    if not userPrompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:

        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)
    
        chat_history = []
        
        def chat(user_input):
            chat_history.append(HumanMessage(content=user_input))
            response = llm.invoke(chat_history)
            chat_history.append(AIMessage(content=response.content))
            return response.content
        
        print(chat("Hi! my name is Chandrasekhar"))
        print(chat("What is my Name..?"))
        
        return {
            "chat_history" : chat_history
            # "response" : chat(userPrompt)
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/practiceThreeCreateAgent")
async def practiceThreeCreateAgent(payload: dict):
    userPrompt = payload.get("prompt")
    
    if not userPrompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        
        def getWeather(city: str) -> str:
            """Get weather for a given city."""
            return f"It's always sunny in {city}!"
            
        agent = create_agent(model="openai:gpt-4.1-mini", tools=[getWeather], system_prompt="You are a helpful assistant")
        
        result = agent.invoke(
            {"messages": [{"role": "user", "content": userPrompt}]}
        )
        
        finalResult = result["messages"][-1].content_blocks
        
        return {
            "response": finalResult
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/practiceFourStreamExampleOne")
async def practiceFourStreamExampleOne():
    try:
        print("Bot: ", end="", flush=True)
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)
        
        fullReply = ""
        
        for chunk in llm.stream([HumanMessage(content="Hi! Tell me a 3-line poem on Python")]):
            print(chunk.content, end="", flush=True)
            fullReply += chunk.content
            
        print()
        
        return {
            "response" : fullReply
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/practiceFiveLangChain")
async def practiceFiveLangChain(payload: dict):
    userPrompt = payload.get("prompt")
    try:
        print("Started..")
        
        schema = fetchSchema()
        buildAPrompt = buildPrompt(userPrompt, schema)
        
        return {
            "fetchSchema": schema,
            "buildPrompt": buildAPrompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))