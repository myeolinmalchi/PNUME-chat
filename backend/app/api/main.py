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
## pydantic-settings.BaseSettings 써서 검증코드 
class DBConfig(BaseSettings):
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


##pydantic써서 requeset data로 받을 데이터형 설정
class Item(BaseModel):
    questionContents: str



@app.post("/question")
async def question(item: Item):
    """
#일단 비동기 처리 신경쓰지 말고 한번에 하나의 질문만 받고 답한다고 생각하고 먼저 코드 구현.
    1. client로 부터 질문을 받는다.
    2. 받은 질문을 응답 생성 모델에 집어 넣는다.
    3. 모델이 생성한 질문을 받아와서 프론트로 넘긴다. (return)
    """
    
    #inference
    #return inference_result