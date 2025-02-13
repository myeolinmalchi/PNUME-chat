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
            "name": "search_orderby_weighted_sum_notice",
                "description": "Given a question, this function retrieves relevant data from the table for the notice by conducting hybrid search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_vector": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "List of float that is embedded from user's question."
                        },
                        "query_sparse_vector": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string"},
                                    "embedding": {"type": "number"}
                                }
                            },
                            "description": "List of Dictionary with string key and float value. The dictionary is made out of user's question."                        
                        } 
                    }
                }
        },
        {
            "name": "search_orderby_weighted_sum_professor",
                "description": "Given a question, this function retrieves relevant data from the table for the professor by conducting hybrid search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": "object",
                        "properties": {
                            "query_vector": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "List of float that is embedded from user's question"
                            },
                            "query_sparse_vector": {
                                "type": "array",
                                "items":{
                                    "type": "object",
                                    "properties": {
                                        "key": {"type": "string"},
                                        "embedding": {"type": "number"}
                                    }
                                },
                                "description": "List of Dictionary with string key and float value, The dictionary is make out of user's question."
                            }
                        }
                    }
                }
        },
        {
            "name": "search_orderby_weighted_sum_support",
                "description": "Given a question, this function retrieves relevant data from the table for student support homepage by conducting hybrid search.",
                "parameter": {
                    "type": "object",
                    "properties": {
                        "query_vector": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of float that is embedded from user's question"
                        },
                        "query_sparse_vector": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string"},
                                    "embedding": {"type": "number"}
                                }
                            },
                            "description": "List of Dictionary with string key and float value, The dictionary is make out of user's quesiton."
                        }
                    }
                }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful user support assistant. Choose the supplied tool to assist the user." 
        },
        {
            "role": "user",
            "content": f"{question}"
        }
    ]

    data = {
        "model": 'gpt-4o-mini',
        "message": messages,
        "functions": tools
    }

    async def async_function_call(data: Dict) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_content = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"Open API Error: {error_content}")
                result = await response.json()
                return result.choices[0].messsage.function_call.name
        
    return await async_function_call(data=data)
    





@router.post("/chat")
@inject
async def chat(request: Request, response_model=Response):
    question = request.questionContent
    try:
        # OpenAI API에 질문을 보내고 적합한 함수를 선택
        function_name = choose_function(question=question)
        response = {
            "questionConten": question,
            "answerContent": function_name
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))