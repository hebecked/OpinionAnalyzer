#!/usr/bin/python

#todo: open tasks marked with todo

from datetime import datetime, date, timedelta
import spiegel_scraper as spon
from utils.article import article
from utils.comment import comment
from utils.databaseExchange import databaseExchange
import dataCollectors.TemplateScraper
import time
import math
import hashlib

class SponScraper(dataCollectors.TemplateScraper.Scraper):
    SUBSET_LENGTH=10   #threshold for database flush
    DELAY_SUBSET=1  #sleep x every SUBSET_LENGTH html requests
    DELAY_INDIVIDUAL=0  #sleep x every html request
    def __init__(self):
        self.id=1 #set corresponding datasource id here
        self.hasErrors=False
        pass
   
    def getArticlesList(self, start:date=date(1900,1,1), end:date=date.today()):
        """
        function makes use of spiegel_scraper package to directly create own article object from crawling the archive
                
        Parameters
        ----------
        start : date, optional
            The default is date(1900,1,1).
        end : date, optional
            The default is date.today().

        Returns
        -------
        List of corresponding article objects (published between start and end date) from this source \n
        article will just contain header information so far
        """
        returnList=[]
        num_of_days=(start-end).days
        date_list=[(timedelta(i)+date.today()) for i in range(num_of_days,1)]
        full_list=[]
        for dt in date_list:
            print("fetching date:",dt)
            try:
                full_list+=(spon.archive.scrape_html(spon.archive.html_by_date(dt)))
            except:
                print("Article List crawl error!")
                self.hasErrors=True
            time.sleep(1) #remove comment for crawler delay
        url_list=list(filter(lambda x: x['is_paid']==False,full_list)) #remove paid aricles without access
        for url in url_list:
            art=article()
            art.setHeader({'source_date':url['date_published'].date(),'source_id':self.id,'url':str(url['url'])})
            returnList+=[art]
        return(returnList)	
	        
    def getArticleDetails(self, art:article):
        """
        adds detailed information (article text and several others) to article \n
        article body will be added

        Parameters
        ----------
        art : article
            the article to add detailed information to

        Returns
        -------
        bool
            returns True if successful.

        """
        try:
            html = spon.article.html_by_url(art.getArticle()['header']['url'])
            content = spon.article.scrape_html(html)
        except:
            print("Article crawl error!")
            self.hasErrors=True
            art.setObsolete(True)
            return False
        if('id' in content.keys()):            
            art.setBody({'headline':content['headline']['main'],'body':content['text'],'proc_timestamp':datetime.today(),'proc_counter':0})
            art.freeData=content['id']
        #add udfs
        if('topics' in content.keys()):
            for topic in content['topics']:
                art.addUdf('label',topic)
        if('author' in content.keys()):
            for author in content['author']['names']:
                art.addUdf('author',author)
        if('date_created' in content.keys()):
            art.addUdf('date_created',content['date_created'])
            try: art.setBodyCounter(max(int(math.log((date.today()-date.fromisoformat(content['date_created'][0:10])).days*24,2))-1,0))
            except: print('Body Counter not set')
        if 'date_modified' in content.keys(): art.addUdf('date_modified',content['date_modified'])
        if 'date_published' in content.keys(): art.addUdf('date_published',content['date_published'])
        return True
    
    def getWriteArticlesDetails(self, writer:databaseExchange, articlesList:list, startdate:date=date(1900,1,1)):
        """
        

        Parameters
        ----------
        writer : databaseExchange
            databaseExchange object, the crawler will use to connect to database
        articlesList : list
            a list of articles to fetch details for and write to database
        startdate : date, optional
            used to define which comments are too old to be fetched. Comments posted after startdate will be processed. \n
            he default is date(1900,1,1).

        Returns
        -------
        None.

        """
        if(type(articlesList)!=list): return False
        start=0
        while start < len(articlesList):
            for art in articlesList[start:(start+SponScraper.SUBSET_LENGTH)]:
                print("fetching article:",art.getArticle()['header']['url'])
                self.getArticleDetails(art)
                time.sleep(SponScraper.DELAY_INDIVIDUAL)
            writer.writeArticles(articlesList[start:(start+SponScraper.SUBSET_LENGTH)])
            for art in articlesList[start:(start+SponScraper.SUBSET_LENGTH)]:
                print("fetching comments for ",art.getArticle()['header']['url'])
                cmts=self.getCommentsForArticle(art,startdate)
                writer.writeComments(cmts)
                time.sleep(SponScraper.DELAY_INDIVIDUAL)
            start+=SponScraper.SUBSET_LENGTH
            time.sleep(SponScraper.DELAY_SUBSET)
    
    def getCommmentExternalId(self,url, cmt:spon.comments):
        """
        calculate comment external id as hash

        Parameters
        ----------
        url : TYPE
            article url where the comment has been found
        cmt : spon.comments
            spon.comment object for which we calculate the external_id

        Returns
        -------
        ext_id : int
            external_id as 8 byte integer

        """
        key=url+cmt['user']['username']+cmt['body']
        ext_id=int.from_bytes(hashlib.md5(key.encode()).digest()[0:8],"big",signed=True)
        return ext_id

    def flattenComments(self, art:article,comments:list,parent:int=None,depth=0,start:date=date(1900,1,1),end:date=date.today()):
        """
        recursively traverses the comment tree and returns list of own comment objects filled with predefined data

        Parameters
        ----------
        art : article
            the article the comments belong to
        comments : list
            list of comments (starting level)
        parent : int, optional
            for recursive call: if comment has parent, add parent_id here to save this connection to database \n
            The default is None.
        depth : TYPE, optional
            current depth of comment list. The default is starting value of 0 (comment for article).
        start : date, optional
            comments before this date are dropped. The default is date(1900,1,1).
        end : date, optional
            comments after this date are dropped. The default is date.today().

        Returns
        -------
        returnList:list
            list of all comment objects below the article, which fit between the given dates

        """
        returnList=[]
        if type(comments)!=list: 
            return []
        for cmt in comments:
            if type(cmt)!=dict: continue
            if (cmt['body']!=None and cmt['user']!=None and cmt['created_at']!=None):
                cmt_id=self.getCommmentExternalId(art.getArticle()["header"]["url"], cmt)
                tmp=comment()
                tmp.setData({"article_body_id":art.getBodyToWrite()["body"]["id"],"parent_id":parent,"level":depth,"body":cmt['body'],"proc_timestamp":datetime.today(),"external_id":cmt_id})
                if 'user' in cmt.keys():tmp.addUdf("author",cmt['user']['username'])
                tmp.addUdf("date_created",cmt['created_at'])
                if (start<=date.fromisoformat(cmt['created_at'][0:10])<=end):
                    returnList+=[tmp]
                if 'replies' in cmt.keys(): 
                    tmp.addUdf("replies",str(len(cmt['replies'])))
                    returnList+= self.flattenComments(art,cmt['replies'],cmt_id,depth+1,start,end)
                #tmp.print()
        return returnList

	
    def getCommentsForArticle(self,art:article,start:date=date(1900,1,1),end:date=date.today()): 
        """
        

        Parameters
        ----------
        art : article
            input article for which we want to gather comments
        start : date, optional
             comments before this date are dropped. The default is date(1900,1,1).
        end : date, optional
            comments after this date are dropped. The default is date.today().

        Returns
        -------
        returnList : list
            list of all comment objects below the article, which fit between the given dates


        """
        returnList=[]
        if type(art.freeData)==str:
            articleId=art.freeData
        else:
            self.getArticleDetails(art)
            articleId=art.freeData
        try:
            comments=spon.comments.by_article_id(articleId)
            returnList+=self.flattenComments(art,comments,None,0,start,end)
        except:
            print("Comment crawl error!")
            self.hasErrors=True
        return returnList


    def __del__(self):
        pass
  

if __name__ == '__main__':
   print("\n\n")
   print("-------------------------------------------------\n")
   print("Starting SpiegelOnlineScraper testcases here:\n\n")
   starttime=datetime.today()
   print("started at ",starttime)
   SpS=SponScraper()
   db=databaseExchange()
   db.connect()
   db.logStartCrawl(SpS.id)
   start=max(db.fetchLastRun(SpS.id).date(),date(2020,12,1))
   end=date.today()
   articleHeaderList=SpS.getArticlesList(start,end)
   db.writeArticles(articleHeaderList)
   todo=db.fetchTodoList(SpS.id)
   SpS.getWriteArticlesDetails(db,todo)
#   for art in todo:
#       print("fetching comments for article:",art)
#       cmts=SpS.getCommentsForArticle(art)
#       db.writeComments(cmts)
#       time.sleep(1)
   
   db.logEndCrawl(not(SpS.hasErrors))
   print("Laufzeit= ",datetime.today()-starttime)
   db.close()




