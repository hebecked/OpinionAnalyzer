# -*- coding: utf-8 -*-
import datetime as dt
from connectDb import database as ownDBObject    #to be recreated with article specific functionality
import validators
import copy



class article:
    
    #static data related database queries
    __UDFS_STATEMENT="""SELECT udf_name,id FROM news_meta_data.udf_header;"""
    __SOURCES_STATEMENT="""SELECT id,source FROM news_meta_data.source_header;"""
    
    
    __sourceList=None
    __udfDict=None
    #mandatory database fields to be checked before writing
    MANDATORY_HEADER={"url","obsolete","source_id"}
    MANDATORY_BODY={"article_id","headline","body","proc_timestamp","proc_counter"}
    
    #article class constants
    OBJECT_TYPE=1 #article - more robust: fetch from database    
    MAX_URL_LENGTH=2048
    MAX_HEADLINE_LENGTH=200
    MAX_UDF_LENGTH=80


    def __init__(self):
        self.__headerComplete=False
        self.__bodyComplete=False
        if(article.__udfDict==None or article.__sourceList==None):
            article.__sourceList=[]
            article.__udfList={}
            print("first launch, setting class variables") #todo delete line (debugging purposes only)
            #database connection to be rewritten later
            db=ownDBObject()
            db.connect()
            udf_header = db.retrieveValues(article.__UDFS_STATEMENT)
            article.__udfDict=dict(zip((udf[0] for udf in udf_header),(udf[1]for udf in udf_header)))
            print("udf Dict: ",article.__udfDict) #todo delete line (debugging purposes only)
            sources = db.retrieveValues(article.__SOURCES_STATEMENT)
            article.__sourceList=list(source[0] for source in sources)
            print("sourceList ", article.__sourceList) #todo delete line (debugging purposes only)
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
        if  type(headerId)==int and headerId>0:
            self.__header["id"]=headerId
            self.__body["article_id"]=headerId
            self.__inDb=True            
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
            self.__header["source_id"]=source
            return True
        return False
    def setHeaderDate(self, datePublished:dt.date):
        if type(datePublished)==dt.date:
            self.__header["source_date"]=datePublished.isoformat()
            return True
        return False
    
    #Body setter functions
    def setBodyId(self,bodyId:int):
        if  type(bodyId)==int and bodyId>0:
            self.__body["id"]=bodyId
            return True
        return False
    def setBodyArticleId(self,bodyArticleId:int):
        if  type(bodyArticleId)==int and bodyArticleId>0:
            self.__body["article_id"]=bodyArticleId
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
            self.__body["proc_timestamp"]=bodyTimestamp.replace(microsecond=0).isoformat()
            return True
        return False
    def setBodyCounter(self, bodyCounter:int):
        if  type(bodyCounter)==int and bodyCounter>0:
            self.__body["proc_counter"]=bodyCounter
            return True
        return False
    def setBodyOld(self):
        #shifting body data to old body data for comparison with newer version
        #tobe used after import from database
        if self.checkBodyComplete():
            self.__oldBody=copy.deepcopy(self.__body)
            self.__body={"proc_counter":0,"article_id":self.__body["article_id"]}
            return True
        return False
    #udf setter functions
    def addUdf(self,key:str,value:str):
        if type(key)==str and key in article.__udfDict.keys() and type(value)==str and len(value)<=article.MAX_UDF_LENGTH:
            self.__udfs|={(article.__udfDict[key],value)}
            return True
        return False


    def checkHeaderComplete(self):
        #checking for data in all mandatory database fields
        #return Value: True=ok, otherwise (False, missing data)
        missing=article.MANDATORY_HEADER-self.__header.keys()
        if not(missing):
            return True
        return (False,missing)
    def setHeaderComplete(self):
        if self.checkHeaderComplete()==True:
            self.__headerComplete=True
            return True
        return False
    
    def checkBodyComplete(self):
        #checking for data in all mandatory database fields
        #return Value: True=ok, ohterwise (False, missing data)
        missing=article.MANDATORY_BODY-self.__body.keys()
        if not(missing):
            return True
        return (False,missing)
    def setBodyComplete(self):
        if self.checkBodyComplete()==True:
            self.__bodyComplete=True
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
    
    def getArticle(self):
        all={"header":self.__header,"body":self.__body,"udfs":self.__udfs}
        return all
    
    def isInDb(self):
        return self.__inDb
    
    def getBodyToWrite(self):
        if self.checkNewVersion():
            return {"insert":True, "body":self.__body}
        return {"insert":False, "body":self.__oldBody}
        

    #class Variable: Lookup table for setter functions
    #defined here because of dependency (setter functions)
    __setHeaderFunct={"id":setHeaderId,"url":setUrl,"obsolete":setObsolete,"source_id":setSource,"source_date":setHeaderDate}
    __setBodyFunct={"id":setBodyId,"article_id":setBodyArticleId,"headline":setBodyHeadline,"body":setBodyText,"proc_timestamp":setBodyTimeStamp,"proc_counter":setBodyCounter}


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
        print("\nprinting article",self)
        print("\nheader: ",self.__header)
        print("\nbody: ",self.__body)
        print("\nudfs\n: ",self.__udfs)
            

if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting article testcases here:\n\n")
    testArticle=article()
    header={"id":5,"obsolete":True,"testBullshit":"asdf","source_date":dt.date.today()}
    body={"id":27,"testBullshit":"asdf","article_id":3,"headline":"example of headline","body":"testText"}
    print("setting article header as: ", header)
    testArticle.setHeader(header)
    print("setting article body as: ", body)
    testArticle.setBody(body)
    print("setting some udfs...")
    for i in range(0,10):
        testArticle.addUdf("label",str(i**2))
        testArticle.addUdf("author","me")
    print("testing empty history: is new Version= ",testArticle.checkNewVersion())
    testArticle.setBodyOld()
    testArticle.setBody({"id":27,"testBullshit":"asdf","article_id":3,"headline":"esxample of headline","body":"testText"})
    print("testing new headline ('esxample of headline'): is new Version= ",testArticle.checkNewVersion())
    print("printing article:")
    testArticle.print()
    print("creating second article object - class variables already in place")
    testArticle2=article() #no first launch, here
    print("test testArticle header for completeness: ",testArticle.checkHeaderComplete())
    print("test testArticle body for completeness: ",testArticle.checkBodyComplete())
