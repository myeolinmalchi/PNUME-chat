from db.models import DepartmentModel, MajorModel, UniversityModel
from db.repositories.base import BaseRepository


class UniversityRepository(BaseRepository[UniversityModel]):

    def create_all(self, objects):
        results = []
        for univ in objects:
            univ_model = self.session.query(UniversityModel).filter(
                UniversityModel.name == univ.name
            ).first()

            if not univ_model:
                result = super().create(univ)
                results.append(result)
                continue

            departments = []
            for d in univ.departments:
                exists = self.session.query(DepartmentModel).filter(
                    DepartmentModel.name == d.name
                ).first()

                if exists:
                    continue

                d.university_id = univ_model.id
                departments.append(d)

            self.session.add_all(departments)
            self.session.flush()
            self.session.refresh(univ_model)

            results.append(univ_model)

        return results

    def find_department_by_name(self, name: str):
        result = self.session.query(DepartmentModel).where(
            DepartmentModel.name == name
        ).first()

        if not result:
            raise ValueError(f"존재하지 않는 학과입니다. ({name})")

        return result

    def find_major(self, department: str, name: str):
        department_model = self.session.query(DepartmentModel).filter(
            DepartmentModel.name == department
        ).first()

        if not department_model:
            raise ValueError(f"존재하지 않는 학과입니다. ({department})")

        major_model = self.session.query(MajorModel).filter(
            MajorModel.name == name
        ).first()

        if not major_model:
            major_model = MajorModel(
                name=name, department_id=department_model.id
            )

            self.session.add(major_model)
            self.session.flush()
            self.session.refresh(major_model)

        return major_model
