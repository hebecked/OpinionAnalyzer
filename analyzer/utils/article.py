# -*- coding: utf-8 -*-
# todo: open tasks marked with todo

import copy  # deepcopy used for oldBody
import datetime as dt
import validators  # used for url validation
from utils.connectDb import Database as ownDBObject


class Article:
    # static data related database queries
    __SQL_UDFS_FETCH_FEASIBLE = """SELECT udf_name,id FROM news_meta_data.udf_header;"""
    __SQL_SOURCES_FETCH_FEASIBLE = """SELECT id,source FROM news_meta_data.source_header;"""

    __source_list = None
    __udf_dict = None
    # mandatory database fields to be checked before writing
    MANDATORY_HEADER = {"url", "obsolete", "source_id"}
    MANDATORY_BODY = {"article_id", "headline", "body", "proc_timestamp", "proc_counter"}

    # Article class constants (given by database entries / restrictions)
    OBJECT_TYPE = 1  # article - more robust: fetch from database
    MAX_URL_LENGTH = 2048
    MAX_HEADLINE_LENGTH = 200
    MAX_UDF_LENGTH = 80

    def __init__(self):
        """
        article object for use with all scrapers \n
        manages article components for several database tables \n
        
        sub objects are "header", "body", "udfs". \n
        they organize the data for the corresponding database tables. \n
        objects to be retrieved by .getArticle()["header"] e.g. \n        
        
        
        free to use data storage .free_data with no predefined type or usage \n
 
        """
        self.__header_complete = False
        self.__body_complete = False
        if Article.__udf_dict is None or Article.__source_list is None:
            Article.__source_list = []
            Article.__udf_dict = {}
#            print("first launch, setting class variables")  # todo delete line (debugging purposes only)
            # todo database connection to be rewritten later
            db = ownDBObject()
            db.connect()
            udf_header = db.retrieveValues(Article.__SQL_UDFS_FETCH_FEASIBLE)
            Article.__udf_dict = dict(zip((udf[0] for udf in udf_header), (udf[1] for udf in udf_header)))
#            print("udf Dict: ", Article.__udf_dict)  # todo delete line (debugging purposes only)
            sources = db.retrieveValues(Article.__SQL_SOURCES_FETCH_FEASIBLE)
            Article.__source_list = list(source[0] for source in sources)
#            print("sourceList ", Article.__source_list)  # todo delete line (debugging purposes only)
            db.close()
        self.__header = {"obsolete": False, "source_date": None}
        self.__body = {"proc_counter": 0}
        self.__old_body = {}
        self.__udfs = set([])
        self.__in_db = False
        self.free_data = None

    def __del__(self):
        self.__header_complete = False
        self.__body_complete = False

    # header setter functions
    def set_header_id(self, header_id: int) -> bool:
        """
        

        Parameters
        ----------
        header_id : int
            Corresponding to database field id in article_header table\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(header_id) == int and header_id > 0:
            self.__header["id"] = header_id
            self.__body["article_id"] = header_id
            self.__in_db = True
            return True
        return False

    def set_url(self, url: str) -> bool:
        """
        

        Parameters
        ----------
        url : str
            Corresponding to database field url in article_header table.\n
            Provide validated url format. Function will validate and reject.

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(url) == str and validators.url(url) and len(url) < Article.MAX_URL_LENGTH:
            self.__header["url"] = url
            return True
        return False

    def set_obsolete(self, obsolete: bool) -> bool:
        """
        

        Parameters
        ----------
        obsolete : bool
            Corresponding to database field obsolete in article_header table.\n
            Set True to exclude url from crawling

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(obsolete) == bool:
            self.__header["obsolete"] = obsolete
            return True
        return False

    def set_source(self, source_id: int) -> bool:
        """
        

        Parameters
        ----------
        source_id : int
            Corresponding to database field obsolete in article_header table.\n
            source_id will be validated as existant in database

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(source_id) == int and source_id > 0 and source_id in Article.__source_list:
            self.__header["source_id"] = source_id
            return True
        return False

    def set_header_date(self, date_published: dt.date) -> bool:
        """
        

        Parameters
        ----------
        date_published : datetime.date
            Corresponding to database field source_date in article_header table.\n
            will be validated as datetime.date and converted to string automatically

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(date_published) == dt.date:
            self.__header["source_date"] = date_published.isoformat()
            return True
        return False

    # Body setter functions
    def set_body_id(self, body_id: int) -> bool:
        """
        

        Parameters
        ----------
        body_id : int
            Corresponding to database field id in article_body table\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(body_id) == int and body_id > 0:
            self.__body["id"] = body_id
            return True
        return False

    def set_body_article_id(self, body_article_id: int) -> bool:
        """
        

        Parameters
        ----------
        body_article_id : int
            Corresponding to database field id in article_header table and database field article_id in table article_body\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(body_article_id) == int and body_article_id > 0:
            self.__body["article_id"] = body_article_id
            return True
        return False

    def set_body_text(self, body_text: str) -> bool:
        """
        

        Parameters
        ----------
        body_text : str
            Corresponding to database field body in article_body table\n
            full Article text to be inserted here

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(body_text) == str:
            self.__body["body"] = body_text
            return True
        return False

    def set_body_headline(self, body_headline: str) -> bool:
        """
        

        Parameters
        ----------
        body_headline : str
            Corresponding to database field headline in article_body table\n
            headline length is cappen at MAX_HEADLINE_LENGTH (corresponding to database layout)

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(body_headline) == str and len(body_headline) <= Article.MAX_HEADLINE_LENGTH:
            self.__body["headline"] = body_headline
            return True
        return False

    def set_body_timestamp(self, body_timestamp: dt.datetime = dt.datetime.today()) -> bool:
        """
        

        Parameters
        ----------
        body_timestamp : datetime.datetime, optional
            Corresponding to database field proc_timestamp in article_body table\n
            When did the crawler add this Article text (version)\n
            The default is datetime.datetime.today()

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(body_timestamp) == dt.datetime:
            self.__body["proc_timestamp"] = body_timestamp.replace(microsecond=0).isoformat()
            return True
        return False

    def set_body_counter(self, body_counter: int) -> bool:
        """
        

        Parameters
        ----------
        body_counter : int
            Corresponding to database field proc_counter in article_body table\n
            set =0 with Article cration and therefore only strictly positive values are allowed\n
            manages the time till revisit of already seen articles\n
            next visit = proc_timestamp + 1 hour * (pow(2,bodyCounter)-1), so set carefully\n
            value of 0 for new articles

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(body_counter) == int and body_counter > 0:
            self.__body["proc_counter"] = body_counter
            return True
        return False

    def set_body_old(self) -> bool:
        """
        function moves current Article body data to old Article body data (deepcopy) and creates new empty body element\n
        intended to be called after import (old) body data fromn database

        Returns
        -------
        bool
            returns True if successful.

        """

        if self.check_body_complete():
            self.__old_body = copy.deepcopy(self.__body)
            self.__body = {"proc_counter": 0, "article_id": self.__old_body["article_id"]}
            return True
        return False

    def add_udf(self, key: str, value: str) -> bool:
        """
        udfs have to be set separately one by one
        important: udf key converted to udf_id internally 

        Parameters
        ----------
        key : str
            name of udf - for insertion only, converted for internal use
        value : str
            value (string) of udf field\n
            length limited to MAX_UDF_LENGTH (corresponding to database layout)

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(key) == str and key in Article.__udf_dict.keys() and type(value) == str and len(
                value) <= Article.MAX_UDF_LENGTH:
            self.__udfs |= {(Article.__udf_dict[key], value)}
            return True
        return False

    def check_header_complete(self):
        """
        validation of completeness of header data\n
        comparision with set MANDATORY_HEADER

        Returns
        -------
        specific
            True if complete
            (false, set of missing fields) if incomplete

        """
        # checking for data in all mandatory database fields
        # return Value: True=ok, otherwise (False, missing data)
        missing = Article.MANDATORY_HEADER - self.__header.keys()
        if not missing:
            return True
        return tuple([False, missing])

    def set_header_complete(self) -> bool:
        """
        check if complete and set internal state

        Returns
        -------
        bool
            True if complete, False if incomplete

        """
        if self.check_header_complete() is True:  # neccessary as 'if tuple' is interpreted as True
            self.__header_complete = True
            return True
        return False

    def check_body_complete(self):
        """
        validation of completeness of body data \n
        comparision with set MANDATORY_BODY

        Returns
        -------
        specific
            True if complete
            (false, set of missing fields) if incomplete

        """
        missing = Article.MANDATORY_BODY - self.__body.keys()
        if not missing:
            return True
        return tuple([False, missing])

    def set_body_complete(self) -> bool:
        """
        check if complete and set internal state

        Returns
        -------
        bool
            True if complete, False if incomplete

        """
        if self.check_body_complete() is True:  # neccessary as 'if tuple' is interpreted as True
            self.__body_complete = True
            return True
        return False

    def check_new_version(self) -> bool:
        """
        some logic to identify newer version of Article body\n
        starting easy with hashes

        Returns
        -------
        bool
            True if new version detected

        """

        check = {"headline", "body"} & Article.MANDATORY_BODY
        shared_keys = check & self.__body.keys() & self.__old_body.keys()
        if len(shared_keys) == 0:
            return True
        for key in shared_keys:
            if hash(self.__body[key]) != hash(self.__old_body[key]):
                return True
        return False

    def get_article(self) -> dict:
        """
        fetch all Article data\n
        consists of header, body, udfs components

        Returns
        -------
        dict
            dict: {"header":dict with headerdata, "body":dict with bodydata, "udfs":set of udfs (key value)}

        """
        all_article_components = {"header": self.__header, "body": self.__body, "udfs": self.__udfs}
        return all_article_components

    def is_in_db(self) -> bool:
        return self.__in_db

    def get_body_to_write(self) -> dict:
        """
        get flags if new version\n
        get new Body if different from old version\n
        get old version if new is the same (no need to write)

        Returns
        -------
        dict
            {"insert":Boolean (new Article body to write),"body": corresponding body data}

        """
        if self.check_new_version():
            return {"insert": True, "body": self.__body}
        return {"insert": False, "body": self.__old_body}

    # class Variable: Lookup table for setter functions
    # defined here because of dependency (setter functions)
    __set_header_functions = {"id": set_header_id, "url": set_url, "obsolete": set_obsolete, "source_id": set_source,
                              "source_date": set_header_date}
    __set_body_functions = {"id": set_body_id, "article_id": set_body_article_id, "headline": set_body_headline,
                            "body": set_body_text, "proc_timestamp": set_body_timestamp,
                            "proc_counter": set_body_counter}

    def set_header(self, data: dict) -> bool:
        """
        more comfortable bulk setter for header information with dictionary\n
        keys: "id","url","obslete","source_id","source_date"\n
        keys corresponding to database table article_header

        Parameters
        ----------
        data : dict
            dict of fields to set.

        Returns
        -------
        bool
            returns True if ALL successful.
        
        """
        return self.__set_by_dict(data, Article.__set_header_functions)

    def set_body(self, data: dict) -> bool:
        """
        more comfortable bulk setter for header information with dictionary\n
        keys: "id","article_id","headline","body","proc_timestamp","proc_counter"\n
        keys corresponding to database table article_body

        Parameters
        ----------
        data : dict
            dict of fields to set.

        Returns
        -------
        bool
            returns True if ALL successful.
        """
        return self.__set_by_dict(data, Article.__set_body_functions)

    def __set_by_dict(self, data: dict, target: dict) -> bool:
        """
        goal: setting all Article sub-object fields (body or header) at once \n
        lookup of setter function in target dict and calling setter function with input parameters from data dict

        Parameters
        ----------
        data : dict
            dict of fields to set.
        target : dict
            dict to look up corresponding setter functions

        Returns
        -------
        bool
            returns True if ALL successful.

        """
        return_default = True
        if type(data) == dict:
            if len(data.keys() & target.keys()) == 0:
                return False
            for key in data.keys() & target.keys():
                if not target[key](self, data[key]):
                    return_default = False
            return return_default
        return False

    def print(self):
        """
        printing Article (python object id) and components  \n
        for testing and debugging purposes

        Returns
        -------
        None.

        """

        print("\nprinting Article", self)
        print("\nheader: ", self.__header)
        print("\nbody: ", self.__body)
        print("\nudfs\n: ", self.__udfs)


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting Article showcase here:\n\n")
    testArticle = Article()
    header = {"id": 5, "obsolete": True, "testBullshit": "asdf", "source_date": dt.date.today()}
    body = {"id": 27, "testBullshit": "asdf", "article_id": 3, "headline": "example of headline", "body": "testText"}
    print("setting Article header as: ", header)
    testArticle.set_header(header)
    print("setting Article body as: ", body)
    testArticle.set_body(body)
    print("setting some udfs...")
    for i in range(0, 10):
        testArticle.add_udf("label", str(i ** 2))
        testArticle.add_udf("author", "me")
    print("testing empty history: is new Version= ", testArticle.check_new_version())
    testArticle.set_body_old()
    testArticle.set_body(
        {"id": 27, "testBullshit": "asdf", "article_id": 3, "headline": "esxample of headline", "body": "testText"})
    print("testing new headline ('esxample of headline'): is new Version= ", testArticle.check_new_version())
    print("printing Article:")
    testArticle.print()
    print("creating second Article object - class variables already in place")
    testArticle2 = Article()  # no first launch, here
    print("test testArticle header for completeness: ", testArticle.check_header_complete())
    print("test testArticle body for completeness: ", testArticle.check_body_complete())
