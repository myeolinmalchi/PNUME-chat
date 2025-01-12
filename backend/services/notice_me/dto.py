from typing import NotRequired, TypedDict, List

from services.base import EmbedResult


class AttachmentDTO(TypedDict):
    name: str
    url: str | None


class NoticeMEInfoDTO(TypedDict):
    title: str
    content: str
    category: str

    date: str
    author: str


class NoticeMEEmbeddingsDTO(TypedDict):
    title_embeddings: EmbedResult
    content_embeddings: List[EmbedResult]


class NoticeMEDTO(TypedDict):
    seq: int
    info: NotRequired[NoticeMEInfoDTO]
    attachments: NotRequired[List[AttachmentDTO]]
    embeddings: NotRequired[NoticeMEEmbeddingsDTO]
