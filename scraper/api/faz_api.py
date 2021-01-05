import requests
from bs4 import BeautifulSoup

class FazApi:


    def get_all_articles_from_date():
        link_list_len = None
        print(link_list_len)
        page = 1
        while True:
            url = 'https://www.faz.net/suche/s' + str(page) + '.html?from=01.01.2021&to=01.01.2021'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            objects = soup.find_all('li', {'class': 'lst-Teaser_Item'})
            link_list_len = len(objects)

            if link_list_len == 0:
                break

            for object in objects:
                new_object = object.find('a', href=True).attrs['href']
                print("-------------------------------")
                print(new_object)

            page += 1


if __name__ == '__main__':
    faz_api = FazApi
    faz_api.get_all_articles_from_date()

