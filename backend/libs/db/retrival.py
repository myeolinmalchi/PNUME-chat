from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.ext.compiler import compiles
import common
from models.Notice import Notice
from sqlalchemy.sql.expression import func, desc
from repositories.NoticeRepository import NoticeRepository as retriever

import os
from dotenv import load_dotenv

load_dotenv()

db_type = "postgresql"
user = os.environ.get("DB_USER")
pw = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
dbname = os.environ.get("DB_NAME")

# BM25 사용자 정의 함수 정의
class bm25(FunctionElement):
    name = 'bm25'

@compiles(bm25, 'postgresql')
def compile_bm25(element, compiler, **kw):
    return "bm25(%s)" % compiler.process(element.clauses, **kw)

# 세션 생성
session = common.get_session()

# 예시 데이터 삽입 (필요 시)
session.add_all([
    Notice(content="논술고사 관련 공지사항."),
    Notice(content="면접고사 관련 공지사항"),
    Notice(content="2024 학사일정 변경 공지"),
])
session.commit()

# 검색어
search_query = '논술'

# BM25 기반 검색 쿼리
results = (
    session.query(Notice, bm25(Notice.content, func.to_tsquery('korean', search_query)).label('score'))
    .filter(Notice.content.op('@@')(func.to_tsquery('korean', search_query)))
    .order_by(desc('score'))
    .limit(10)  # 상위 10개의 결과만 가져오기
    .all()
)

# 결과 출력
for document, score in results:
    print(f"ID: {document.id}, Score: {score}, Content: {document.content}")
