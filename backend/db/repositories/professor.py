from db.models import MajorModel
from db.models.professor import ProfessorModel
from db.repositories.base import BaseRepository


class ProfessorRepository(BaseRepository[ProfessorModel]):
    """
    def find_major_minor(self, major: str, minor: MinorModel):
        major_instance = self.session.query(MajorModel).where(
            MajorModel.name == major
        ).one_or_none()

        if not major_instance:
            major_instance = MajorModel(name=major)
            self.session.add(major_instance)
            self.session.flush()

        minor_instance = self.session.query(MinorModel).where(
            (MinorModel.name == minor)
            & (MinorModel.major_id == major_instance.id)
        ).one_or_none()

        if not minor_instance:
            minor_instance = MinorModel(name=minor, major_id=major_instance.id)
            self.session.add(minor_instance)
            self.session.flush()

        return {"major_id": major_instance.id, "minor_id": minor_instance.id}
    """
