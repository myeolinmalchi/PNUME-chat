from fastapi import FastAPI

##CORS
from starlette.middleware.cors import CORSMiddleware

##ORM(sqlalchemy)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

##data validation(pydantic)
from pydantic import BaseModel

##env
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

##CORS
origins = [
    "http://localhost:3000",
]

##CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## bind DB
## pydantic-settings.BaseSettings 써서 검증코드 추가
Base = declarative_base()

DB_USER = os.environ.get('db_user')
DB_PASSWORD = os.environ.get('db_password')
DB_HOST = os.environ.get('db_host')
DB_PORT = os.environ.get('db_port')
DB_DATABASE = os.environ.get('db_database')
SQLALCHEMY_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

engine = create_engine(SQLALCHEMY_DB_URL, echo=False)
Base.metadata.bind = engine 


##pydantic써서 requeset data로 받을 데이터형 설정
class Item(BaseModel):
    quest: str



@app.post("/question")
##원래 get api를 쓰고 query parameter에 사용자 질문 담아 보낼려고 했음. get api는 request body가 없으니깐 !!
##근데 queyr-parameter는 대게 256byte 길이 제한이 있어서 사용자의 질문이 길어질 경우 제대로 된 응답이 힘들다. (웹 브라우저 마다 다르긴 함)
##get이 아닌 post api쓰고 사용자 질문을 request body에 담아서 보내기러 함.
async def question(item: Item):
    """
#일단 비동기 처리 신경쓰지 말고 한번에 하나의 질문만 받고 답한다고 생각하고 먼저 코드 구현.
    1. client로 부터 질문을 받는다.
    2. 받은 질문을 응답 생성 모델에 집어 넣는다.
    3. 모델이 생성한 질문을 받아와서 프론트로 넘긴다. (return)
    """
    quest = item.quest
    #inference
    #return inference_result