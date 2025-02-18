from typing import List
from bs4 import Tag
from bs4.element import NavigableString
from services.base.crawler.crawler import BaseCrawler

from services.notice.dto import AttachmentDTO
from services.support.dto import SupportDTO
from services.base.crawler import preprocess

DOMAIN = "https://onestop.pusan.ac.kr"


class SupportCrawler(BaseCrawler):

    def _parse_detail(self, soup):
        """학지시 상세 내용 파싱"""

        pages = soup.select("div.tab-content > div.tab-pane")

        attachments: List[AttachmentDTO] = []
        content = ""

        for idx, page in enumerate(pages):
            nav_element = page.select_one(f"a#tab{idx}")
            if not nav_element:
                continue

            heading = nav_element.get_text(strip=True)
            heading_element = soup.new_tag(name="h2", string=heading)

            message_section = page.find("message-box message-body", recursive=False)
            file_section = page.select_one("#file_tabs2")
            content_section = page.select_one("accordian")

            if not content_section:
                continue

            if file_section:
                for e in file_section.select(".my-2"):
                    anchor = e.select("a")[-1]
                    if not anchor.has_attr("href"):
                        continue

                    name_element = next(e.children)
                    if not isinstance(name_element, NavigableString):
                        continue

                    attachments.append({
                        "name": name_element.string,
                        "url": f"{DOMAIN}{anchor['href']}",
                    })

            if isinstance(message_section, Tag):
                message_section.extract()
                content_section.insert(0, message_section)

            content_section.insert(0, heading_element)
            content += "\n" + str(preprocess.clean_html(str(content_section)))

        dto = {"info": {"content": content}, "attachments": attachments}
        return SupportDTO(**dto)
