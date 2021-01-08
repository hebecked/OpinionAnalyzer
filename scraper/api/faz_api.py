import requests
from bs4 import BeautifulSoup
import datetime
from dateutil.parser import parse
import json


def is_date(string: str, fuzzy=False) -> bool:
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


class FazApi:

    def get_all_articles_from_dates(self, start: str, end: str) -> []:
        if not is_date(start):
            raise Exception(start + " (start) has incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")
        elif not is_date(end):
            raise Exception(end + "(end) has incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")

        link_array = []
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%d.%m.%Y')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').strftime('%d.%m.%Y')
        page = 1
        while True:
            url = 'https://www.faz.net/suche/s' + str(page) + '.html?from=' + str(start_date) + '&to=' + str(end_date)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            objects = soup.find_all('li', {'class': 'lst-Teaser_Item'})
            link_list_len = len(objects)

            if link_list_len == 0:
                break

            for object in objects:
                link = object.find('a', {'class': 'js-hlp-LinkSwap js-tsr-Base_ContentLink tsr-Base_ContentLink'}, href=True).attrs['href']
                if link not in link_array:
                    link_array.append(link)

            page += 1

        return link_array

    def get_article_meta(self, url: str) -> {}:
        article_url = url + "?printPagedArticle=true#pageIndex_1"
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'lxml')

        article_meta = soup.find('div', {'class': 'js-adobe-digital-data is-Invisible'}).attrs['data-digital-data']
        article_meta_json = json.loads(article_meta)
        article_meta_json_formatted = json.dumps(article_meta_json, indent=2)

        return article_meta_json_formatted

    def get_article_body_meta(self, url: str) -> {}:
        article_url = url + "?printPagedArticle=true#pageIndex_1"
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'lxml')
        article_body = soup.find_all('script', {'type': 'application/ld+json'})
        article_body_meta = article_body[1].contents[0].rstrip("\n").rstrip("\t").strip()
        article_body_meta_json = json.loads(article_body_meta)
        article_body_meta_json_formatted = json.dumps(article_body_meta_json, indent=2)

        return article_body_meta_json_formatted

    def get_article_comments(self, url: str) -> []:

        print('---------- Comments -----------')
        comment_response = requests.get('https://www.faz.net/aktuell/feuilleton/buecher/rezensionen/sachbuch/biographie-des-schriftstellers-leonhard-frank-17092115.html?action=commentList&page=1&onlyTopArguments=false&ot=de.faz.ArticleCommentsElement.comments.ajax.ot')
        comment_soup = BeautifulSoup(comment_response.content, 'lxml')
        print(comment_soup)
        comment_title_soup = comment_soup.find_all('p', {'class': 'js-lst-Comments_CommentTitle lst-Comments_CommentTitle'})
        comment_body_soup = comment_soup.find_all('p', {'class': 'lst-Comments_CommentText'})

        print(comment_title_soup)
        print(comment_body_soup)


        return []




if __name__ == '__main__':
    faz_api = FazApi()
    list_of_links = faz_api.get_all_articles_from_dates(start='2021-01-01', end='2021-01-01')
    article_meta = faz_api.get_article_meta(url=list_of_links[0])
    article_body_meta = faz_api.get_article_body_meta(url=list_of_links[0])
    article_comments = faz_api.get_article_comments(url=list_of_links[0])


