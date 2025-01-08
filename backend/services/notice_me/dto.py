from typing import NotRequired, TypedDict, List, Optional


class AttachmentDTO(TypedDict):
    name: str
    url: str | None


class NoticeMEDTO(TypedDict):
    seq: int
    title: str
    content: str

    date: str
    author: str
    attachments: NotRequired[List[AttachmentDTO]]
