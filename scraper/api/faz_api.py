import requests
from bs4 import BeautifulSoup
import datetime


class FazApi:

    def get_all_articles_from_dates(self, start, end):
        start = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%d.%m.%Y')
        end = datetime.datetime.strptime(end, '%Y-%m-%d').strftime('%d.%m.%Y')
        print(start)
        print(end)
        page = 1
        while True:
            url = 'https://www.faz.net/suche/s' + str(page) + '.html?from=' + str(start) + '&to=' + str(end)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            objects = soup.find_all('li', {'class': 'lst-Teaser_Item'})
            link_list_len = len(objects)

            if link_list_len == 0:
                break

            for object in objects:
                new_object = object.find('a', {'class': 'js-hlp-LinkSwap js-tsr-Base_ContentLink tsr-Base_ContentLink'}, href=True).attrs['href']
                print("-------------------------------")
                print(url)
                print(new_object)

            page += 1


if __name__ == '__main__':
    faz_api = FazApi()
    faz_api.get_all_articles_from_dates(start='2020-12-31', end='2021-01-01')

