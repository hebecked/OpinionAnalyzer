import urllib.request
import datetime
import json
from bs4 import BeautifulSoup


class Faz:

    def __init__(self):
        self.article_url = 'https://www.faz.net/suche/s'
        self.full_page_url = '?printPagedArticle=true#pageIndex_1'
        self.all_comments_url = """?action=commentList&page={}&onlyTopArguments=false&ot=de.faz.ArticleCommentsElement.comments.ajax.ot"""

    def get_all_articles_from_dates(self, start: datetime.datetime, end: datetime.datetime) -> []:
        """
        Return a list of all article links created in the time interval set

        :param start: str, start date of the intervall in YYYY-mm-dd format
        :param end: str, end date of the intervall in YYYY-mm-dd format
        """
        link_array = []

        # Transforming start and end date into format to request data from faz.net
        start_date = start.strftime('%d.%m.%Y')
        end_date = end.strftime('%d.%m.%Y')

        # Retrieving all article links from time interval via the search HTML
        page = 1
        while True:
            url = self.article_url + str(page) + '.html?from=' + str(start_date) + '&to=' + str(end_date)
            with urllib.request.urlopen(url) as response:
                article_response = response.read().decode('utf-8')
            soup = BeautifulSoup(article_response, 'lxml')
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
        article_url = url + self.full_page_url

        # Retrieve full article HTML and transform into soup
        with urllib.request.urlopen(article_url) as response:
            article_response = response.read().decode('utf-8')
        soup = BeautifulSoup(article_response, 'lxml')

        try:
            # Select only article meta data of article
            article_meta_data = soup.find('div', {'class': 'js-adobe-digital-data is-Invisible'}).attrs['data-digital-data']
            article_meta_data_json = json.loads(article_meta_data)

            article_body_data = soup.find_all('script', {'type': 'application/ld+json'})
            article_body_meta_data = article_body_data[1].contents[0].rstrip("\n").rstrip("\t").strip()
            article_body_meta_data_json = json.loads(article_body_meta_data)

            meta = {
                "article_meta": article_meta_data_json,
                "article_body_meta": article_body_meta_data_json
            }
            return meta

        except IndexError:
            return {}

    def get_article_comments(self, url: str) -> []:
        """
        Return a Array with comments meta data of a single article

        :param url: str, url of a article
        """

        # Load javascript only with comments
        pagecount = 1
        comments = []

        while True:
            try:
                cmt_url = url + self.all_comments_url.format(pagecount)
                # Retrieve comments page of article and transform it into soup
                with urllib.request.urlopen(cmt_url) as response:
                    comment_response = response.read().decode('utf-8')
                comment_soup = BeautifulSoup(comment_response, 'lxml')
            except:
                break
            # Select from soup the parts where title, body of comment and the comment timestamp is saved,
            # differentiated by comment level (if reply of comment or not)

            comment_first_level_soup = comment_soup.find_all('li', {'class': 'js-lst-Comments_Item lst-Comments_Item lst-Comments_Item-level1'})
            if not comment_first_level_soup:
                break
            comments += self.get_comment_data(comment_first_level_soup, 0)
            if len(comment_first_level_soup) < 20:
                break
            pagecount += 1
        return comments

    def get_comment_data(self, comment_soup, level):
        comments = []

        for cmt in comment_soup:
            title_soup = cmt.find('p', {'class': 'js-lst-Comments_CommentTitle lst-Comments_CommentTitle'})
            title_contents = "".join(str(item) for item in title_soup.contents)
            comment_title_cleaned = title_contents.replace("\n", ' ').replace("\t", ' ').rstrip("<br/>").rstrip("<br/").strip()

            body_soup = cmt.find('p', {'class': 'lst-Comments_CommentText'})
            body_contents = "".join(str(item) for item in body_soup.contents)
            comment_body_cleaned = body_contents.replace("\n", ' ').replace("\t", ' ').replace("<br/>", '').replace("<br/", '').strip()

            author_soup = cmt.find('span', {'class': 'lst-Comments_CommentInfoNameText'})
            author_contents = "".join(str(item) for item in author_soup.contents)
            comment_author_cleaned = author_contents.replace("\n", ' ').replace("\t", ' ').replace("<br/>", '').replace("<br/", '').strip()

            created_at_soup = cmt.find('span', {'class': 'lst-Comments_CommentInfoDateText'})
            contents_time = created_at_soup.contents[0]
            contents_german_day = contents_time.split(' - ')[0]
            contents_day = datetime.datetime.strptime(contents_german_day, '%d.%m.%Y').strftime('%Y-%m-%d')
            contents_timestamp = contents_day + ' ' + contents_time.split(' - ')[1]

            comment = {
                "title": comment_title_cleaned,
                "body": comment_body_cleaned,
                "author": comment_author_cleaned,
                "created_at": contents_timestamp,
                "level": level
            }
            if level == 0:
                comment_second_level_soup = cmt.find_all('li',
                                        {'class': 'js-lst-Comments_Item lst-Comments_Item lst-Comments_Item-level2'})
                sub_comments = self.get_comment_data(comment_second_level_soup, level+1)
                if sub_comments:
                    comment["replies"] = sub_comments
            comments.append(comment)

        return comments


if __name__ == '__main__':
    faz_api = Faz()
    list_of_links = faz_api.get_all_articles_from_dates(start=datetime.datetime(2021, 1, 1), end=datetime.datetime(2021, 1, 1))
    art = []
    cmt = []
    for link in list_of_links:
        print(link)
        article_meta = faz_api.get_article_meta(url=link)
        art += [article_meta]
        print(article_meta)
        article_comments = faz_api.get_article_comments(url=link)
        cmt += [article_comments]
        print(article_comments)




