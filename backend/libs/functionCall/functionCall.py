from dotenv import load_dotenv
from openai import OpenAI


import os

load_dotenv()

openai_key = os.environ.get("OPENAI_KEY")

client = OpenAI(api_key=openai_key)


tools = [
  {
      "type": "function",
      "function": {
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
  },
  {
      "type": "function",
      "function": {
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
      },
  }
]


messages = [
  {
      "role": "system",
      "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."
  },
  {
      "role": "user",
      "content": "What's the content of noticement of graduation at engineering school?"
  }
]

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=messages,
  tools=tools,
)

print(completion.choices[0].message.tool_calls[0].function.name)