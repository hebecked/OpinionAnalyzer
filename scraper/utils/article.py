# -*- coding: utf-8 -*-

#todo: open tasks marked with todo

import datetime as dt
from utils.connectDb import database as ownDBObject
import validators      # used for url validation
import copy            #deepcopy used for oldBody


class Article:
    
    #static data related database queries
    __UDFS_STATEMENT="""SELECT udf_name,id FROM news_meta_data.udf_header;"""
    __SOURCES_STATEMENT="""SELECT id,source FROM news_meta_data.source_header;"""
    
    
    __sourceList=None
    __udfDict=None
    #mandatory database fields to be checked before writing
    MANDATORY_HEADER={"url","obsolete","source_id"}
    MANDATORY_BODY={"article_id","headline","body","proc_timestamp","proc_counter"}
    
    #Article class constants (given by database entries / restrictions)

    OBJECT_TYPE=1 #article - more robust: fetch from database    
    MAX_URL_LENGTH=2048
    MAX_HEADLINE_LENGTH=200
    MAX_UDF_LENGTH=80


    def __init__(self):
        """
        article object for use with all scrapers \n
        manages article components for several database tables \n
        
        sub objects are "header", "body", "udfs". \n
        they organize the data for the corresponding database tables. \n
        objects to be retrieved by .getArticle()["header"] e.g. \n        
        
        
        free to use data storage .freeData with no predefined type or usage \n
 
        """
        self.__headerComplete=False
        self.__bodyComplete=False
        if(Article.__udfDict==None or Article.__sourceList==None):
            Article.__sourceList=[]
            Article.__udfList={}
            print("first launch, setting class variables") #todo delete line (debugging purposes only)
            #database connection to be rewritten later
            db=ownDBObject()
            db.connect()
            udf_header = db.retrieveValues(Article.__UDFS_STATEMENT)
            Article.__udfDict=dict(zip((udf[0] for udf in udf_header), (udf[1] for udf in udf_header)))
            print("udf Dict: ", Article.__udfDict) #todo delete line (debugging purposes only)
            sources = db.retrieveValues(Article.__SOURCES_STATEMENT)
            Article.__sourceList=list(source[0] for source in sources)
            print("sourceList ", Article.__sourceList) #todo delete line (debugging purposes only)
            db.close()
        self.__header={"obsolete":False,"source_date":None}
        self.__body={"proc_counter":0}
        self.__oldBody={}
        self.__udfs=set([])
        self.__inDb=False
        self.freeData=None

    def __del__(self):
        self.__headerComplete=False
        self.__bodyComplete=False
        
    #header setter functions    
    def setHeaderId(self, headerId:int):
        """
        

        Parameters
        ----------
        headerId : int
            Corresponding to database field id in article_header table\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(headerId)==int and headerId>0:
            self.__header["id"]=headerId
            self.__body["article_id"]=headerId
            self.__inDb=True            
            return True
        return False
    def setUrl(self, url:str):
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

        if type(url)==str and validators.url(url)and len(url)<Article.MAX_URL_LENGTH:

            self.__header["url"]=url
            return True
        return False
        
    def setObsolete(self, obsolete:bool):
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
        if type(obsolete)==bool:
            self.__header["obsolete"]=obsolete
            return True
        return False
    def setSource(self, source:int):
        """
        

        Parameters
        ----------
        source : int
            Corresponding to database field obsolete in article_header table.\n
            source_id will be validated as existant in database

        Returns
        -------
        bool
            returns True if successful.

        """

        if type(source)==int and source>0 and source in Article.__sourceList:

            self.__header["source_id"]=source
            return True
        return False
        
    def setHeaderDate(self, datePublished:dt.date):
        """
        

        Parameters
        ----------
        datePublished : datetime.date
            Corresponding to database field source_date in article_header table.\n
            will be validated as datetime.date and converted to string automatically

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(datePublished)==dt.date:
            self.__header["source_date"]=datePublished.isoformat()
            return True
        return False
    
    #Body setter functions
    def setBodyId(self,bodyId:int):
        """
        

        Parameters
        ----------
        bodyId : int
            Corresponding to database field id in article_body table\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(bodyId)==int and bodyId>0:
            self.__body["id"]=bodyId
            return True
        return False
    
    def setBodyArticleId(self,bodyArticleId:int):
        """
        

        Parameters
        ----------
        bodyArticleId : int
            Corresponding to database field id in article_header table and database field article_id in table article_body\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(bodyArticleId)==int and bodyArticleId>0:
            self.__body["article_id"]=bodyArticleId
            return True
        return False
    
    def setBodyText(self, bodyText:str):
        """
        

        Parameters
        ----------
        bodyText : str
            Corresponding to database field body in article_body table\n
            full article text to be inserted here

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(bodyText)==str:
            self.__body["body"]=bodyText
            return True
        return False
    
    def setBodyHeadline(self, bodyHeadline:str):
        """
        

        Parameters
        ----------
        bodyHeadline : str
            Corresponding to database field headline in article_body table\n
            headline length is cappen at MAX_HEADLINE_LENGTH (corresponding to database layout)

        Returns
        -------
        bool
            returns True if successful.

        """

        if type(bodyHeadline)==str and len(bodyHeadline)<=Article.MAX_HEADLINE_LENGTH:
            self.__body["headline"]=bodyHeadline
            return True
        return False
    
    def setBodyTimeStamp(self, bodyTimestamp:dt.datetime=dt.datetime.today()):
        """
        

        Parameters
        ----------
        bodyTimestamp : datetime.datetime, optional
            Corresponding to database field proc_timestamp in article_body table\n
            When did the crawler add this article text (version)\n
            The default is datetime.datetime.today()

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(bodyTimestamp)==dt.datetime:
            self.__body["proc_timestamp"]=bodyTimestamp.replace(microsecond=0).isoformat()
            return True
        return False
    
    def setBodyCounter(self, bodyCounter:int):
        """
        

        Parameters
        ----------
        bodyCounter : int
            Corresponding to database field proc_counter in article_body table\n
            set =0 with Article creation and therefore only strictly positive values are allowed\n
            manages the time till revisit of already seen articles\n
            next visit = proc_timestamp + 1 hour * (pow(2,bodyCounter)-1), so set carefully\n
            value of 0 for new articles

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(bodyCounter)==int and bodyCounter>0:
            self.__body["proc_counter"]=bodyCounter
            return True
        return False
    
    def setBodyOld(self):
        """

        function moves current Article body data to old Article body data (deepcopy) and creates new empty body element\n
        intended to be called after import (old) body data fromn database

        Returns
        -------
        bool
            returns True if successful.

        """

        if self.checkBodyComplete():
            self.__oldBody=copy.deepcopy(self.__body)
            self.__body={"proc_counter":0,"article_id":self.__oldBody["article_id"]}
            return True
        return False

    def addUdf(self,key:str,value:str):
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

        if type(key)==str and key in Article.__udfDict.keys() and type(value)==str and len(value)<=Article.MAX_UDF_LENGTH:
            self.__udfs|={(Article.__udfDict[key], value)}
            return True
        return False


    def checkHeaderComplete(self):
        """
        validation of completeness of header data\n
        comparision with set MANDATORY_HEADER

        Returns
        -------
        specific
            True if complete
            (false, set of missing fields) if incomplete

        """
        #checking for data in all mandatory database fields
        #return Value: True=ok, otherwise (False, missing data)
        missing= Article.MANDATORY_HEADER - self.__header.keys()
        if not(missing):
            return True
        return (False,missing)
    
    def setHeaderComplete(self):
        """
        check if complete and set internal state

        Returns
        -------
        bool
            True if complete, False if incomplete

        """
        if self.checkHeaderComplete()==True:
            self.__headerComplete=True
            return True
        return False
    
    def checkBodyComplete(self):
        """
        validation of completeness of body data \n
        comparision with set MANDATORY_BODY

        Returns
        -------
        specific
            True if complete
            (false, set of missing fields) if incomplete

        """

        missing= Article.MANDATORY_BODY - self.__body.keys()

        if not(missing):
            return True
        return (False,missing)
    
    def setBodyComplete(self):
        """
        check if complete and set internal state

        Returns
        -------
        bool
            True if complete, False if incomplete

        """
        if self.checkBodyComplete()==True:
            self.__bodyComplete=True
            return True
        return False

    def checkNewVersion(self):
        """

        some logic to identify newer version of Article body\n
        starting easy with hashes

        Returns
        -------
        bool
            True if new version detected

        """

        check= {"headline","body"} & Article.MANDATORY_BODY
        sharedKeys=check&self.__body.keys()&self.__oldBody.keys()
        if len(sharedKeys)==0:
            return True
        for key in sharedKeys:
            if (hash(self.__body[key])!=hash(self.__oldBody[key])):
                return True
        return False
    
    def getArticle(self):
        """

        fetch all article data\n
        consists of header, body, udfs components

        Returns
        -------
        dict
            dict: {"header":dict with headerdata, "body":dict with bodydata, "udfs":set of udfs (key value)}

        """
        all={"header":self.__header,"body":self.__body,"udfs":self.__udfs}
        return all
    
    def isInDb(self):
        return self.__inDb
    
    def getBodyToWrite(self):
        """
        get flags if new version\n
        get new Body if different from old version\n
        get old version if new is the same (no need to write)

        Returns
        -------
        dict
            {"insert":Boolean (new article body to write),"body": corresponding body data}

        """
        if self.checkNewVersion():
            return {"insert":True, "body":self.__body}
        return {"insert":False, "body":self.__oldBody}
        

    #class Variable: Lookup table for setter functions
    #defined here because of dependency (setter functions)
    __setHeaderFunct={"id":setHeaderId,"url":setUrl,"obsolete":setObsolete,"source_id":setSource,"source_date":setHeaderDate}
    __setBodyFunct={"id":setBodyId,"article_id":setBodyArticleId,"headline":setBodyHeadline,"body":setBodyText,"proc_timestamp":setBodyTimeStamp,"proc_counter":setBodyCounter}


    def setHeader(self, data:dict):
        """
        more comfortable bulk setter for header information with dictionary\n
        keys: "id","url","obslete","source_id","source_date"\n
        keys corresponding to database table article_header
        
        
        """

        return self.__setByDict__(data, Article.__setHeaderFunct)
    
    def setBody(self, data:dict):
        """
        more comfortable bulk setter for header information with dictionary\n
        keys: "id","article_id","headline","body","proc_timestamp","proc_counter"\n
        keys corresponding to database table article_body
        """

        return self.__setByDict__(data, Article.__setBodyFunct)
    
    def __setByDict__(self,data:dict,target:dict):
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
        returnDefault=True
        if type(data)==dict:
            if len(data.keys()&target.keys())==0:
                return False
            for key in data.keys()&target.keys():
                if(target[key](self,data[key])==False):
                    returnDefault=False
            return returnDefault
        return False
    
    def print(self):
        """

        printing Article (python object id) and components  \n
        for testing and debugging purposes

        Returns
        -------
        None.

        """


        print("\nprinting Article",self)
        print("\nheader: ",self.__header)
        print("\nbody: ",self.__body)
        print("\nudfs\n: ",self.__udfs)
            

if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")

    print("Starting Article showcase here:\n\n")
    testArticle=Article()
    header={"id":5,"obsolete":True,"testBullshit":"asdf","source_date":dt.date.today()}
    body={"id":27,"testBullshit":"asdf","article_id":3,"headline":"example of headline","body":"testText"}
    print("setting Article header as: ", header)
    testArticle.setHeader(header)
    print("setting Article body as: ", body)
    testArticle.setBody(body)
    print("setting some udfs...")
    for i in range(0,10):
        testArticle.addUdf("label",str(i**2))
        testArticle.addUdf("author","me")
    print("testing empty history: is new Version= ",testArticle.checkNewVersion())
    testArticle.setBodyOld()
    testArticle.setBody({"id":27,"testBullshit":"asdf","article_id":3,"headline":"esxample of headline","body":"testText"})
    print("testing new headline ('esxample of headline'): is new Version= ",testArticle.checkNewVersion())
    print("printing Article:")
    testArticle.print()
    print("creating second Article object - class variables already in place")
    testArticle2=Article() #no first launch, here
    print("test testArticle header for completeness: ",testArticle.checkHeaderComplete())
    print("test testArticle body for completeness: ",testArticle.checkBodyComplete())
