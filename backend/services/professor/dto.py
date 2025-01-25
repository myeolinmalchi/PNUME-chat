from typing import List, NotRequired, Required, TypedDict

from services.base import EmbedResult


class ProfessorInfoDTO(TypedDict):
    name: str
    name_eng: NotRequired[str]

    profile_img: NotRequired[str]
    office_phone: NotRequired[str]
    website: NotRequired[str]
    email: NotRequired[str]
    lab_addr: NotRequired[str]

    detail: NotRequired[str]

    department: str
    major: NotRequired[str]


class ProfessorDTO(TypedDict, total=False):
    url: Required[str]
    info: Required[ProfessorInfoDTO]
    embeddings: NotRequired[List[EmbedResult]]
