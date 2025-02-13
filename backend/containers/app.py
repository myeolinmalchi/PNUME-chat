from dependency_injector import containers, providers

from .notice import NoticeContainer
from .professor import ProfessorContainer
from .support import SupportContainer
from db import repositories as repo

class AppContainers(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.main"])
    config = providers.Configuration()

    univ_repo = providers.Singleton(repo.UniversityRepository)


    notice = providers.Container(
        NoticeContainer, univ_repo=univ_repo
    )
    professor = providers.Container(
        ProfessorContainer, univ_repo=univ_repo
    )
    support = providers.Container(
        SupportContainer
    )