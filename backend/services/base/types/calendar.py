from datetime import date
from typing import Literal, TypedDict


class SemesterType(TypedDict):
    """학기 타입"""

    year: int
    type_: Literal["1학기", "2학기", "여름방학", "겨울방학"]


class DateRangeType(TypedDict):
    """날짜 범위 타입"""

    st_date: date
    ed_date: date
