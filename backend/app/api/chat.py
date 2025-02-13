from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

import containers as co

from services import notice, support, calendar
from services.base.types.calendar import SemesterType

router = APIRouter()


class TestRequestBody(BaseModel):
    input: str
    department: str


@router.post("/chat")
@inject
async def chat(
    req: TestRequestBody,
    notice_service: notice.NoticeServiceBase = Depends(
        Provide[co.AppContainer.notice.notice_service]
    ),
    support_service: support.SupportService = Depends(
        Provide[co.AppContainer.support.provided.support_service]
    ),
    calendar_service: calendar.CalendarService = Depends(
        Provide[co.AppContainer.calendar.provided.calendar_service]
    ),
):

    notices = notice_service.search_notices_with_filter(
        query=req.input,
        semesters=[
            SemesterType(year=2024, type_="겨울방학"),
            SemesterType(year=2024, type_="2학기"),
            SemesterType(year=2024, type_="1학기")
        ],
        count=5,
        departments=[req.department]
    )

    results = [{
        "title": _result.title,
        "url": _result.url,
        "date": _result.date,
    } for _result, _ in notices]

    return results
