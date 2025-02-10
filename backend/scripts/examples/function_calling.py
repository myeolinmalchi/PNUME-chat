import json
import logging
from time import time
from typing import List

from openai.types.chat import ChatCompletionToolParam
from openai.types.chat_model import ChatModel
from db.repositories.calendar import CalendarRepository, SemesterRepository
from services.calendar.service import CalendarService
from services.support import create_support_service
from services.notice import create_notice_service

from openai import OpenAI

from config.logger import _logger

logger = _logger(__name__, disabled=True)

client = OpenAI()

TOOLS: List[ChatCompletionToolParam] = [{
    "type": "function",
    "function": {
        "name": "search_supports",
        "description": "'학생지원시스템'에서 학적, 교육과정, 수업, 성적, 장학, 등록, 졸업, 학생교류, 대학생활, 학생역량 등 학교 생활 전반에 대한 정보를 검색합니다. 학사 일정에 대한 구체적인 정보가 필요하다면 이 함수를 호출하세요.",
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
        "description": "'학과별 공지사항'에서 수업, 과제, 공모전 등 학과 운영과 연관된 정보를 검색합니다. '학생지원시스템'의 포괄적인 정보를 구체적으로 찾기 위해서 최소한 이 함수를 한 번은 호출하세요",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "유사도 검색을 위한 텍스트 입력값. 학과별 공지사항에서 관련 정보를 검색할 때, 이 값과 가장 유사한 데이터를 찾습니다."
                },
                "semesters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "integer",
                                "description": "검색 년도"
                            },
                            "type_": {
                                "type": "string",
                                "enum": ["1학기", "2학기", "여름방학", "겨울방학"],
                                "description": "공지사항의 작성 시점을 기준으로 필터링 합니다. 대략 3~6월은 1학기, 7~8월은 여름방학, 9~12월은 2학기, 1~2월은 겨울방학입니다. 겨울방학은 다음 학년도와 걸쳐 있기 때문에 주의해야 합니다. (ex: 2025년 1월 2일은 2024학년도의 겨울방학)"
                            }
                        },
                        "required": ["year", "semester"],
                    },
                    "description": "학기에 대한 정보를 담습니다."
                },
                "departments": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["정보컴퓨터공학부", "기계공학부", "국어국문학과"],
                        "description": "검색할 학과를 결정합니다. 사용자가 특정 학과를 언급하지 않는다면 학생의 학과를 포함하세요. 최소 한 개 이상의 학과를 포함하세요."
                    }
                }
            },
            "required": ["query"],
        },
        "strict": False
    }
}, {
    "type": "function",
    "function": {
        "name": "search_calendars",
        "description": "주요 학사 일정을 학기별로 검색합니다. 일정 관련 질문에는 이 기능을 반드시 사용하세요.",
        "parameters": {
            "type": "object",
            "properties": {
                "semesters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "integer",
                                "description": "년도"
                            },
                            "type_": {
                                "type": "string",
                                "enum": ["1학기", "2학기", "여름방학", "겨울방학"],
                                "description": "작성 시점을 기준으로 필터링 합니다. 대략 3~6월은 1학기, 7~8월은 여름방학, 9~12월은 2학기, 1~2월은 겨울방학입니다. 겨울방학은 다음 학년도와 걸쳐 있기 때문에 주의해야 합니다. (ex: 2025년 1월 2일은 2024학년도의 겨울방학)"
                            }
                        },
                        "required": ["year", "semester"],
                    },
                    "description": "학기에 대한 정보를 담습니다."
                },
            },
            "required": ["semesters"],
        },
        "strict": False
    }
}]

prompt = """
당신은 부산대학교 학생에게 도움을 주는 어시스턴트입니다.
학생의 질문과 관련된 정보를 직접 검색하고, 이를 바탕으로 답변을 제공하세요.

지시사항:

- 검색 결과에 포함되지 않은 정보는 임의로 생성하지 마세요.

- 구체적인 정보를 얻을 수 있을 때까지 검색을 수행합니다.
    - Ex: 정보컴퓨터학부 1학년 수강신청 유의사항을 알려주세요
        - Bad: 정보컴퓨터학부 1학년은 전공 기초 및 교양 필수 과목을 수강하는 것이 좋습니다. 자세한 사항은 학생지원시스템 및 학과 공지사항에서 확인할 수 있습니다.
        - Good: 전공 기초 과목 중 '공학수학', '일반물리학', 'C 프로그래밍'은 1학년에 수강하는 것이 권장됩니다. 또한 교양 필수 과목 중 '컴퓨팅적 사고' 및 '대학실용영어' 과목을 수강하는 것이 좋습니다.
    - Ex: 정보컴퓨터공학부는 한 학기에 최대 몇학점까지 수강할 수 있나요?
        - Bad: 최대 수강 학점은 학생지원시스템에서 확인하는 것이 좋습니다.
        - Good: 최대 수강 학점은 21학점이며, 이전 학기의 평균 평점이 4.1 이상인 경우 23학점까지 수강할 수 있습니다.

- 특정 학기에 대한 정보는 직전 방학 기간을 반드시 포함하여 검색합니다. 가령 2024년 2학기에 대해 검색하는 경우 2024년 여름방학과 2024년 1학기를 포함합니다.

- 모든 응답에는 URL 출처를 반드시 포함하세요.
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

        - Good:
            - "자퇴, 전과, 휴학"
            - "졸업, 복학, 편입"

- 검색 query에 "부산대학교"를 포함하지 마세요.

- 오늘의 날짜는 2025년 2월 9일 일요일이며, "2024학년도 겨울방학"에 해당합니다.
- 특정 시점에 대한 언급이 없는 경우, 학기 필터링에 2024학년도 겨울방학과 2025학년도 1학기를 반드시 포함하세요.
- 질문자는 "정보컴퓨터공학부" 1학년 학생입니다.
"""

model: ChatModel = "o3-mini"


def run(query: str):

    notice_service = create_notice_service()
    support_service = create_support_service()

    semester_repo = SemesterRepository()
    calendar_repo = CalendarRepository()

    calendar_service = CalendarService(semester_repo, calendar_repo)

    search_count = 0
    messages: list = [{
        "role": "system",
        "content": prompt
    }, {
        "role": "user",
        "content": query
    }]

    st = time()

    while True:
        tool_choice = "required" if search_count < 2 else "auto"
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice=tool_choice,
            reasoning_effort="low"
            #temperature=0.9
        )

        tool_calls = completion.choices[0].message.tool_calls

        if not tool_calls:
            message = completion.choices[0].message.content
            #logger(f"답변: \n\n{message}")
            print(f"답변({time() - st:.2f}sec): \n\n{message}")
            break

        if tool_calls:
            messages.append(completion.choices[0].message)

            search_count += 1
            for tool_call in tool_calls:
                id = tool_call.id
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                logger(f"({search_count}) tool: {name}")

                result = []
                if name == "search_notices":
                    if 'departments' in args:
                        departments = args['departments']
                        logger(f"({search_count}) 학과: {', '.join(departments)}")
                    if 'semesters' in args:
                        semesters = args['semesters']
                        for s in semesters:
                            logger(
                                f"({search_count}) 학기: {s['year']}년 {s['type_']}"
                            )

                    logger(f"({search_count}) 검색어: {args['query']}")
                    result = notice_service.search_notices_with_filter(
                        **args, count=5
                    )
                    result = [{
                        "title": _result.title,
                        "content": _result.content,
                        "url": _result.url
                    } for _result, _ in result]
                    logger(f"({search_count}) 검색 결과:")
                    for r in result:
                        title = r["title"]
                        title = title if len(title) < 40 else title[:40] + "..."
                        logger(f"({search_count})   - {title}")
                elif name == "search_supports":
                    logger(f"({search_count}) 검색어: {args['query']}")
                    result = support_service.search_supports_with_filter(
                        **args, count=5
                    )
                    result = [{
                        "title": _result.title,
                        "content": chunk.chunk_content,
                        "url": _result.url
                    } for _result, chunk, _ in result]
                    logger(f"({search_count}) 검색 결과:")
                    for r in result:
                        title = r["title"]
                        title = title if len(title) < 40 else title[:40] + "..."
                        logger(f"({search_count})   - {title}")
                elif name == "search_calendars":
                    semesters = args['semesters']
                    for s in semesters:
                        logger(
                            f"({search_count}) 학기: {s['year']}년 {s['type_']}"
                        )
                    result = calendar_service.get_calendars(semesters)

                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "name": name,
                    "tool_call_id": id
                })

            continue


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", dest="query", required=True)
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()
    query = str(args.query)

    if bool(args.verbose):
        logger.disabled = False

    run(query)
