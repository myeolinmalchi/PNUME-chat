from dependency_injector import containers, providers

from services.app import ApplicationService

from .notice import NoticeContainer
from .calendar import CalendarContainer
from .support import SupportContainer
from .professor import ProfessorContainer
from db import repositories as repo


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.chat"])
    config = providers.Configuration()

    univ_repo = providers.Singleton(repo.UniversityRepository)
    semester_repo = providers.Singleton(repo.SemesterRepository)
    calendar_repo = providers.Singleton(repo.CalendarRepository)

    notice_package = providers.Container(NoticeContainer, semester_repo=semester_repo, univ_repo=univ_repo)
    calendar_package = providers.Container(CalendarContainer, calendar_repo=calendar_repo, semester_repo=semester_repo)
    support_package = providers.Container(SupportContainer)
    professor_package = providers.Container(ProfessorContainer, univ_repo=univ_repo)

    app = providers.Factory(
        ApplicationService,
        professor_service=professor_package.professor_service,
        notice_service=notice_package.notice_service,
        calendar_service=calendar_package.calendar_service,
        support_service=support_package.support_service,
    )
