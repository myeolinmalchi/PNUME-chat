from typing import List, TypedDict

class Attatchment(TypedDict):
    name: str
    link:str | None

class News(TypedDict):
    title: str
    date: str
    author: str
    attatchments: List[Attatchment]
    contents: str
