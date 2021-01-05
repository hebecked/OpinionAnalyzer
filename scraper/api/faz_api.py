import requests
from bs4 import BeautifulSoup
import datetime
from dateutil.parser import parse


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
            raise Exception("Error: " + start + " incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")
        elif not is_date(end):
            raise Exception("Error: " + end + " incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")

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

    def get_article_meta(self, url) -> {}:
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        print(soup)

        #<p class="First atc-TextParagraph" id="pageIndex_1"
        #<p class="atc-TextParagraph"
        #<h3 class="atc-SubHeadline
        #

        print('---------- Comments -----------')
        comment_response = requests.get('https://www.faz.net/aktuell/feuilleton/buecher/rezensionen/sachbuch/biographie-des-schriftstellers-leonhard-frank-17092115.html?action=commentList&page=1&onlyTopArguments=false&ot=de.faz.ArticleCommentsElement.comments.ajax.ot')
        comment_soup = BeautifulSoup(comment_response.content, 'lxml')
        print(comment_soup)

        return {}




if __name__ == '__main__':
    faz_api = FazApi()
    list_of_links = faz_api.get_all_articles_from_dates(start='2021-01-01', end='2021-01-01')
    faz_api.get_article_meta(url=list_of_links[0])


