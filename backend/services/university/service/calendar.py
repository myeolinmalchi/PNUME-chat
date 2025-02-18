from typing import List
from db.models.calendar import CalendarModel, SemesterModel
from db.repositories.base import transaction
from db.repositories.calendar import CalendarRepository, SemesterRepository
from services.base.service import BaseDomainService
from services.base.types.calendar import SemesterType
from services.university.dto import CalendarDTO


class CalendarService(BaseDomainService[CalendarDTO, CalendarModel]):

    def __init__(self, semester_repo: SemesterRepository, calendar_repo: CalendarRepository):
        self.semester_repo = semester_repo
        self.calendar_repo = calendar_repo

    @transaction()
    def dto2orm(self, dto):
        semester_model = self.semester_repo.search_semesters({**dto["semester"]})
        if not semester_model:
            raise ValueError("학기 정보가 존재하지 않습니다.")

        assert isinstance(semester_model, SemesterModel)

        CalendarModel(
            st_date=dto["date_range"]["st_date"],
            ed_date=dto["date_range"]["ed_date"],
            semester_id=semester_model.id,
            name=dto["description"]
        )
        return None

    @transaction()
    def orm2dto(self, orm):
        return CalendarDTO(
            **{
                "date_range": {
                    "st_date": orm.st_date,
                    "ed_date": orm.ed_date,
                },
                "description": orm.name,
                "semester": {
                    "year": orm.semester.year,
                    "type_": orm.semester.type_,
                }
            }
        )

    @transaction()
    def get_calendars(self, semesters: List[SemesterType]):

        semester_models = self.semester_repo.search_semesters(semesters)

        if not semester_models or not isinstance(semester_models, list):
            raise ValueError("학사 일정을 불러오지 못했습니다.")

        ids: List[int] = [s.id for s in semester_models]
        search_results = self.calendar_repo.search_calendars_by_semester_ids(ids)

        return [self.orm2dto(orm) for orm in search_results]
