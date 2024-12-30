from dotenv import load_dotenv
from openai import OpenAI
import asyncio
import aiohttp
import json
from typing import List, Dict
import time

import os

load_dotenv()

openai_key = os.environ.get("OPENAI_KEY")

client = OpenAI(api_key=openai_key)


tools = [
  {
    "name": "hybrid_search_ME",
          "description" : "Given a question, this function retrieves relevant documents from mechanical engineering department database by conducting hybird search.",
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
                                      "key": {"type" : "number"},
                                      "embeding" : {"type" : "number"}
                                    }
                                  },
                        "description" : "List of Dictionary with string key and float value. The dictionary is made out of user's question.",
              }
          },
      },
  },
  {
    "name": "hybrid_search_FR",
          "description" : "Given a question, this function retrieves relevant documents from french department database by conducting hybird search.",
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
                                      "key": {"type" : "number"},
                                      "embeding" : {"type" : "number"}
                                    }
                                  },
                        "description" : "List of Dictionary with string key and float value. The dictionary is made out of user's question.",
              }
          },
      },
  }
]


messages_me = [
  {
      "role": "system",
      "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."
  },
  {
      "role": "user",
      "content": "What's the content of noticement of graduation at engineering school?"
  }
]

data_me = {
    "model" : "gpt-4o-mini",
    "messages" : messages_me,
    "functions" : tools
}

messages_fr = [
  {
      "role": "system",
      "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."
  },
  {
      "role": "user",
      "content": "What's the content of noticement of graduation at libral art school?"
  }
]

data_fr = {
    "model" : "gpt-4o-mini",
    "messages" : messages_fr,
    "functions" : tools
}

async def asyncFunctionCalling(data:Dict) -> Dict:
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
            return result

async def chooseFunction(data: Dict):
    response_data1 = await asyncFunctionCalling(data = data)
    print(response_data1["choices"][0]["message"]["function_call"]["name"])
  
   
async def main_task():
    task1 = asyncio.create_task(
        chooseFunction(data_me))

    task2 = asyncio.create_task(
        chooseFunction(data_fr))

    print(f"task started at {time.strftime('%X')}")

    await task1
    await task2

    print(f"task finished at {time.strftime('%X')}")

async def main_coroutine():
    print(f"coroutine started at {time.strftime('%X')}")

    await chooseFunction(data_me)
    await chooseFunction(data_fr)

    print(f"coroutine finished at {time.strftime('%X')}")

asyncio.run(main_coroutine())
asyncio.run(main_task())