from libs.db.models.Notice import Notice
from libs.db.repositories.NoticeRepository import NoticeRepository
from libs.db import common
import os
from dotenv import load_dotenv

import openai

load_dotenv()

db_type = "postgresql"
user = os.environ.get("DB_USER")
pw = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
dbname = os.environ.get("DB_NAME")
openai_key = os.environ.get("OPENAI_KEY")


openai.api_key = openai_key

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.Embedding.create(
        input=text,
        model=model,
        dimensions=common.N_DIM
    )
    embedding = response['data'][0]['embedding']
    return embedding

question = "무슨 교육 관련 공지가 있었는데 뭔지 기억이 안 나"
question_vector = get_embedding(question)


class Retriever:
    def __init__(self):
        self.question = ""
        self.question_vector = []
        self.retrieved_noitces = []
        self.prompt = "다음은 게시물의 제목과 내용을 토대로 답변하세요. 질문에 대한 답변만 하고 이외의 필요없는 단어는 생성하지 마세요. 다음은 제목과 내용들입니다."
        self.repository = NoticeRepository()

    def total_similarity_retrieve(self, question:str, question_vector:list,) -> str:
        self.question = question
        self.question_vector = question_vector
        self.retireved_notices = self.repository.find_orderby_total_similarity(query_encoding= question_vector)
        for notice in self.retrieved_noitces:
            self.prompt += f"\n제목:{notice.title}\n내용:{notice.content}\n"
        self.prompt += f"\n질문:{self.question}"
        return self.prompt