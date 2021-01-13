import datetime
import json
from bs4 import BeautifulSoup
import urllib.request


def get_article_comments_recursively(url: str, comments: [], minimum_created: datetime.datetime) -> []:
    """
     Return a Array with comments meta data of a single article recursively in case there are more than 100
     :param url: str, url of a article
     :param comments: [], first comment batch
     :param minimum_created: datetime.datetime, minimum created date of first 100 comments
     """
    min_created_time = minimum_created.strftime("%Y-%m-%dT%H:%M:%S.%f")
    comment_url = url + '&created-cursor=' + str(min_created_time)

    with urllib.request.urlopen(comment_url) as response:
        comments_rec = response.read().decode('utf-8')

    comments_rec_json = json.loads(comments_rec)

    if len(comments_rec_json['comments']) == 0:
        return comments

    elif len(comments_rec_json['comments']) == 1:
        comments.append(comments_rec_json['comments'])
        return comments

    else:
        for comment in comments_rec_json['comments']:
            comment_created = datetime.datetime.strptime(comment['created'], "%Y-%m-%dT%H:%M:%S.%f")
            if comment_created < minimum_created:
                minimum_created = comment_created
            comments.append(comment)
        return get_article_comments_recursively(url=url, comments=comments, minimum_created=minimum_created)


class Welt:

    def __init__(self):
        self.article_url = 'https://www.welt.de/schlagzeilen/nachrichten-vom-'
        self.comment_url = 'https://api-co.la.welt.de/api/comments?document-id='

    # Use datetime.date as type for start and end str
    def get_all_articles_from_dates(self, start: datetime.datetime, end: datetime.datetime) -> []:
        """
        Return a list of all article links created in the time interval set
        :param start: str, start date of the interval in YYYY-mm-dd format
        :param end: str, end date of the interval in YYYY-mm-dd format
        """
        # Creating time interval to fetch articles from
        step = datetime.timedelta(days=1)
        dates_to_search = []
        while start <= end:
            dates_to_search.append(str(start.date()))
            start += step

        link_array = []

        for publish_date in dates_to_search:

            # Transforming publish_date variable into format to request data from welt.de
            start_date = datetime.datetime.strptime(publish_date, '%Y-%m-%d').strftime('%d-%m-%Y')

            # Retrieving all article links from time interval via the search HTML

            url = self.article_url + str(start_date) + '.html'
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
        # Retrieving full html from Url and transforming into soup
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'lxml')

        # Retrieving meta data
        article_meta_data = soup.find('script', {'data-qa': 'StructuredData', 'type': 'application/ld+json'}).contents[0]
        article_meta_data_json = json.loads(article_meta_data)

        article_meta_data_json['articleBody'] = BeautifulSoup(article_meta_data_json['articleBody'], "lxml").text

        return article_meta_data_json

    def get_article_comments(self, url: str) -> []:
        """
        Return a Array with comments meta data of a single article,
        because of API limitations it can only return maximum 100 comments per article
        :param url: str, url of a article
        """
        # https://api-co.la.welt.de/api/comments?document-id=223620336&limit=100

        try:
            article_id = url.split('article')[1].split('/')[0]
        except IndexError:
            article_id = url.split('plus')[1].split('/')[0]

        comment_url = self.comment_url + article_id + '&limit=100&sort=NEWEST'
        comments_list = []

        with urllib.request.urlopen(comment_url) as response:
            comments = response.read().decode('utf-8')

        comment_json = json.loads(comments)

        min_comment_created = datetime.datetime.now()
        for comment in comment_json['comments']:
            comment_created = datetime.datetime.strptime(comment['created'], "%Y-%m-%dT%H:%M:%S.%f")
            if comment_created < min_comment_created:
                min_comment_created = comment_created
            comments_list.append(comment)

        comments_list = get_article_comments_recursively(url=comment_url, comments=comments_list, minimum_created=min_comment_created)

        return comments_list


if __name__ == '__main__':
    welt_api = Welt()
    link_list = welt_api.get_all_articles_from_dates(start=datetime.datetime(2021,1,1), end=datetime.datetime(2021,1,1))
    print(link_list)
    for article_link in link_list:
        a_json = welt_api.get_article_meta(article_link)
        print(a_json)
    all_comments = welt_api.get_article_comments(link_list[0])
    print(all_comments)
