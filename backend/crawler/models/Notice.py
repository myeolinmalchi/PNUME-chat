from typing import List, TypedDict


class Attachment(TypedDict):
    name: str
    url: str | None


class Notice(TypedDict):
    title: str
    content: str

    date: str
    author: str
    attachments: List[Attachment]
