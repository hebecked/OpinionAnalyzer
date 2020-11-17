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


def article_comments(article_id: str):
    return spon.comments.by_article_id(article_id)


if __name__ == '__main__':
    print(article("https://www.spiegel.de/politik/ausland/barack-obama-soll-angela-merkel-zu-vierter-amtszeit-gedraengt-haben-a-1244446.html")["content"])
    #print(article_comments("1244446")) Throws error !!!



