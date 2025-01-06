from dotenv import load_dotenv
import aiohttp
from typing import Dict
import os



async def choose_function(question:str) -> str:
    
    #Getting openai_key
    load_dotenv()
    openai_key = os.environ.get("OPENAI_KEY")

    #Format for the Function Calling
    tools = [
    {
        "name": "search_orderby_weighted_sum_ME",
            "description" : "Given a question, this function retrieves relevant data from the table for the department of Mechanical Engineering by conducting hybird search.",
            "parameters": {
                "type": "object",
                "properties": {
                        "query_vector": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description" : "List of float that is embedded from user's question."
                        },
                        "query_sparse_vector" : {
                            "type": "array",
                            "items": {"type": "object",
                                    "properties" : {
                                        "key": {"type" : "string"},
                                        "embeding" : {"type" : "number"}
                                        }
                                    },
                            "description" : "List of Dictionary with string key and float value. The dictionary is made out of user's question.",
                }
            },
        },
    },
    {
        "name": "search_orderby_weighted_sum_FR",
            "description" : "Given a question, this function retrieves relevant data from the table for the department of French Literature and French Language by conducting hybird search.",
            "parameters": {
                "type": "object",
                "properties": {
                        "query_vector": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description" : "List of float that is embedded from user's question."
                        },
                        "query_sparse_vector" : {
                            "type": "array",
                            "items": {"type": "object",
                                    "properties" : {
                                        "key": {"type" : "string"},
                                        "embeding" : {"type" : "number"}
                                        }
                                    },
                            "description" : "List of Dictionary with string key and float value. The dictionary is made out of user's question.",
                }
            },
        },
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
        "model" : "gpt-4o-mini",
        "messages" : messages,
        "functions" : tools
    }


    #main function
    async def async_function_calling(data:Dict) -> Dict:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers = headers, json = data) as response:
                if response.status != 200:
                    error_content = await response.text()
                    raise Exception(f"OpenAI API Error: {response.status} - {error_content}")
                result = await response.json()
                return result["choices"][0]["message"]["function_call"]["name"]
    
    

    return await async_function_calling(data)

