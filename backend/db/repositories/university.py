from db.models.universities import DepartmentModel, UniversityModel
from db.repositories.base import BaseRepository


class UniversityRepository(BaseRepository[UniversityModel]):

    def find_department_by_name(self, name: str):
        result = self.session.query(DepartmentModel).where(
            DepartmentModel.name == name
        ).one_or_none()

        if not result:
            raise ValueError(f"존재하지 않는 학과입니다. ({name})")

        return result
