from fastapi import FastAPI

##CORS
from starlette.middleware.cors import CORSMiddleware

##ORM(sqlalchemy)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

##data validation(pydantic)
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Dict


##for import embed module
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import embed


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
        env_file = '../../.env'

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
    
    

 ##openAI / gpt-4o-mini
 





##api 구현
##fastapi는 pydantic model로 정의된 parameter를 request body에서 찾는다. 
@app.post("/question", response_model=Response)
async def question(request: Request):
    previousContents: List = request.previousQuestionAnswerPairs ##이전 질의응답 list
    question: str = request.questionContent  ##이번에 들어온 질문 
"""
    ##1. 유사도 검색 (retreival 변수로 받기)
    ##이때 await사용 
        ##유사도 검색을 위해서 우리는 hybrid search를 사용한다. 따라서 2개의 vector를 전해야 한다. 
            ##a. sparse vector 
            ##b. dense vector
            ##즉 입력으로 들어온 question을 다음과 같이 만든다.
            
            question_vector {
                'sparse': question을 sparse vector로 변환
                'dense' : question을 dense vector로 embedding 
            }

            retrevial = question_vector를 이용한 유사도 검색.
            

    ##2. [ request에 담겨온 questionContents, 유사도 검색 결과 - retreival, 이전 대화 내역들 - previousQuestionAnswerPairs ] 이러한 것들을 gpt-4o-mini한테 넘김 
        ##여기서 function calling moudle사용
        ##이렇게 생성한 응답은 answer변수로 받는다. 
        ##libs/db/에 있음 
    ##이때도 await사용 
    
    ##3. answer을 response데이터 양식에 맞게 정제하고 담아서 front로 return  -> 이 구조는 밑에 짜놨음 / 1번 2번 하면 됨 ~_~ ㅎㅎ
"""
    ##response data
    
"""
    response = {
        "questionContent": question,
        "answerContent": answer
    }

    return response

"""

def main():
    test_string = 'hello bye hi bye'
    embed_result = embed.embed_onnx(test_string)
    print(embed_result)
    

if __name__ == '__main__':
    main()