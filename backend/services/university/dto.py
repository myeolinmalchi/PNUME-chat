from services.base.dto import BaseDTO
from services.base.types.calendar import DateRangeType, SemesterType


class CalendarDTO(BaseDTO):
    semester: SemesterType
    date_range: DateRangeType
    description: str
