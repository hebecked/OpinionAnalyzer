# -*- coding: utf-8 -*-
import datetime as dt
from connectDb import database as ownDBObject    #to be recreated with article specific functionality
import validators


class article:
    __sourceList=None
    __udfList=None
    #mandatory database fields to be checked before writing
    MANDATORY_HEADER={"url","obsolete","source"}
    MANDATORY_BODY={"articleId","headline","body","procTimestamp","procCounter"}
    
    #article class constants
    OBJECT_TYPE=1 #article    
    MAX_URL_LENGTH=2048
    MAX_HEADLINE_LENGTH=200
    MAX_UDF_LENGTH=80


    def __init__(self):
        self.__complete=False
        if(article.__udfList==None or article.__sourceList==None):
            article.__sourceList=[]
            article.__udfList=[]
            print("first launch, setting class variables")
            #database connection to be rewritten later
            db=ownDBObject()
            db.connect()
            udf_header = db.retrieveValues("SELECT udf_name,id FROM news_meta_data.udf_header;")
            for udf_name in udf_header:
                article.__udfList+=[udf_name[0]]
            print(article.__udfList)
            sources = db.retrieveValues("SELECT id,source FROM news_meta_data.source_header;")
            for sourceId in sources:
                article.__sourceList+=[sourceId[0]]
            db.close()
        self.__header={"obsolete":False}
        self.__body={"procCounter":0}
        self.__oldBody={}
        self.__udfs=set([])

    def __del__(self):
        self.__complete=False
        
    #header setter functions    
    def setHeaderId(self, headerId:int):
        if  type(headerId)==int and headerId>0:
            self.__header["headerId"]=headerId
            self.__body["articleId"]=headerId
            return True
        return False
    def setUrl(self, url:str):
        if type(url)==str and validators.url(url)and len(url)<article.MAX_URL_LENGTH:
            self.__header["url"]=url
            return True
        return False
    def setObsolete(self, obsolete:bool):
        if type(obsolete)==bool:
            self.__header["obsolete"]=obsolete
            return True
        return False
    def setSource(self, source:int):
        if type(source)==int and source>0 and source in article.__sourceList:
            self.__header["source"]=source
            return True
        return False
    def setHeaderDate(self, datePublished:dt.datetime):
        if type(datePublished)==dt.datetime:
            self.__header["datePublished"]=datePublished
            return True
        return False
    
    #Body setter functions
    def setBodyId(self,bodyId:int):
        if  type(bodyId)==int and bodyId>0:
            self.__body["bodyId"]=bodyId
            return True
        return False
    def setBodyArticleId(self,bodyArticleId:int):
        if  type(bodyArticleId)==int and bodyArticleId>0:
            self.__body["articleId"]=bodyArticleId
            return True
        return False
    def setBodyText(self, bodyText:str):
        if type(bodyText)==str:
            self.__body["body"]=bodyText
            return True
        return False
    def setBodyHeadline(self, bodyHeadline:str):
        if type(bodyHeadline)==str and len(bodyHeadline)<=article.MAX_HEADLINE_LENGTH:
            self.__body["headline"]=bodyHeadline
            return True
        return False
    def setBodyTimeStamp(self, bodyTimestamp:dt.datetime=dt.datetime.today()):
        if type(bodyTimestamp)==dt.datetime:
            self.__body["procTimestamp"]=bodyTimestamp
            return True
        return False
    def setBodyCounter(self, bodyCounter:int):
        if  type(bodyCounter)==int and bodyCounter>0:
            self.__body["procCounter"]=bodyCounter
            return True
        return False
    def setBodyOld(self):
        #shifting body data to old body data for comparison with newer version
        #tobe used after import from database
        self.__oldBody=self.__body
        self.__body={"procCounter":0}
        return True
    #udf setter functions
    def addUdf(self,key:str,value:str):
        if type(key)==str and key in article.__udfList and type(value)==str and len(value)<=article.MAX_UDF_LENGTH:
            self.__udfs|={(key,value)}
            return True
        return False


    def checkComplete(self):
        #checking for data in all mandatory database fields
        #return Value: True=ok, ohterwise (False, missing data)
        missing={"header":{},"body":{}}
        missing["header"]=article.MANDATORY_HEADER-self.__header.keys()
        missing["body"]=article.MANDATORY_BODY-self.__body.keys()
        if missing["header"]=={} and missing["body"]=={}:
            return True
        return (False,missing)
    def setComplete(self):
        if self.checkComplete():
            self.__complete=True
            return True
        return False


    def checkNewVersion(self):
        #some logic to identify newer version of article body
        #starting easy with hashes
        check={"headline","body"}&article.MANDATORY_BODY
        sharedKeys=check&self.__body.keys()&self.__oldBody.keys()
        if len(sharedKeys)==0:
            return True
        for key in sharedKeys:
            if (hash(self.__body[key])!=hash(self.__oldBody[key])):
                return True
        return False
    
    def getData(self):
        all={"header":self.__header,"body":self.__body,"udfs":self.__udfs}
        return all

    #class Variable: Lookup table for setter functions
    #defined here because of dependency (setter functions)
    __setHeaderFunct={"headerId":setHeaderId,"url":setUrl,"obsolete":setObsolete,"source":setSource,"datePublished":setHeaderDate}
    __setBodyFunct={"bodyId":setBodyId,"articleId":setBodyArticleId,"headline":setBodyHeadline,"body":setBodyText,"procTimestamp":setBodyTimeStamp,"procCounter":setBodyCounter}


    def setHeader(self, data:dict):
        """
        more comfortable bulk setter for header information with dictionary
        """
        return self.__setByDict__(data,self.__setHeaderFunct)
    def setBody(self, data:dict):
        """
        more comfortable bulk setter for header information with dictionary
        """
        return self.__setByDict__(data,self.__setBodyFunct)    
    def __setByDict__(self,data:dict,target:dict):
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
        #for testing and debugging purposes
        print("printing article",self)
        print("header: ",self.__header)
        print("body: ",self.__body)
        print("udfs: ",self.__udfs)
            

if __name__ == '__main__':
    testArticle=article()
    testArticle.setHeader({"headerId":5,"obsolete":True,"testBullshit":"asdf","datePublished":dt.datetime.today()})
    testArticle.setBody({"bodyId":27,"testBullshit":"asdf","articleId":3,"headline":"example of headline","body":"testText"})
    for i in range(0,10):
        testArticle.addUdf("label",str(i**2))
        testArticle.addUdf("author","me")
    print("testing empty history - new Version: ",testArticle.checkNewVersion())
    testArticle.setBodyOld()
    testArticle.setBody({"bodyId":27,"testBullshit":"asdf","articleId":3,"headline":"esxample of headline","body":"testText"})
    print("testing new headline - new Version: ",testArticle.checkNewVersion())
    testArticle.print()
    print("creating new article object - class variables already in place")
    testArticle2=article() #no first launch, here
    print("test testArticle for completeness: ",testArticle.checkComplete())
