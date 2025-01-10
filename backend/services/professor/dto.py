from typing import List, NotRequired, TypedDict, Literal

from utils.embed import EmbedResult


class ResearchFieldDTO(TypedDict):
    seq: int
    name: str
    embeddings: NotRequired[EmbedResult]


class EducationDTO(TypedDict):
    seq: int
    name: str
    edu_type: NotRequired[Literal["학사", "석사", "박사", "석박사통합"]]
    embeddings: NotRequired[EmbedResult]


class CareerDTO(TypedDict):
    seq: int
    name: str
    embeddings: NotRequired[EmbedResult]


class ProfessorBasicInfoDTO(TypedDict):
    name: str
    name_eng: NotRequired[str]

    profile_img: NotRequired[str]
    office_phone: NotRequired[str]
    website: NotRequired[str]
    email: NotRequired[str]
    lab_addr: NotRequired[str]

    major: str
    minor: NotRequired[str]


class ProfessorAdditionalInfoDTO(TypedDict):
    fields: NotRequired[List[ResearchFieldDTO]]
    educations: NotRequired[List[EducationDTO]]
    careers: NotRequired[List[CareerDTO]]


class ProfessorDTO(TypedDict):
    seq: int
    basic_info: ProfessorBasicInfoDTO
    additional_info: ProfessorAdditionalInfoDTO
