from fastapi import FastAPI
from app.routes.query import router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(router, prefix="/api")

@app.get("/")
def health():
    return {"status": "running"}