from typing import Any, NotRequired, Optional, TypedDict, Unpack, Required, List

from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall

from services.app.prompt import search_result_context
from services.base.types.calendar import SemesterType
from services.base.service import BaseService
from services.notice import NoticeService
from services.professor import ProfessorService
from services.support import SupportService
from services.university.service.calendar import CalendarService


class ApplicationService(BaseService):

    def __init__(
        self, notice_service: NoticeService, professor_service: ProfessorService, support_service: SupportService,
        calendar_service: CalendarService
    ):
        self.notice_service = notice_service
        self.professor_service = professor_service
        self.support_service = support_service
        self.calendar_service = calendar_service

    def call_by_name(self, function_name: str, **args):
        if not hasattr(self, function_name):
            return None
        func = getattr(self, function_name)
        return func(**args)

    def call_tool_by_name(self, tool_call: ChatCompletionMessageToolCall):
        import json
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        result = self.call_by_name(name, **args)

        args_str = [f"{key}: {value}" for key, value in args.items()]
        args_str = "\n".join([f"- {key}: {value}" for key, value in args.items()])

        return search_result_context(name, args_str, result) if result else None

    def parse_chat_completion(self, completion: ChatCompletion) -> Optional[str | List[str]]:
        tool_calls = completion.choices[0].message.tool_calls
        if not tool_calls:
            return completion.choices[0].message.content

        contexts = []
        for tool_call in tool_calls:
            context = self.call_tool_by_name(tool_call)
            if context:
                contexts.append(context)

        return contexts

    class SearchOpts(TypedDict):
        count: NotRequired[int]
        lexical_ratio: NotRequired[float]

    class SearchNoticeOpts(SearchOpts):
        query: str
        semesters: Required[List[SemesterType]]
        departments: Required[List[str]]

    class SearchProfessorOpts(SearchOpts):
        query: str
        departments: Required[List[str]]

    class SearchSupportOpts(SearchOpts):
        query: str

    def search_notices(self, **opts: Unpack[SearchNoticeOpts]):
        notices = self.notice_service.search_notices_with_filter(**opts)
        return [self.notice_service.dto2context(notice) for notice in notices]

    def search_calendars(self, semesters: List[SemesterType]):
        return self.calendar_service.get_calendars(semesters)

    def search_professors(self, **opts: Unpack[SearchNoticeOpts]):
        return self.professor_service.search_professors(**opts)

    def search_supports(self, query: str, **opts: Unpack[SearchOpts]):
        supports = self.support_service.search_supports_with_filter(query, **opts)
        return [self.support_service.dto2context(support) for support in supports]
