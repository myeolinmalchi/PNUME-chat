from typing import Optional

TEMPLATE = """
<Goal>
    - 부산대학교 학생의 <Question>에 대해 명료하고 구체적인 답변을 작성해야 합니다.
    - 추가적인 맥락을 위해 function calling을 사용하거나, <SearchHistory>의 정보만으로 답변을 완성합니다.
</Goal>

<Question> {} </Question>

<ReturnFormat>
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
        - <SearchHistory>를 찾을 수 없다면 function calling을 사용하여 추가로 검색하세요
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

CONTEXT_DUMP = """
<ContextDump>
    <SearchHistory>
        {}
    </SearchHistory>
</ContextDump>
"""

SEARCH_RESULT = """
<SearchResult>
    <SearchMethod>
        <name>{}</name>
        <args>{}</args>
    </SearchMethod>
    <Details>
        {}
    </Detail>
</SearchResult>
"""


def prompt(question: str, department: str, grade: int, history: Optional[str]):
    return TEMPLATE.format(question, department, grade, CONTEXT_DUMP.format(history) if history else "")


def search_result_context(tool_name: str, tool_args: str, result: str):
    return SEARCH_RESULT.format(tool_name, tool_args, result)
