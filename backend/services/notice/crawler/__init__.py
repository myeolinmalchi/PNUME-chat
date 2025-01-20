from typing import Literal
from .me import *
from .base import *
from .default import *


def create_notice_crawler(_type: Literal["default", "me"] = "default"):
    match _type:
        case "default":
            Crawler = NoticeCrawler
        case "me":
            Crawler = NoticeMECrawler

    notice_crawler = Crawler()
    return notice_crawler
