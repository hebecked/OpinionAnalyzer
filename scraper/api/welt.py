import datetime
import json
from bs4 import BeautifulSoup
from dateutil.parser import parse
import time
from selenium import webdriver
import urllib.request


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


class Welt:

    def get_all_articles_from_dates(self, start: str, end: str) -> []:
        """
        Return a list of all article links created in the time interval set
        :param start: str, start date of the intervall in YYYY-mm-dd format
        :param end: str, end date of the intervall in YYYY-mm-dd format
        """
        # Checking if date strings have correct format
        if not is_date(start):
            raise Exception(start + " (start) has incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")
        elif not is_date(end):
            raise Exception(end + "(end) has incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")

        # Creating time interval to fetch articles from
        start_interval = datetime.datetime.strptime(start, '%Y-%m-%d')
        end_interval = datetime.datetime.strptime(end, '%Y-%m-%d')
        step = datetime.timedelta(days=1)
        dates_to_search = []
        while start_interval <= end_interval:
            dates_to_search.append(str(start_interval.date()))
            start_interval += step

        link_array = []

        for publish_date in dates_to_search:

            # Transforming publish_date variable into format to request data from welt.de
            start_date = datetime.datetime.strptime(publish_date, '%Y-%m-%d').strftime('%d-%m-%Y')

            # https://www.welt.de/schlagzeilen/nachrichten-vom-1-1-2021.html

            # Retrieving all article links from time interval via the search HTML

            url = 'https://www.welt.de/schlagzeilen/nachrichten-vom-' + str(start_date) + '.html'
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'lxml')
            article_text_soup = soup.find('div', {'class': 'articles text'})
            link_soup = article_text_soup.find_all('div', {'class': 'article'})

            for link_spoon in link_soup:
                link = link_spoon.find('a', href=True).attrs['href']
                link_array.append(link)

        return link_array


    def get_article_meta(self, url: str) -> {}:
        """
        Return a JSON with meta data related to a single article
        :param url: str, url of a article
        """

        """
        # Get full content of a article on one page
        article_url = url + "?printPagedArticle=true#pageIndex_1"

        # Retrieve full article HTML and transform into soup
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'lxml')

        # Select only article meta data of article
        article_meta_data = soup.find('div', {'class': 'js-adobe-digital-data is-Invisible'}).attrs['data-digital-data']
        article_meta_data_json = json.loads(article_meta_data)
        article_meta_data_json_formatted = json.dumps(article_meta_data_json, indent=2)
        """
        print(url)
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'lxml')
        #print(soup)
        article_meta_data = soup.find('script', {'data-qa': 'StructuredData', 'type': 'application/ld+json'}).contents[0]
        article_meta_data_json = json.loads(article_meta_data)
        article_meta_data_json_formatted = json.dumps(article_meta_data_json, indent=2)
        print('----------------------------------- JSON -------------------------')
        print(article_meta_data_json_formatted)

        return article_meta_data_json_formatted

    def get_article_comments(self, url: str) -> []:
        """
        Return a Array with comments meta data of a single article
        :param url: str, url of a article
        """

        return []


if __name__ == '__main__':
    welt_api = Welt()
    link_list = welt_api.get_all_articles_from_dates(start='2021-01-01', end='2021-01-01')
    #welt_api.get_article_meta(url='https://www.welt.de/vermischtes/article223586640/Leipzig-Bundeswehr-Jeeps-in-Leipzig-angezuendet-und-ausgebrannt.html')
    for link in link_list:
        welt_api.get_article_meta(link)
