import os, sys

import asyncio
from typing import TypedDict, List, Dict
from aiohttp import ClientSession

from dto import QuestionDTO, QuestionEmbeddingsDTO
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.base.embedder import BaseEmbedder, EmbedResult

load_dotenv()

EMBED_URL = os.environ.get("EMBED_URL")

class QuestionEmbedder(BaseEmbedder[QuestionDTO]):
    pass 