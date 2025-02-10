from dependency_injector import containers, providers

from .notice import NoticeContainer
from .calendar import CalendarContainer
from .support import SupportContainer
from db import repositories as repo


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.chat"])
    config = providers.Configuration()

    univ_repo = providers.Singleton(repo.UniversityRepository)
    semester_repo = providers.Singleton(repo.SemesterRepository)
    calendar_repo = providers.Singleton(repo.CalendarRepository)

    notice = providers.Container(
        NoticeContainer, semester_repo=semester_repo, univ_repo=univ_repo
    )
    calendar = providers.Container(
        CalendarContainer,
        calendar_repo=calendar_repo,
        semester_repo=semester_repo
    )
    support = providers.Container(SupportContainer)
