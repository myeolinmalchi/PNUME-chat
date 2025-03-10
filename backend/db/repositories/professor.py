from typing import List, Dict

from pgvector.sqlalchemy import SparseVector
from sqlalchemy import func
from db.common import V_DIM
from db.models import ProfessorModel, DepartmentModel
from db.models.professor import ProfessorDetailChunkModel
from db.repositories.base import BaseRepository


class ProfessorRepository(BaseRepository[ProfessorModel]):

    def create_all(self, objects):
        professors = []
        for professor in objects:
            professor_model = self.session.query(ProfessorModel).filter(ProfessorModel.url == professor.url).first()

            if not professor_model:
                professors.append(professor)
                continue

        professors = super().create_all(professors)

        return professors

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

    def search_professors_hybrid(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 5,
    ):
        """내용으로 유사도 검색"""
        score_dense = 1 - ProfessorDetailChunkModel.dense_vector.cosine_distance(
            dense_vector
        )
        score_lexical = -1 * (
            ProfessorDetailChunkModel.sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )

        score = func.max((score_lexical * lexical_ratio) + score_dense *
                         (1 - lexical_ratio)).label("score")

        query = (
            self.session.query(ProfessorModel, score).join(
                ProfessorDetailChunkModel,
                ProfessorModel.id == ProfessorDetailChunkModel.professor_id
            ).group_by(ProfessorModel.id).order_by(score.desc()).limit(k)
        )

        return query.all()
