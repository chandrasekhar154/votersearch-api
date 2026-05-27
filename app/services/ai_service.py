from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def buildChain():
    """
    Builds and returns a LangChain chain.
    Chain = prompt template | LLM | output parser
    This is LangChain way of composing an AI Pipeline.
    """
    
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = ChatPromptTemplate.from_messages([
        ("system","You are a MySQL expert. Generate only valid SELECT queries."),
        ("human","{prompt}")
    ])
    
    # The | operator chains: prompt → llm → parse output as string
    chain = prompt | llm | StrOutputParser()
    return chain

# Build the chain once when the module loads (not on every request)
_chain = buildChain()

def generateSQL(prompt: str) -> str:
    """
    Invokes the LangChain chain with the given prompt.
    Returns the raw SQL string from the LLM.
    """
    result = _chain.invoke({"prompt": prompt})
    return result.strip()