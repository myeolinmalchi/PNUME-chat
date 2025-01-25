from db.models.professor import ProfessorModel
from db.models.universities import DepartmentModel
from db.repositories.base import BaseRepository


class ProfessorRepository(BaseRepository[ProfessorModel]):

    def delete_by_department(self, department: str):
        department = self.session.query(DepartmentModel).filter(
            DepartmentModel.name == department
        ).one_or_none()
        if department is None:
            raise ValueError(f"존재하지 않는 학과입니다: {department}")

        affected = self.session.query(ProfessorModel).filter(
            ProfessorModel.department_id == department.id
        ).delete()

        return affected
