# -*- coding: utf-8 -*-
import datetime as dt
from utils.connectDb import database as ownDBObject    #to be recreated with article specific functionality


class comment:
    
    #static data related database queries
    __UDFS_STATEMENT="""SELECT udf_name,id FROM news_meta_data.udf_header;"""
    
   
    __udfDict=None
    #mandatory database fields to be checked before writing
    MANDATORY_DATA={"article_body_id","external_id","level","body","proc_timestamp"}
    KEY_DATA={"article_body_id""external_id"}   #unique identifier in database
    OBJECT_TYPE=2 #comment - more robust: fetch from database
    MAX_UDF_LENGTH=80


    def __init__(self):
        self.__complete=False
        if comment.__udfDict==None:
            comment.__udfList={}
            print("first launch, setting class variables") #todo delete line (debugging purposes only)
            #database connection to be rewritten later
            db=ownDBObject()
            db.connect()
            udf_header = db.retrieveValues(comment.__UDFS_STATEMENT)
            comment.__udfDict=dict(zip((udf[0] for udf in udf_header),(udf[1]for udf in udf_header)))
            print("udf Dict: ",comment.__udfDict) #todo delete line (debugging purposes only)
            db.close()
        self.__data={}
        self.__udfs=set([])
        self.__data["parent_id"]=None

    def __del__(self):
        self.__complete=False
        
    #setter functions
    def setCommentId(self, commentId:int):
        if  type(commentId)==int and commentId>0:
            self.__data["id"]=commentId
            return True
        return False
    def setBodyId(self, bodyId:int):
        if  type(bodyId)==int and bodyId>0:
            self.__data["article_body_id"]=bodyId
            return True
        return False
    def setLevel(self,level:int):
        if  type(level)==int and level>=0:
            self.__data["level"]=level
            return True
        return False        
    def setCommentText(self, commentText:str):
        if type(commentText)==str:
            self.__data["body"]=commentText.replace('\x00','')
            return True
        return False
    def setTimeStamp(self, commentTimestamp:dt.datetime=dt.datetime.today()):
        if type(commentTimestamp)==dt.datetime:
            self.__data["proc_timestamp"]=commentTimestamp.replace(microsecond=0).isoformat()
            return True
        return False   
    def setExternalId(self,externalId:int):
        if  type(externalId)==int:
            self.__data["external_id"]=externalId
            return True
        return False
    def setParentId(self,parentId:int):
        if  type(parentId)==int:
            self.__data["parent_id"]=parentId
            return True
        return False
    
    #udf setter functions
    def addUdf(self,key:str,value:str):
        if type(key)==str and key in comment.__udfDict.keys() and type(value)==str and len(value)<=comment.MAX_UDF_LENGTH:
            self.__udfs|={(comment.__udfDict[key],value)}
            return True
        return False


    def checkCommentComplete(self):
        #checking for data in all mandatory database fields
        #return Value: True=ok, otherwise (False, missing data)
        missing=comment.MANDATORY_DATA-self.__data.keys()
        if not(missing):
            return True
        return (False,missing)
    def setComplete(self):
        if self.checkCommentComplete()==True:
            self.__complete=True
            return True
        return False

    def getComment(self):
        all={"data":self.__data,"udfs":self.__udfs}
        return all
    def getKey(self):
        if not(comment.KEY_DATA-self.__data.keys()):
            return (self.__data["article_body_id"],self.__data["external_id"])
        return False
  
    #class Variable: Lookup table for setter functions
    #defined here because of dependency (setter functions)
    __setDataFunct={"article_body_id":setBodyId,"parent_id":setParentId,"level":setLevel,"body":setCommentText,"proc_timestamp":setTimeStamp,"external_id":setExternalId}

    def setData(self, data:dict):
        """
        more comfortable bulk setter for mandatory data with dictionary
        """
        return self.__setByDict__(data,self.__setDataFunct)
 
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
        print("\nprinting comment",self)
        print("\ndata: ",self.__data)
        print("\nudfs: ",self.__udfs)
            

if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting comment testcases here:\n\n")
    testComment=comment()
    commentData={"article_body_id":5,"level":3,"body":"asdf","proc_timestamp":dt.datetime.today()}
    print("setting comment with data: ",commentData)
    testComment.setData(commentData)
    print("adding udf= ","author","some author")
    testComment.addUdf("author:","some author")
    print("adding udf= ","label:","nonsense")
    testComment.addUdf("label","nonsense")
    print("setting external ID")
    testComment.setExternalId(hash(testComment.getComment()["data"]["body"]+testComment.getComment()["data"]["proc_timestamp"]))
    print("printing resulting comment:")
    testComment.print()