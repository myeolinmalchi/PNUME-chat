from typing import List
from db.models.calendar import CalendarModel
from db.repositories.calendar import CalendarRepository, SemesterRepository
from services.base.service import BaseService
from services.base.types.calendar import SemesterType


class CalendarService(BaseService):

    def __init__(self, semester_repo: SemesterRepository, calendar_repo: CalendarRepository):
        self.semester_repo = semester_repo
        self.calendar_repo = calendar_repo

    def dto2orm(self, dto):
        pass

    def orm2dto(self, orm):
        pass

    async def run_full_crawling_pipeline_async(self, **kwargs) -> List[CalendarModel]:
        return [CalendarModel()]

    def get_calendars(self, semesters: List[SemesterType]):

        semester_models = self.semester_repo.search_semesters(semesters)

        if not semester_models or not isinstance(semester_models, list):
            raise ValueError("학사 일정을 불러오지 못했습니다.")

        ids: List[int] = [s.id for s in semester_models]
        search_results = self.calendar_repo.search_calendars_by_semester_ids(ids)

        return [{
            "period": f"{c.st_date} ~ {c.ed_date}",
            "description": c.name
        } for c in search_results]
