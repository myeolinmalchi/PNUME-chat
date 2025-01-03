from fastapi import FastAPI

##CORS
from starlette.middleware.cors import CORSMiddleware

##ORM(sqlalchemy)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

##data validation(pydantic)
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Dict


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
class DBConfig(BaseSettings):   ##pydantic data validation
    DB_USER: str = Field(env = "db_user")
    DB_PASSWORD: str = Field(env = "db_password")
    DB_HOST: str = Field(env = "db_host")
    DB_PORT: int = Field(env = "db_port")
    DB_DATABASE: str = Field(env = 'db_database')


    class Config:
        env_file = 'backend/.env'

db_config = DBConfig()
SQLALCHEMY_DB_URL = f"postgresql://{db_config.DB_USER}:{db_config.DB_PASSWORD}@{db_config.DB_HOST}:{db_config.DB_PORT}/{db_config.DB_DATABASE}"




Base = declarative_base()
engine = create_engine(SQLALCHEMY_DB_URL, echo=False)
Base.metadata.bind = engine 


##pydantic으로 Input/Output validation 
class Request(BaseModel):
    previousQuestionAnswerPairs: List[Dict[str, str]]
    questionContent: str

class Response(BaseModel):
    questionContent: str
    answerContent: str
    
    





##api 구현
##fastapi는 pydantic model로 정의된 parameter를 request body에서 찾는다. 
@app.post("/question", response_model=Response)
async def question(request: Request):
    previousContents: List = request.previousQuestionAnswerPairs ##이전 질의응답 list
    question: str = request.questionContent  ##이번에 들어온 질문 

    ##inference
    answer: str = ##여기서 추론
    
    ##response data
    response = {
        "questionContent": question,
        "answerContent": answer
    }

    return response