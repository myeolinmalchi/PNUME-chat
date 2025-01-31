import json
from typing import List

from openai.types.chat import ChatCompletionToolParam
from services.support import create_support_service
from services.notice import create_notice_service

from openai import OpenAI

from config.logger import _logger

logger = _logger(__name__)

client = OpenAI()

TOOLS: List[ChatCompletionToolParam] = [{
    "type": "function",
    "function": {
        "name": "search_supports",
        "description": "'학생지원시스템'에서 학적, 교육과정, 수업, 성적, 장학, 등록, 졸업, 학생교류, 대학생활, 학생역량 등 학교 생활 전반에 대한 정보를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "유사도 검색을 위한 텍스트 입력값. '학생지원시스템'에서 관련 정보를 검색할 때, 이 값과 가장 유사한 데이터를 찾습니다."
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": False
    }
}, {
    "type": "function",
    "function": {
        "name": "search_notices",
        "description": "공지사항에서 수업, 과제, 공모전, 학과별 공지 등 학과 운영과 직접적으로 연관된 정보를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "유사도 검색을 위한 텍스트 입력값. 학과별 공지사항에서 관련 정보를 검색할 때, 이 값과 가장 유사한 데이터를 찾습니다."
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

prompt = """
당신은 부산대학교 학생에게 도움을 주는 어시스턴트입니다.
학생의 질문과 관련된 정보를 직접 검색하고, 이를 바탕으로 답변을 제공하세요.

지시사항:

- 검색 결과에 포함되지 않은 정보는 임의로 생성하지 마세요.

- 모든 응답에는 구체적인 출처가 표기되어야 합니다. 각주 등에 URL 출처를 반드시 남기세요.
    - Ex:  
        - "부산대학교의 2024년 신입생 모집 요강은 다음과 같습니다. [출처](https://onestop.pusan.ac.kr/)"
        - "부산대학교 도서관의 운영 시간은 오전 9시부터 오후 10시까지입니다.[^1]"
            - [^1]: https://onestop.pusan.ac.kr/

- 질문에 대해 복합적인 정보가 필요하다면 query를 유사한 카테고리별로 세분화 합니다.
    - Ex: 기계공학부에서 복수전공을 두 개 하면 몇 학점을 들어야 해?
        - Bad: "기계공학부, 복수전공, 학점"
        - Good: 
            - "기계공학부, 공과대학"
            - "복수전공, 심화전공, 전과"
            - "학점 이수, 교육 과정, 수강 편람"

- query 생성시 질문에 포함된 어휘는 최소한으로 사용하고, 유의어 및 상위 개념어를 사용하세요.

    - Ex: 부산대학교 기계공학부의 전공 필수 과목을 찾아줘
        - Bad: "기계공학부, 전공 필수"
        - Good: 
            - "전공 필수, 전공 기초, 전공 선택"
            - "교양 필수, 교양 선택, 일반 선택"
            - "공과대학, 기계공학부"

- query 생성시 이미 사용한 어휘는 중복하여 사용하지 마세요.

    - Ex: 
        - Bad:
            - "자퇴, 전과, 휴학"
            - "자퇴, 전과, 편입"
            - "자퇴, 휴학, 복학"

        - Good: query에 중복되는 어휘가 없습니다.
            - "자퇴, 전과, 휴학"
            - "졸업, 복학, 편입"

- 검색 query에 "부산대학교"를 포함하지 마세요.
"""

model = "gpt-4o"


def run(query: str):

    notice_service = create_notice_service()
    support_service = create_support_service()

    search_count = 0
    messages: list = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]

    while True:
        tool_choice = "required" if search_count < 2 else "auto"
        completion = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS, tool_choice=tool_choice
        )

        tool_calls = completion.choices[0].message.tool_calls

        if not tool_calls:
            message = completion.choices[0].message.content
            logger(f"\n{message}")
            break

        if tool_calls:
            search_count += 1
            for tool_call in tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                logger(f"{name}: {args['query']}")

                result = []
                if name == "search_notices":
                    result = notice_service.search_notices_with_filter(**args, count=5)
                    result = [{
                        "title": _result.title,
                        "content": _result.content,
                        "url": _result.url
                    } for _result, _ in result]
                elif name == "search_supports":
                    result = support_service.search_supports_with_filter(**args, count=5)
                    result = [{
                        "title": _result.title,
                        "content": chunk.chunk_content,
                        "url": _result.url
                    } for _result, chunk, _ in result]

                messages.append({"role": "function", "content": json.dumps(result, ensure_ascii=False), "name": name})

            continue


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", dest="query", required=True)
    args = parser.parse_args()
    query = str(args.query)

    run(query)
