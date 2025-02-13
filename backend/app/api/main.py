import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
import aiohttp
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from services import notice, professor, support

class Request(BaseModel):
    questionContent: str
    
class Response(BaseModel):
    questionContent: str
    answerContent: str

router = APIRouter()

load_dotenv()

# OpenAI functioncalling 비동기 함수
async def choose_function(question: str) -> str:
    openai_key = os.environ.get("OPENAI_KEY")

    # Format for the Function Calling
    tools = [
        {
            "name": "search_orderby_weighted_sum",
                "description": "Given a question, this function retrieves relevant data from the"
        }
    ]
    




@router.post("/chat")
@inject
async def chat(
    req: Request,
    notice_service: n
)

