from typing import TypedDict, List

from services.base.dto import BaseDTO
from services.base.embedder import EmbedResult


class SupportAttachmentDTO(TypedDict):
    name: str
    url: str | None


class SupportInfoDTO(TypedDict):
    category: str
    sub_category: str

    title: str
    content: str


class SupportEmbeddingsDTO(TypedDict):
    title_embeddings: EmbedResult
    content_embeddings: List[EmbedResult]


class SupportDTO(BaseDTO):
    info: SupportInfoDTO
    embeddings: SupportEmbeddingsDTO
    attachments: List[SupportAttachmentDTO]
