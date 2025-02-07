import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from services.base.embedder import EmbedResult
from typing import TypedDict, List, NotRequired, Dict

class QuestionEmbeddingsDTO(TypedDict):
    question_dense: List[float]
    quesiton_sparse: Dict[int, float]

class QuestionDTO(TypedDict):
    question: str
    embeddings: NotRequired[QuestionEmbeddingsDTO]


if __name__ == "__main__":
    dtoTest = QuestionDTO(embeddings=QuestionEmbeddingsDTO(question_dense=[1,2,3]))
    test = dtoTest.get("embeddings").get("question_dense")
    print(test)
    print(dtoTest["embeddings"]["question_dense"])