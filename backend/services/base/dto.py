from typing import Required, TypedDict, TypeVar


class BaseDTO(TypedDict, total=False):
    url: Required[str]


DTO = TypeVar("DTO", bound=BaseDTO)
