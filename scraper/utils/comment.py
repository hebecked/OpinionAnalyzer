# -*- coding: utf-8 -*-

#todo: open tasks marked with todo

import datetime as dt
from utils.connectDb import database as ownDBObject    #to be recreated with article specific functionality


class Comment:
    
    #static data related database queries
    __UDFS_STATEMENT="""SELECT udf_name,id FROM news_meta_data.udf_header;"""
    
   
    __udfDict=None
    #mandatory database fields to be checked before writing
    MANDATORY_DATA={"article_body_id","external_id","level","body","proc_timestamp"}
    KEY_DATA={"article_body_id""external_id"}   #unique identifier in database
    OBJECT_TYPE=2 #comment - more robust: fetch from database
    MAX_UDF_LENGTH=80


    def __init__(self):
        
        """
        Comment object for use with all scrapers \n
        manages Comment components for several database tables \n
        
        sub objects are "data" and "udfs". \n
        they organize the data for the corresponding database tables. \n
        objects to be retrieved by .getComment()["data"] e.g. \n        
 
        """
        
        self.__complete=False
        if Comment.__udfDict==None:
            Comment.__udfList={}
            print("first launch, setting class variables") #todo delete line (debugging purposes only)
            #database connection to be rewritten later
            db=ownDBObject()
            db.connect()
            udf_header = db.retrieveValues(Comment.__UDFS_STATEMENT)
            Comment.__udfDict=dict(zip((udf[0] for udf in udf_header), (udf[1] for udf in udf_header)))
            print("udf Dict: ", Comment.__udfDict) #todo delete line (debugging purposes only)
            db.close()
        self.__data={}
        self.__udfs=set([])
        self.__data["parent_id"]=None

    def __del__(self):
        self.__complete=False
        
    #setter functions
    def setCommentId(self, commentId:int):
        """
        

        Parameters
        ----------
        commentId : int
            Corresponding to database field id in Comment table\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(commentId)==int and commentId>0:
            self.__data["id"]=commentId
            return True
        return False
    def setBodyId(self, bodyId:int):
        """
        

        Parameters
        ----------
        bodyId : int
            Corresponding to database field article_body_id in Comment table\n
            Id is given by database. Don't add random self generated data here.'

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(bodyId)==int and bodyId>0:
            self.__data["article_body_id"]=bodyId
            return True
        return False
    def setLevel(self,level:int):
        """
        

        Parameters
        ----------
        level : int
            Corresponding to database field level in Comment table\n
            level of Comment: \n
            0 for Comment directly related to Article \n
            n depth of Comment of Comment

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(level)==int and level>=0:
            self.__data["level"]=level
            return True
        return False        
    def setCommentText(self, commentText:str):
        """
        

        Parameters
        ----------
        commentText : str
            Corresponding to database field body in Comment table\n
            full Comment text to be inserted here

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(commentText)==str:
            self.__data["body"]=commentText.replace('\x00','')
            return True
        return False
    def setTimeStamp(self, commentTimestamp:dt.datetime=dt.datetime.today()):
        """
        

        Parameters
        ----------
        commentTimestamp : dtatetime.datetime, optional
            Corresponding to database field proc_tiomestamp in Comment table\n
            When did the crawler add this Comment text \n
            The default is datetime.datetime.today()

        Returns
        -------
        bool
            returns True if successful.

        """
        if type(commentTimestamp)==dt.datetime:
            self.__data["proc_timestamp"]=commentTimestamp.replace(microsecond=0).isoformat()
            return True
        return False   
    def setExternalId(self,externalId:int):
        """
        

        Parameters
        ----------
        externalId : int
            Corresponding to database field external_id in Comment table\n
            unique identifier for Comment
            best practice: (8 Byte hash value of body, author and url)

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(externalId)==int:
            self.__data["external_id"]=externalId
            return True
        return False
    def setParentId(self,parentId:int):
        """
        

        Parameters
        ----------
        parentId : int
            Corresponding to database field parent_id in Comment table\n
            set external_id of parent Comment (if level >0)

        Returns
        -------
        bool
            returns True if successful.

        """
        if  type(parentId)==int:
            self.__data["parent_id"]=parentId
            return True
        return False
    
    #udf setter functions
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
        if type(key)==str and key in Comment.__udfDict.keys() and type(value)==str and len(value)<=Comment.MAX_UDF_LENGTH:
            self.__udfs|={(Comment.__udfDict[key], value)}
            return True
        return False


    def checkCommentComplete(self):
        """
        validation of completeness of Comment data \n
        comparision with set MANDATORY_DATA

        Returns
        -------
        specific
            True if complete
            (false, set of missing fields) if incomplete

        """
        #checking for data in all mandatory database fields
        #return Value: True=ok, otherwise (False, missing data)
        missing= Comment.MANDATORY_DATA - self.__data.keys()
        if not(missing):
            return True
        return (False,missing)
    def setComplete(self):
        """
        check if complete and set internal state

        Returns
        -------
        bool
            True if complete, False if incomplete
        """
        if self.checkCommentComplete()==True:
            self.__complete=True
            return True
        # return False

    def getComment(self):
        """
        fetch all Comment components\n
        consists of data and udfs components

        Returns
        -------
        dict
            dict: {"data":dict with Comment data, "udfs":set of udfs (key value)}

        """
        all={"data":self.__data,"udfs":self.__udfs}
        return all

  
    #class Variable: Lookup table for setter functions
    #defined here because of dependency (setter functions)
    __setDataFunct={"article_body_id":setBodyId,"parent_id":setParentId,"level":setLevel,"body":setCommentText,"proc_timestamp":setTimeStamp,"external_id":setExternalId}

    def setData(self, data:dict):
        """
        more comfortable bulk setter for mandatory data with dictionary
        keys: "article_body_id","parent_id","level","body","proc_timestamp","external_id"\n
        keys corresponding to database table Comment
        """
        return self.__setByDict__(data,self.__setDataFunct)
 
    def __setByDict__(self,data:dict,target:dict):
        """
        goal: setting all Comment data fields at once \n
        lookup of setter function in target dict and calling setter function with input parameters from data dict
        same as in article.py though no multi-object switch needed

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
        #for testing and debugging purposes
        print("\nprinting Comment",self)
        print("\ndata: ",self.__data)
        print("\nudfs: ",self.__udfs)
            

if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting Comment showcase here:\n\n")
    testComment=Comment()
    commentData={"article_body_id":5,"level":3,"body":"asdf","proc_timestamp":dt.datetime.today()}
    print("setting Comment with data: ",commentData)
    testComment.setData(commentData)
    print("adding udf= ","author","some author")
    testComment.addUdf("author:","some author")
    print("adding udf= ","label:","nonsense")
    testComment.addUdf("label","nonsense")
    print("setting external ID")
    testComment.setExternalId(hash(testComment.getComment()["data"]["body"]+testComment.getComment()["data"]["proc_timestamp"]))
    print("printing resulting Comment:")
    testComment.print()