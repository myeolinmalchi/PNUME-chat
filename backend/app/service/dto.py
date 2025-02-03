import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from services.base.embedder import EmbedResult
from typing import TypedDict, List, NotRequired

class QuestionEmbeddingsDTO(TypedDict):
    question_dense: List[float]
    quesiton_sparse: List[int, float]

class QuestionDTO(TypedDict):
    question: str
    embeddings: NotRequired[QuestionEmbeddingsDTO]