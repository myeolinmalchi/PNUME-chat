from typing import TypedDict, List

from services.base import EmbedResult
from services.base.dto import BaseDTO


class AttachmentDTO(TypedDict):
    name: str
    url: str | None


class NoticeInfoDTO(TypedDict):
    title: str
    content: str
    category: str

    department: str

    date: str
    author: str


class NoticeEmbeddingsDTO(TypedDict):
    title_embeddings: EmbedResult
    content_embeddings: List[EmbedResult]


class NoticeDTO(BaseDTO):
    info: NoticeInfoDTO
    attachments: List[AttachmentDTO]
    embeddings: NoticeEmbeddingsDTO
