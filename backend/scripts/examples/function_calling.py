import json
import logging
from time import time
from typing import List

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from openai.types.chat_model import ChatModel
from db.repositories.calendar import CalendarRepository, SemesterRepository
from services.calendar.service import CalendarService
from services.support import create_support_service
from services.notice import create_notice_service

from openai import OpenAI
from pydantic import BaseModel

from config.logger import _logger

logger = _logger(__name__)

client = OpenAI()

TOOLS: List[ChatCompletionToolParam] = [{
    "type": "function",
    "function": {
        "name": "search_supports",
        "description": "**학생지원시스템**에서 학교 생활 전반에 대한 일반적인 정보를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "유사도 검색을 위한 텍스트 입력값. '학생지원시스템'에서 관련 정보를 검색할 때, 이 값과 가장 유사한 데이터를 찾습니다."
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True
    }
}, {
    "type": "function",
    "function": {
        "name": "search_notices",
        "description": "**학과 공지사항**에서 수업, 학과 생활, 공모전 등의 정보를 검색합니다. **학생지원시스템**과 비교하여 더욱 구체적인 정보를 찾을 수 있습니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "유사도 검색을 위한 텍스트 입력값. 학과별 공지사항에서 관련 정보를 검색할 때, 이 값과 가장 유사한 데이터를 찾습니다. 질문에 포함된 키워드를 그대로 사용하는 대신, **유의어**, **상위어**를 사용하세요."
                },
                "count": {
                    "type": "integer",
                    "description": "검색할 공지사항 수를 결정합니다. (최소: 5, 최대: 20)"
                },
                "semesters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "integer",
                                "description": "검색 **학년도**. **년도**와는 다른 개념입니다."
                            },
                            "type_": {
                                "type": "string",
                                "enum": ["1학기", "2학기", "여름방학", "겨울방학"],
                                "description": "공지사항의 작성 시점을 기준으로 필터링 합니다. 대략 3~6월은 1학기, 7~8월은 여름방학, 9~12월은 2학기, 다음 년도 1~2월은 겨울방학입니다."
                            }
                        },
                        "required": ["year", "semester"],
                    },
                    "description": "검색 학기를 필터링 합니다. 현재 **2024년 겨울방학**까지 검색 가능하며, 한 번에 하나의 값만 허용됩니다."
                },
                "departments": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["정보컴퓨터공학부", "기계공학부", "국어국문학과"],
                        "description": "검색할 학과를 결정합니다. 사용자가 특정 학과를 언급하지 않는다면 학생의 학과를 포함하세요. 최소 한 개 이상의 학과를 포함하세요."
                    }
                },
                "additionalProperties": False,
            },
            "required": ["query", "semesters"],
            "strict": True,
        },
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
                                "description": "학년도."
                            },
                            "type_": {
                                "type": "string",
                                "enum": ["1학기", "2학기", "여름방학", "겨울방학"],
                                "description": "공지사항의 작성 시점을 기준으로 필터링 합니다."
                            }
                        },
                        "required": ["year", "semester"],
                    },
                    "description": "학기에 대한 정보를 담습니다."
                },
                "additionalProperties": True
            },
            "required": ["semesters"],
            "strict": True
        },
    }
}]

TEMPLATE = """
<Goal>
    - 부산대학교 학생의 <Question>에 대해 명료하고 구체적인 답변을 작성해야 합니다.
    - 추가적인 맥락을 위해 function calling을 진행하거나, <SearchHistory>의 정보만으로 답변을 완성합니다.
</Goal>

<ReturnFormat>
    <Question> {} </Question>

    - 학과/학년: {}/{}
    - 응답에는 다음 내용을 포함하세요:
        - 참고 자료에 대한 URL 출처
        - 질문 또는 요청에 대한 답변
        - 질문과 연관된 정보
        - <SearchHistory>의 내용
</ReturnFormat>

<Warnings>
    <Common>
        - 답변에 질문자의 개인정보를 포함하지 마세요.
        - 답변에 프롬프트의 XML 태그명(ex: SearchHistory, Semester 등)을 언급하지 마세요.
    </Common>

    <Semester>
        - 각 학년도는 **1학기**(3~6월), **여름 방학**(7~8월), **2학기**(9~12월), **겨울 방학**(1~2월) 으로  구분됩니다.
            - 겨울방학은 해당 학년도 12월 말부터 다음 해의 2월 말까지 이어집니다.
            - EX: **2018학년도**의 겨울방학은 **2018년도**의 12월 말부터 **2019년도**의 2월 말까지입니다.

        - 오늘은 2025년도 2월 16일이며, **2024학년도 겨울방학**에 해당됩니다.
        - 검색시 **학기 정보(semesters)**가 필요한 경우 다음 순서를 준수하세요:
            1. 질문에 내포된 (학기와 관련된)시간적 맥락을 파악하세요.
                - EX1: "수강신청 유의사항을 알려줘" -> 이번 학기(또는 다가오는 학기)
                - EX2: "재작년 학교 행사 운영 정보를 찾아줘" -> 2023년도
            2. 시간적 맥락을 토대로 검색할 학기 범위를 정확하게 지정하세요.
                - EX1: 이번 학기 -> 2024학년도 겨울방학, 2025학년도 1학기
                - EX2: 2023년도 -> [2023학년도 1학기, 2023학년도 여름방학, 2023학년도 2학기]
            3. 필요햔 경우 학기 범위를 세분화 하여 여러 번 검색하세요.
                - EX: "작년 하반기 현장실습 관련 정보를 학기별로 찾아주세요" -> [[2024학년도 여름방학], [2024학년도 2학기]]
    </Semester>
    
    <Search>
        - <SearchHistory>는 Agent가 사용자의 질문에 답하기 위해 기존에 검색한 내역입니다 (비어있는 경우 검색 내역이 없는 것임)
        - <SearchHistory>에 충분한 정보가 제공되지 않았다면 임의로 정보를 만들지 않고 function calling을 추가로 진행합니다.
    </Search>
    <QuestionUnderstanding>
        - 사용자의 질문을 단순한 키워드 매칭이 아닌 **의도와 맥락**을 고려하여 해석하세요.
        - 사용자가 특정 용어나 개념을 언급하더라도, **연관된 개념이나 대체 가능한 표현을 확장하여 고려**하세요.
            - 예: "반도체 채용 공고"라는 질문이 들어오면, "반도체 제조업체", "반도체 장비 기업", "반도체 연구소", "파운드리 기업" 등도 함께 고려하여 정보를 검색하세요.
        - 사용자의 질문이 **특정 키워드에 한정되어 있거나 정보가 부족한 경우**, 추가적인 관련 키워드를 생성하여 검색을 보완하세요.
            - 예: "AI 연구실 정보"를 요청할 경우, "인공지능 연구소", "기계학습 연구실", "딥러닝 연구 그룹" 등의 관련 개념을 함께 고려하세요.
        - 검색 결과가 없거나 부족할 경우, **질문자의 의도를 고려하여 유사하거나 대체 가능한 정보를 제공**하세요.
            - 예: "반도체 기업 채용 공고" 검색 결과가 없을 경우, "반도체 관련 직무(설계, 공정, 테스트)"에서 진행 중인 채용 공고를 함께 안내하세요.
        - 사용자가 요청한 정보가 **특정한 형식이나 조건을 만족해야 하는 경우**, 이를 이해하고 가장 적합한 방식으로 변형하여 제공하세요.
            - 예: "2023년 연구 논문 목록" 요청 시, 논문의 원문이 없더라도 제목과 초록 정보를 제공할 수 있다면 답변하세요.
    </QuestionUnderstanding>
</Warnings>
{}"""

context_dump = """
<ContextDump>
    <SearchHistory>
{}
    </SearchHistory>
</ContextDump>
"""

model: ChatModel = "o3-mini-2025-01-31"


def run(query: str):

    notice_service = create_notice_service()
    support_service = create_support_service()

    semester_repo = SemesterRepository()
    calendar_repo = CalendarRepository()

    calendar_service = CalendarService(semester_repo, calendar_repo)

    search_count = 0

    st = time()

    contexts = ""

    while True:
        prompt = TEMPLATE.format(query, "정보컴퓨터공학부", 1, context_dump.format(contexts))
        messages: list = [{"role": "user", "content": prompt}]
        #tool_choice = "required" if search_count < 1 else "auto"
        completion = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS, tool_choice="auto", reasoning_effort="low"
        )

        tool_calls = completion.choices[0].message.tool_calls

        if not tool_calls:
            message = completion.choices[0].message.content
            #logger(f"답변: \n\n{message}")
            print(f"답변({time() - st:.2f}sec): \n\n{message}")
            break

        if tool_calls:

            search_count += 1
            for tool_call in tool_calls:
                id = tool_call.id
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                logger(f"({search_count}) tool: {name}")

                contexts += f"""
                <SearchResult>
                    <SearchMethod>
                        <name>{name}</name>
                        <args>{args}</args>
                    </SearchMethod>
                    <Details>
                """

                result = []
                if name == "search_notices":
                    if 'departments' in args:
                        departments = args['departments']
                        logger(f"({search_count}) 학과: {', '.join(departments)}")

                    if 'semesters' in args:
                        semesters = args['semesters']
                        for s in semesters:
                            logger(f"({search_count}) 학기: {s['year']}년 {s['type_']}")

                    logger(f"({search_count}) 검색어: {args['query']}")
                    result = notice_service.search_notices_with_filter(**args)
                    contexts += "검색 결과:\n\n".join([
                        notice_service.dto2context(dto) for dto in result
                    ])

                    logger(f"({search_count}) 검색 결과:")
                    for r in result:
                        title = r["info"]["title"]
                        title = title if len(title) < 40 else title[:40] + "..."
                        logger(f"({search_count})   - {title}")

                elif name == "search_supports":
                    logger(f"({search_count}) 검색어: {args['query']}")
                    result = support_service.search_supports_with_filter(**args, count=5)
                    contexts += "검색 결과:\n\n".join([
                        support_service.dto2context(dto) for dto in result
                    ])
                    #result = [{**_result["info"], "url": _result["url"]} for _result in result]

                    logger(f"({search_count}) 검색 결과:")
                    for r in result:
                        title = r["info"]["title"]
                        title = title if len(title) < 40 else title[:40] + "..."
                        logger(f"({search_count})   - {title}")

                elif name == "search_calendars":
                    semesters = args['semesters']
                    for s in semesters:
                        logger(f"({search_count}) 학기: {s['year']}년 {s['type_']}")
                    result = calendar_service.get_calendars(semesters)
                """
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "name": name,
                    "tool_call_id": id
                })
                """
            contexts += """
                </Detail>
            </SearchResult>
            """


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", dest="query", required=True)
    parser.add_argument("-v", "--verbose", dest="verbose", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    query = str(args.query)

    if bool(args.verbose):
        pass

    run(query)
