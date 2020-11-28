# -*- coding: utf-8 -*-
import datetime as dt
from connectDb import database as ownDBObject
import validators


class article:
    __sourceList=None
    __udfList=None
    OBJECT_TYPE=1 #article

    def __init__(self):
        self.__complete=False
        if(article.__udfList==None or article.__sourceList==None):
            print("first launch, setting class variables")
            #db=ownDBObject()
            #db.connect()
            #todo fetch lists
            article.__sourceList=[]
            article.__udfList=[]
            
            #db.close()
            pass
        self.__header={"obsolete":False}
        self.__body={"counter":0}
        self.__oldBody={}
        self.__udfs=[]

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
        if type(url)==str and validators.url(url)and len(url)<2048:
            self.__header["url"]=url
            return True
        return False
    def setObsolete(self, obsolete:bool):
        if type(obsolete)==bool:
            self.__header["obsolete"]=obsolete
            return True
        return False
    def setSource(self, source:int):
        if type(source)==int and source>0 and source in self.__sourceList:
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
    
    #udf setter functions
    def addUdf(self,key:str,value:str):
        pass


    def checkComplete(self):
        #todo
        return False
    def setComplete(self):
        if self.checkComplete:
            self.__complete=True
            return True
        return False
        

    #class Variable: Lookup table for setter functions
    #defined here because of dependency (setter functions)
    __setHeaderFunct={"headerId":setHeaderId,"url":setUrl,"obsolete":setObsolete,"source":setSource,"datePublished":setHeaderDate}
    __setBodyFunct={"bodyId":setBodyId,"articleId":setBodyArticleId,"body":setBodyText,"procTimestamp":setBodyTimeStamp,"procCounter":setBodyCounter}


    def setHeader(self, data:dict):
        """
        more comfortable bulk setter for header information with dictionary

        Parameters
        ----------
        data : dict
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.__setByDict__(data,self.__setHeaderFunct)
    def setBody(self, data:dict):
        """
        more comfortable bulk setter for header information with dictionary

        Parameters
        ----------
        data : dict
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

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

    def setUdfs(self, data:dict):
        #todo bulk setter useful at all?
        pass

    
    
    
    def print(self):
        #for testing and debugging purposes
        print("printing article",self)
        print("header: ",self.__header)
        print("body: ",self.__body)
        print("udfs: ",self.__udfs)
            

if __name__ == '__main__':
    testArticle=article()
    testArticle.setHeader({"headerId":5,"obsolete":True,"testBullshit":"asdf","datePublished":dt.datetime.today()})
    testArticle.setBody({"bodyId":27,"testBullshit":"asdf","articleId":3,"body":"testText"})
    testArticle.print()
    testArticle2=article() #no first launch, here
