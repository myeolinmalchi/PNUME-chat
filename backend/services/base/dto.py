from typing import Dict, List, NotRequired, Required, TypedDict, TypeVar


class BaseDTO(TypedDict, total=False):
    url: Required[str]


DTO = TypeVar("DTO", bound=BaseDTO)


class EmbedResult(TypedDict):
    chunk: NotRequired[str]
    dense: List[float]
    sparse: Dict[int, float]
