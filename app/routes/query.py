from fastapi import APIRouter, HTTPException
from app.services.ai_service import generateSQL
from app.db.database import executeQuery
from app.utils.prompt_builder import buildPrompt, cleanSQL
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import json
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Load schema
with open("app/schema/ai_schema.json") as f:
    schema = json.load(f)

@router.post("/query")
async def queryData(payload: dict):
    userPrompt = payload.get("prompt")

    if not userPrompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        # Step 1: Build prompt
        aiPrompt = buildPrompt(userPrompt, schema)

        # Step 2: Generate SQL
        sql = generateSQL(aiPrompt)
        cleanedQeury = cleanSQL(sql)
        print("Generated SQL:", cleanedQeury)

        # Step 3: Execute SQL
        result = executeQuery(cleanedQeury)

        return {
            "sql": cleanedQeury,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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