from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
from config.logger import _logger

logger = _logger(__name__)


def preprocess_text(text: str):
    """Clean plain text"""

    import re
    text = re.sub(r"\\+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\t", " ", text)
    text = re.sub(r"\r", " ", text)
    exclude_base64 = re.compile(r"data:image/[a-zA-Z]+;base64,[^\"']+")
    text = re.sub(exclude_base64, "", text)
    re.sub(r"\s+", " ", text).strip()
    return text


def clean_html(html: str | BeautifulSoup) -> BeautifulSoup:
    """Clean html string or `BeautifulSoup` instance"""

    match html:
        case str():
            html = html.replace("<br/>", " ")
            html = html.replace("<br />", " ")
            html = html.replace("<br>", " ")
            soup = BeautifulSoup(html, "html.parser")
        case BeautifulSoup():
            soup = html

    while True:
        affected = sum([
            _clean_html_tag(soup, child)
            if isinstance(child, Tag) else _clean_html_string(soup, child)
            for child in list(soup.descendants)
        ])

        if affected == 0:
            break

    return soup


def _clean_html_string(soup: BeautifulSoup, element: PageElement) -> int:
    """Clean `NavigableString` instance"""
    if not element.parent and element != soup:
        return 0

    if len(element.text) == 0 or all(c == " " for c in element.text):
        element.extract()
        return 1

    return 0


def _clean_html_tag(soup: BeautifulSoup, element: Tag) -> int:
    """Clean `Tag` instance"""

    if not element.parent and element != soup:
        return 0

    affected = 0

    children = list(element.children)
    only_string = all(isinstance(child, NavigableString) for child in children)

    if only_string and len(children) > 1:
        inner_texts = [child.text for child in children]
        combined_text = ''.join(inner_texts)

        element.clear()
        element.append(NavigableString(combined_text))

        affected += 1

    match element:
        case Tag(name="a", attrs={"href": str(href)}):
            if not href.startswith("#"):
                return affected
            target = soup.select_one(href)
            if not target:
                return affected
            target.extract()
            element.replace_with(target)
            return affected + 1
        case Tag(
            name="span" | "p" | "u" | "b" | "strong",
            parent=Tag(name="span" | "p" | "td" | "li" | "td" | "th" | "b")
        ):
            if not only_string:
                return affected
            inner_text = element.get_text(strip=True)
            element.replace_with(NavigableString(inner_text))
            return affected + 1
        case Tag(name="img"):
            element.extract()
            return affected + 1
        case _ if len(children) == 0 or element.string == "":
            element.extract()
            return affected + 1
        case _:
            return affected
