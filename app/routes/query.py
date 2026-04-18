from fastapi import APIRouter, HTTPException
from app.services.ai_service import generateSQL
from app.db.database import executeQuery
from app.utils.prompt_builder import buildPrompt, cleanSQL
import json

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