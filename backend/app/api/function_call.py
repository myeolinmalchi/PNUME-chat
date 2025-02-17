import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Tuple

from fastapi import HTTPException

from openai.types.chat import ChatCompletionToolParam
from openai import OpenAI
import openai


from services.notice import create_notice_service
from services.professor import create_professor_service
from services.support import create_support_service
from db.repositories.calendar import CalendarRepository, SemesterRepository
from services.calendar.service import CalendarService
from db.models.notice import NoticeModel
from db.models.support import SupportModel
from db.models.professor import ProfessorModel
from services.base.types.calendar import SemesterType

## 의존성 주입 테스트
"""from services import notice, support, calendar, professor
import containers as co
from dependency_injector.wiring import inject, Provide
from fastapi import Depends"""

load_dotenv()


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



# OpenAI functioncalling 비동기 함수
async def function_calling(question: str) -> str:
    question = question
    openai.api_key = os.environ.get("OPENAI_KEY")

    tools = TOOLS
    prompt: str = prompt

    messages: List = [
        {
            "role": "system",
            "content": prompt 
        },
        {
            "role": "user",
            "content": f"{question}"
        }
    ]
    

    while True:
        completion = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=messages,
        functions=tools,
        function_call="auto",
    )
        try:
            choice = completion.get("choices")[0]
            if choice["finish_reason"] == "function_call":
                function_name = function_call["name"]
                function_args = json.loads(function_call["arguments"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during function call: {str(e)}")    

        try:
            choice = completion.get("choices")[0]
            if choice["finish_reason"] == "function_call":
                function_call = choice["message"]["function_call"]
                function_name = function_call["name"]
                function_args = json.loads(function_call["arguments"])

                if function_name == "search_support":
                    support_search_result =  await search_support(**function_args) 
                    supports_info =[]
                    for support, rrf_score in support_search_result:
                        support_info = (
                            f"Category: {support.category}\n"
                            f"SubCategory: {support.sub_category}\n"
                            f"Title: {support.title}\n"
                            f"URL: {support.url}\n"
                            f"Content: {support.content}\n"
                        )
                        supports_info.append(support_info)
                    supports_info_str = "\n\n".join(supports_info)
                    messages.append({
                        "role": "function",
                        "content": f"{supports_info_str}"
                    })

                elif function_name == "search_notices":
                    notice_search_result =  await search_notices(**function_args)
                    notices_info = []
                    for notice, rrf_score in notice_search_result:
                        notice_info = (
                            f"Title: {notice.title}\n"
                            f"Date: {notice.date}\n"
                            f"URL: {notice.url}\n"
                            f"Department: {notice.department}\n"
                            f"content: {notice.content}\n"
                        )
                        notices_info.append(notice_info)
                    notices_info_str = "\n\n".join(notices_info)
                    messages.append({
                        {
                            "role": "function",
                            "content": f"{notices_info_str}"
                        }
                    })
                
                elif function_name == "search_calendar":
                    calendar_search_result =  await search_calendar(**function_args)
                    calendars_info: List[Dict] = []
                    for calendar in calendar_search_result:
                        calendar_info = (
                            f"기간: {calendar.period}\n"
                            f"학사일정: {calendar.description}\n"
                        )
                        calendars_info.append(calendar_info)
                    calendar_info_str = "\n\n".join(calendars_info)
                    messages.append({
                        "role": "function",
                        "content": f"{calendar_info_str}"
                    })
                    
                elif function_name == "search_professor":
                    professor_search_result =  await search_professor(**function_args)
                    professors_info = []
                    for professor, rrf_score in professor_search_result:
                        professor_info = (
                            f"Name: {professor.name}\n"
                            f"Office Phone: {professor.office_phone}\n"
                            f"Website: {professor.website}\n"
                            f"Email: {professor.email if professor.emial else 'N/A'}\n"
                            f"Department: {professor.department.name}\n"  # department 객체의 name 필드 접근
                            f"Major: {professor.major.name if professor.major else 'N/A'}\n"  # major가 없을 수 있으므로 체크
                            f"Detail: {professor.detail}"
                        )
                        professors_info.append(professor_info)
                    professor_info_str = "\n\n".join(professors_info)
                    messages.append({
                        "role": "function",
                        "content": f"{professor_info_str}"
                    })   
                else:
                    raise HTTPException(status_code=400, detail="Unknown function called")
            else:
                answer = choice["message"]["content"]
                messages.append({
                    "role": "assistant",
                    "content": answer
                })
                return choice["message"]["content"] ##여기서 최종 답변 생성하고 리턴되는거임 !!

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during function call: {str(e)}")
        
        continue




async def search_support(query: str) -> List[Tuple[SupportModel, float]]:
    support_service = create_support_service()
    search_result = support_service.search_supports_with_filter(query=query)

    return search_result

async def search_notices(query: str) -> List[Tuple[NoticeModel, float]]:
    notice_service = create_notice_service()
    search_result = notice_service.search_notices_with_filter(query=query)

    return search_result

## 날짜와 학사 일정에 대한 질문을 받으면 그걸 토대로 학기 데이터를 추출해서 이를 semestertype객체로서 전달
## semetsetertype객체를 이용해서 calendar table에서 
async def search_calendar(query: str, semesters: List[SemesterType]):
# 학사일정 searching function
    semester_repo = SemesterRepository()
    calendar_repo = CalendarRepository()
    calendar_service = CalendarService(semester_repo=semester_repo, calendar_repo=calendar_repo)

    search_result = calendar_service.get_calendars(semesters=semesters)
    
    return search_result

async def search_professor(query: str) -> List[Tuple[ProfessorModel, float]]:
    professor_service = create_professor_service()
    search_result = professor_service.search_professors(query=query)

    return search_result