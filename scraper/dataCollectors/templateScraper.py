#!/usr/bin/python
from datetime import date


class Scraper:

    def __init__(self):
        self.name = None  #
        self.id = None
        # todo add database connection as class object?
        # todo add local copy of database elements (urls) to compare with crawler results
        # todo add id of source for use in database querys (e.g Spiegel, ZEIT)
        pass

    def getArticlesList(self, start: date = date(1900, 1, 1), end: date = date.today()):
        """
        

        Parameters
        ----------
        start : date, optional
            DESCRIPTION. The default is date(1900,1,1).
        end : date, optional
            DESCRIPTION. The default is date.today().

        Returns
        -------
        List of corresponding URLs from this source in string format

        """
        pass

    def getArticle(self, article_url):
        pass

    def getCommentsForArticle(self, article_url, start: date = date(1900, 1, 1), end: date = date.today()):
        pass

    # switch following functionality to database object?
    def _alreadyInDB(self, article_url):
        pass

    def _getArticlesFromDB(self):
        pass

    def writeArticleToDB(self):
        pass

    def __del__(self):
        # call __del__ for subclass
        pass


if __name__ == '__main__':
    pass
