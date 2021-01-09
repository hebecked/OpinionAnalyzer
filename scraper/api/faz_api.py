import requests
import datetime
import json
from bs4 import BeautifulSoup
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


class Faz:

    def get_all_articles_from_dates(self, start: str, end: str) -> []:
        """
        Return a list of all article links created in the time interval set

        :param start: str, start date of the intervall in YYYY-mm-dd format
        :param end: str, end date of the intervall in YYYY-mm-dd format
        """

        # Checking if date string have correct format
        if not is_date(start):
            raise Exception(start + " (start) has incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")
        elif not is_date(end):
            raise Exception(end + "(end) has incorrect format. Please use format \'%YYYY-mm-dd\' as input format!")

        link_array = []

        # Transforming start and end date into format to request data from faz.net
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%d.%m.%Y')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').strftime('%d.%m.%Y')

        # Retrieving all article links from time interval via the search HTML
        page = 1
        while True:
            url = 'https://www.faz.net/suche/s' + str(page) + '.html?from=' + str(start_date) + '&to=' + str(end_date)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            link_soup = soup.find_all('li', {'class': 'lst-Teaser_Item'})

            if len(link_soup) == 0:
                break

            for link_spoon in link_soup:
                article_link = link_spoon.find('a', {'class': 'js-hlp-LinkSwap js-tsr-Base_ContentLink tsr-Base_ContentLink'}, href=True).attrs['href']
                if article_link not in link_array:
                    link_array.append(article_link)

            page += 1

        return link_array

    def get_article_meta(self, url: str) -> {}:
        """
        Return a JSON with meta data related to a single article

        :param url: str, url of a article
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

        return article_meta_data_json_formatted

    def get_article_body_meta(self, url: str) -> {}:
        """
        Return a JSON with body meta data (including article text) related to a single article

        :param url: str, url of a article
        """

        # Get full content of a article on one page
        article_url = url + "?printPagedArticle=true#pageIndex_1"

        # Retrieve full article HTML and transform into soup
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'lxml')

        # Select only body meta data of article
        article_body_data = soup.find_all('script', {'type': 'application/ld+json'})
        article_body_meta_data = article_body_data[1].contents[0].rstrip("\n").rstrip("\t").strip()
        article_body_meta_data_json = json.loads(article_body_meta_data)
        article_body_meta_data_json_formatted = json.dumps(article_body_meta_data_json, indent=2)

        return article_body_meta_data_json_formatted

    def get_article_comments(self, url: str) -> []:
        """
        Return a Array with comments meta data of a single article

        :param url: str, url of a article
        """

        # Load javascript only with comments
        url = url + "?action=commentList&page=1&onlyTopArguments=false&ot=de.faz.ArticleCommentsElement.comments.ajax.ot"

        # Retrieve comments page of article and transform it into soup
        comment_response = requests.get(url)
        comment_soup = BeautifulSoup(comment_response.content, 'lxml')

        # Select from soup the parts where title, body of comment and the comment timestamp is saved
        comment_title_soup = comment_soup.find_all('p', {'class': 'js-lst-Comments_CommentTitle lst-Comments_CommentTitle'})
        comment_body_soup = comment_soup.find_all('p', {'class': 'lst-Comments_CommentText'})
        comment_timestamp_soup = comment_soup.find_all('span', {'class': 'lst-Comments_CommentInfoDateText'})

        # Safety mechanism in case there are pages which have comments with no title
        if len(comment_title_soup) != len(comment_body_soup):
            raise Exception("The number of comment bodies is not equal to the number of commen titles in + " + url)

        # Clean meta data and create array for comments meta data in order
        comments = []
        i = 0
        while i < len(comment_body_soup) and i < len(comment_title_soup):
            contents = "".join(str(item) for item in comment_title_soup[i].contents)
            comment_title_cleaned = contents.replace("\n", ' ').replace("\t", ' ').rstrip("<br/>").rstrip("<br/").strip()

            contents_body = "".join(str(item) for item in comment_body_soup[i].contents)
            comment_body_cleaned = contents_body.replace("\n", ' ').replace("\t", ' ').replace("<br/>", '').replace("<br/", '').strip()

            contents_time = comment_timestamp_soup[i].contents[0]
            contents_german_day = contents_time.split(' - ')[0]
            contents_day = datetime.datetime.strptime(contents_german_day, '%d.%m.%Y').strftime('%Y-%m-%d')
            contents_timestamp = contents_day + ' ' + contents_time.split(' - ')[1]

            comment = {
                "title": comment_title_cleaned,
                "body": comment_body_cleaned,
                "commented_at": contents_timestamp
            }

            comments.append(comment)
            i += 1

        return comments




if __name__ == '__main__':
    faz_api = Faz()
    list_of_links = faz_api.get_all_articles_from_dates(start='2021-01-01', end='2021-01-01')
    for link in list_of_links:
        print(link)
        try:
            article_meta = faz_api.get_article_meta(url=link)
            article_body_meta = faz_api.get_article_body_meta(url=link)
            article_comments = faz_api.get_article_comments(url=link)
            print(article_comments)
        except IndexError:
            print("non regular article")




