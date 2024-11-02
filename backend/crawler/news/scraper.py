from typing import Optional
from common import fetch
from models.News import News
from news.urls import urls
import re

list_selector = '#contents > div > div > div > div.board-list02 > table > tbody > tr'

def get_last_seq(url_key: str) -> Optional[int]:
    """가장 최근에 올라온 게시글 seq 반환"""
    if url_key not in urls:
        return

    parsed = fetch(urls[url_key]['path'])
    if parsed is None: 
        return

    seq: Optional[int] = None
    
    table_rows = parsed.select(list_selector)
    for row in table_rows:
        if row.has_attr('class') and row['class'][0] == 'notice':
            continue

        anchor = row.select_one('td > a:first-child')
        if anchor is None or not anchor.has_attr('href'): 
            continue

        href = str(anchor['href'])
        seq_str = re.search(r"javascript:goDetail\((.*?)\)", href)

        if seq_str != None:
            seq = int(seq_str.group(1))
            break

    return seq

detail_selectors = {
    'title': '#contents > div > div > div.board-view > dl:nth-child(1) > dd', 
    'date': '#contents > div > div > div.board-view > dl:nth-child(2) > dd', 
    'author': '#contents > div > div > div.board-view > dl:nth-child(3) > dd', 
    'attatchments': '#contents > div > div > div.board-view > dl.half-box01.none > dd', 
    'contents': '#contents > div > div > div.board-contents.clear',
}

def get_detail(url_key: str, seq: int) -> Optional[News]:
    """게시글 세부 정보 추출"""
    if url_key not in urls:
        return

    path = urls[url_key]['path']
    db = urls[url_key]['db']

    parsed = fetch(f"{path}?db={db}&seq={seq}&page_mode=view")
    if parsed is None: 
        return

    result: News = {
        'title': '', 
        'date': '', 
        'author': '', 
        'attatchments': [], 
        'contents': '',
    }

    for key, selector in detail_selectors.items():
        element = parsed.select_one(selector)
        if key != 'attatchments':
            result[key] = '' if element is None else element.text
            continue

        if element is None: 
            continue

        temp = []
        anchors = element.select('a')
        for a in anchors:
            temp.append({ 'name': a.text, 'link': a['href'][0] })
            
        result[key] = temp

    return result

