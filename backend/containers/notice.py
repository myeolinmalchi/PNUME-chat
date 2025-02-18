from dependency_injector import containers, providers

import db.repositories as repo
from services import notice


class NoticeContainer(containers.DeclarativeContainer):
    univ_repo = providers.Dependency(repo.UniversityRepository)
    semester_repo = providers.Dependency(repo.SemesterRepository)

    notice_repo = providers.Singleton(repo.NoticeRepository)
    notice_embedder = providers.Singleton(notice.NoticeEmbedder)

    notice_service = providers.Factory(
        notice.NoticeService,
        notice_repo=notice_repo,
        notice_embedder=notice_embedder,
        university_repo=univ_repo,
        semester_repo=semester_repo,
    )
