#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import json

SLEEP_TIME = 2

threadId = "<THREAD ID HERE>"
saveFileName = "{}.json".format(threadId)

saBaseUrl = "http://forums.somethingawful.com/"
myCookies = {
    "bbuserid":"<BBUSERID HERE>",
    "bbpassword":"<BBPASSWORD HERE>",
    "aduserid":"<ADUSERID HERE>",
    "__csdrc":"<CSDRC HERE>",
    "sessionid":"<SESSIONID HERE>",
    "sessionhash":"<SESSIONHASH HERE>",
    "popunder":"yes",
    "popundr":"yes",
    "setover18":"1"
}

class ImageInfo:
    
    def __init__(self, imgUrl, threadId, userName, postedDate, postId):
        
        self.imgUrl = imgUrl
        self.threadId = threadId
        self.userName = userName
        self.postedDate = postedDate
        self.postId = postId
        
    
    def getObject(self):
        return {
            "imgUrl":self.imgUrl,
            "threadId":self.threadId,
            "userName":self.userName,
            "postedDate":self.postedDate,
            "postId":self.postId,
        }
    
#end ImageInfo class


class AwfulImageScrape:
    
    def __init__(self):
        
        self.config = {
            'doSave': True,
            'debug': True,
            'sleepTimeMin': 4,
            'sleepTimeMax': 7,
        }
        
        self.imgLinks = []
        self.imgObj = []
        try:
            print "loading json file"
            f = open(saveFileName, "r")
            links = f.read().split()
            f.close()
            for link in links:
                self.imgLinks.append(link)
            print "json file loaded"
        except Exception , e :
            print e
            f = open(saveFileName, "w+")
            f.close()
            #sys.exit('don wan no trabaou')
        
        
        self.filterList = [
            'waffleimages.com',
            'somethingawful.com',
            'photos.cx',
            'imagehost.org',
            'attachment'
        ]
        
    #end init
    
    def grabFromThread(self, threadid, cookies, startPage, endPage):
        #get the html
        #req = requests.get(saBaseUrl + 'showthread.php?threadid=' + threadid, cookies=cookies)
        
        #"{}showthread.php?threadid={}&perpage={}&pagenumber={}".format(saBaseUrl,threadid,40,0)
        
        for pageNum in range(startPage,endPage+1):
            req = requests.get("{}showthread.php?threadid={}&perpage={}&pagenumber={}".format(saBaseUrl,threadid,40,pageNum), cookies=cookies)
            
            """
            if self.config['debug']:
                print '#'*5 , "Request Text"
                print req.text
            """
            
            
            #now grab the content of the posts
            parsed_html = BeautifulSoup(req.text, "html.parser")
            posts = parsed_html.body.findAll('td', attrs={'class':'postbody'})
            
            posts_all = parsed_html.body.findAll('table', attrs={'class':'post'})
            
            for post in posts_all:
                
                #grab information from post
                postUserName = post.find('dt', attrs={'class':'author'}).text
                postBody = post.find('td', attrs={'class':'postbody'})
                postDate = post.find('td', attrs={'class':'postdate'})
                
                postUserId = postDate.find('a', attrs={'class':'user_jump'})['href'].split('=')[2]
                postLink = postDate.find('a', attrs={'title':'Link to this post'})['href']
                postDateVal = postDate.text.split('?')[1].strip()
                
                print "*"*10 , 'POST:'
                print postUserName
                print postUserId
                print postLink
                print postDateVal
                
                imgs = post.findAll('img')
                for img in imgs:
                    keepImg = True
                    #remove items that are in filter
                    for filter in self.filterList:
                        if filter in img['src']:
                            keepImg = False
                            break
                    #dont keep images that are copies
                    if keepImg and (img['src'] not in self.imgLinks):
                        print img['src']
                        self.imgLinks.append(img['src'])
                        self.imgObj.append(
                            ImageInfo(
                                img['src'],
                                threadid,
                                postUserName,
                                postDateVal,
                                postLink
                            ))
                    #endif
                
            #end for loop
            
            print "---------------------------------"
            print "page " + str(pageNum)
            
            time.sleep(random.randint(self.config['sleepTimeMin'],self.config['sleepTimeMax']))
        #end pageNum loop
        
        
        #write the links to a file
        if self.config['doSave']:
            self.saveFile()
        
    #end grabFromThread function
    
    def saveFile(self):
        f = open(saveFileName,'w')
        outObj = {"threadId":threadId,
            "imageList" : [ imageObj.getObject() for imageObj in self.imgObj]
        }
        f.write(json.dumps(outObj))
        f.close()
    #end saveFile function
    
#end AwfulImageScrape class

def main():
    scrape = AwfulImageScrape()
    
    scrape.grabFromThread(threadId,myCookies,200,200)

    
if __name__ == '__main__':
    main()



