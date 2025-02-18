from typing import NotRequired, TypedDict, Unpack, Required, List

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

    class SearchOpts(TypedDict):
        count: NotRequired[int]
        lexical_ratio: NotRequired[float]

    class SearchNoticeOpts(SearchOpts):
        semesters: Required[List[SemesterType]]
        departments: Required[List[str]]

    class SearchProfessorOpts(SearchOpts):
        departments: Required[List[str]]

    def search_notices(self, query: str, **opts: Unpack[SearchNoticeOpts]):
        return self.notice_service.search_notices_with_filter(query, **opts)

    def search_calendar(self, semesters: List[SemesterType]):
        return self.calendar_service.get_calendars(semesters)

    def search_professor(self, query: str, **opts: Unpack[SearchNoticeOpts]):
        return self.professor_service.search_professors(query, **opts)

    def search_supports(self, query: str, **opts: Unpack[SearchOpts]):
        return self.support_service.search_supports_with_filter(query, **opts)
