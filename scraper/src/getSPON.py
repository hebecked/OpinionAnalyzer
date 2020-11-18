#!/usr/bin/python
from datetime import date
import spiegel_scraper as spon



def archive(year: int, month: int, day: int):
    html = spon.archive.html_by_date(date(year, month, day))
    content = spon.archive.scrape_html(html)
    return {'content': content, 'html': html}




def article(article_url):
    html = spon.article.html_by_url(article_url)
    content = spon.article.scrape_html(html)
    return {'content': content, 'html': html}


def article_comments(article_url):
    art=article(article_url)
    return spon.comments.by_article_id(art['content']['id'])


if __name__ == '__main__':
    print(article("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8")["content"])
    print(article_comments("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8"))



