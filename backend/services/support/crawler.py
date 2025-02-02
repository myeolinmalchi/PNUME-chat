from services.base.crawler import BaseCrawler
from markdownify import markdownify as md

from services.support.dto import SupportDTO

SELECTORs = {"attachments": ".message-body", "info-text": ".info-text", "cards": ".card"}

DOMAIN = "https://onestop.pusan.ac.kr"


class SupportCrawler(BaseCrawler):

    def _parse_detail(self, dto, soup):
        """학지시 상세 내용 파싱"""

        # 첨부파일 파싱
        att_element = soup.select_one(SELECTORs["attachments"])
        _attachments = []
        if att_element:
            for div in att_element.select("div"):
                name = self._preprocess_text(div.text)

                anchor = div.select_one("a:nth-child(2)")
                if not anchor or not anchor.has_attr("href"):
                    continue

                path = self._preprocess_text(str(anchor["href"]))
                _attachments.append({"name": name, "url": f"{DOMAIN}{path}"})

        # 상세 내용 파싱
        info_texts = soup.select(SELECTORs["info-text"])

        total_info_text = []
        for info_text in info_texts:
            temp = self._preprocess_text(info_text.text)
            total_info_text.append(temp)

        info_text = " ".join(total_info_text)

        cards = soup.select(SELECTORs["cards"])

        contents = []
        for card in cards:
            content = ""
            header = card.select_one(".card-header > button")
            if header:
                content = self._preprocess_text(header.text)

            body = card.select_one(".card-body")
            if not body:
                continue

            body_ = self._preprocess_text(md(body.text))
            content = content + " " + body_

            contents.append(content)

        content = "\n".join(contents)
        _info = {**dto["info"], "content": content}
        _dto = {"info": _info, "attachments": _attachments, "url": dto["url"]}

        return SupportDTO(**_dto)
