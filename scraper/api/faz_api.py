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
            print("Error: " + start + " has not the correct format. Please use format \'%YYYY-mm-dd\' as input format!")
            raise Exception("DateError")
        elif not is_date(end):
            print("Error: " + end + " has not the correct format. Please use format \'%YYYY-mm-dd\' as input format!")
            raise Exception("DateError")

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

        print(link_array)
        return link_array


if __name__ == '__main__':
    faz_api = FazApi()
    list_of_links = faz_api.get_all_articles_from_dates(start='202012-31', end='2021-01-01')

