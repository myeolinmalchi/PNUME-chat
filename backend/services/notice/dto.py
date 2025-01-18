from typing import NotRequired, TypedDict, List

from services.base import EmbedResult


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


class NoticeDTO(TypedDict):
    url: str
    info: NotRequired[NoticeInfoDTO]
    attachments: NotRequired[List[AttachmentDTO]]
    embeddings: NotRequired[NoticeEmbeddingsDTO]
