import os
import asyncio
from typing import TypedDict, List

from aiohttp import ClientSession

from app.service.dto import QuestionDTO, QuestionEmbeddingsDTO

from services.base import BaseEmbedder
from dotenv import load_dotenv

load_dotenv()

EMBED_URL = os.environ.get("EMBED_URL")

class QuestionEmbedResult(TypedDict):
    dense: List[float]
    sparse: List[int, float]

class QuestionEmbedder(BaseEmbedder[QuestionDTO]):

    async def _embed_dto_async(self, item: QuestionDTO, session: ClientSession) -> QuestionEmbeddingsDTO:
        
