from typing import List

from openai.types.chat import ChatCompletionToolParam

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
