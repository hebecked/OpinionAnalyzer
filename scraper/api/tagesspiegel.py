from urllib.request import Request, urlopen
import datetime
import json
from bs4 import BeautifulSoup


class Tagesspiegel:

    def __init__(self):
        self.article_url = 'https://www.tagesspiegel.de/suchergebnis/artikel/?sw=alle&/p9049616='

    def get_all_articles_from_dates(self, start: datetime.datetime, end: datetime.datetime) -> []:
        """
        Return a list of all article links created in the time interval set

        :param start: str, start date of the intervall in YYYY-mm-dd format
        :param end: str, end date of the intervall in YYYY-mm-dd format
        """
        link_array = []

        #https://www.tagesspiegel.de/suchergebnis/artikel/?p9049616=2&sw=alle&search-fromday=1&search-frommonth=1&search-fromyear=1997&search-today=10&search-tomonth=1&search-toyear=2021

        step = datetime.timedelta(days=1)
        dates_to_search = []
        while start <= end:
            dates_to_search.append(start)
            start += step

        for publish_date in dates_to_search:
            page = 1

            url = self.article_url + str(page) + '&search-fromday=' + str(publish_date.day) + '&search-frommonth=' + str(publish_date.month) + '&search-fromyear=' + str(publish_date.year) + '&search-today=' + str(publish_date.day) + '&search-tomonth=' + str(publish_date.month) + '&search-toyear=' + str(publish_date.year)

            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            soup = BeautifulSoup(html, 'lxml')
            article_field_soup = soup.find_all('ul', {'class': 'hcf-teaser-list'})
            article_link_soup = article_field_soup.find_all('a')

            for link_spoon in article_link_soup:
                link = link_spoon.find('a', href=True).attrs['href']
                print(link)
                link_array.append(link)

        return link_array

    def get_article_meta(self, url: str) -> {}:
        """
        Return a JSON with meta data related to a single article

        :param url: str, url of a article
        """

        return {}

    def get_article_comments(self, url: str) -> []:
        """
        Return a Array with comments meta data of a single article

        :param url: str, url of a article
        """
        comments = []

        return comments


if __name__ == '__main__':
    tagesspiegel_api = Tagesspiegel()
    list_of_links = tagesspiegel_api.get_all_articles_from_dates(start=datetime.datetime(2021, 1, 1), end=datetime.datetime(2021, 1, 1))





