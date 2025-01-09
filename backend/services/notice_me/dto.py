from typing import NotRequired, Optional, TypedDict, List

from utils.embed import EmbedResult


class AttachmentDTO(TypedDict):
    name: str
    url: str | None


class NoticeMEInfoDTO(TypedDict):
    title: str
    content: str

    date: str
    author: str
    attachments: Optional[List[AttachmentDTO]]


class NoticeMEEmbeddingsDTO(TypedDict):
    title_embeddings: EmbedResult
    content_embeddings: List[EmbedResult]


class NoticeMEDTO(TypedDict):
    seq: int
    info: NotRequired[NoticeMEInfoDTO]
    embeddings: NotRequired[NoticeMEEmbeddingsDTO]
