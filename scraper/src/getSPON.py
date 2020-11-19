#!/usr/bin/python
from datetime import date, timedelta
import spiegel_scraper as spon



def archive(year: int, month: int, day: int):
    html = spon.archive.html_by_date(date(year, month, day))
    content = spon.archive.scrape_html(html)
    return {'content': content, 'html': html}

def fetchURLs(start:date, end:date):
    #get all articles from archive between corresponding start and end date 
    num_of_days=(start-end).days
    date_list=[(timedelta(i)+date.today()) for i in range(num_of_days,1)]
    full_list=[]
    for dt in date_list:
        full_list+=(spon.archive.scrape_html(spon.archive.html_by_date(dt)))
#    time.sleep(2) #remove comment for crawler delay
    url_list=list(filter(lambda x: x['is_paid']==False,full_list)) #remove paid aricles
    return([article['url'] for article in url_list])
  
def article(article_url):
    html = spon.article.html_by_url(article_url)
    content = spon.article.scrape_html(html)
    return {'content': content, 'html': html}


def article_comments(article_url):
    art=article(article_url)
    return spon.comments.by_article_id(art['content']['id'])

def runTest():
    test_article=article("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8")["content"]
    test_comments=article_comments("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8")
    start=date(2020,11,1)
    end=date(2020,11,1)
    for url in fetchURLs(start,end):
        print(url,end="\n")
    print("\narticle structure:")
    print(test_article.keys())
    print("\ncomment structure:")
    print(test_comments[0].keys())   

if __name__ == '__main__':
    runTest()