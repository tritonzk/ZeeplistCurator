import json
import os
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup as bs

from Console import Console
from Formatting import ZeepfileFormatting as zf

Workdirectory = os.getcwd()

class WorkshopScraper():
    def __init__(self):
        self.choicesDict = {} # choices from console
        self.tracklist = {} 

        # GTR
        self.gtr_popular = "https://api.zeepkist-gtr.com/levels/popular"
        self.gtr_hot = "https://api.zeepkist-gtr.com/levels/hot"
        self.gtr_points = "https://api.zeepkist-gtr.com/levels/points?SortByPoints=true&Ascending=false&Limit={}&Offset=0"

        # Zworpshop
        self.zworpshopGraphHql = "https://graphql.zworpshop.com/"
        self.randomlink = "https://api.zworpshop.com/levels/random?Amount={}"
        self.userlink = "https://api.zworpshop.com/levels/author/{}?IncludeReplaced=false"
        self.workshoplink = "https://api.zworpshop.com/levels/workshop/{}?IncludeReplaced=false"
        self.zworp_hash = "https://api.zworpshop.com/levels/hash/{}?IncludeReplaced=false&IncludeDeleted=false"

        self.searchWsLink = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=textsearch&section=readytouseitems"
        self.searchWsRecent = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=mostrecent&section=&actualsort=mostrecent&p=1"
        self.searchWsPopular = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=trend&section=&actualsort=trend&p=1&days=-1"


    def start(self):
        self.choicesDict = Console.console(self)
        if int(self.choicesDict["functionChoice"]) == 1:
            self.info_from_random(int(self.choicesDict["amount"]))
        elif int(self.choicesDict["functionChoice"]) == 2:
            self.info_from_workshopid(str(self.choicesDict["idchoice"]))
        elif int(self.choicesDict["functionChoice"]) == 3:
            if "steamUserId" in self.choicesDict:
                self.info_from_user(str(self.choicesDict["steamUserId"]))
            elif "authorId" in self.choicesDict:
                self.info_from_user(str(self.choicesDict["authorId"]))
        elif int(self.choicesDict["functionChoice"]) == 4:
            self.info_from_multiple_worshopid(self.ws_id_from_browsing(self.search_ws(self.choicesDict["searchTerm"], self.choicesDict["sorting"])))
        elif int(self.choicesDict["functionChoice"]) == 5: # Get tracks from GTR sorting
            if int(self.choicesDict["gtr_choice"]) == 1: # popular
                self.get_popular_hashes()
            elif int(self.choicesDict["gtr_choice"]) == 2: # hot
                self.get_hot_hashes()
            elif int(self.choicesDict["gtr_choice"]) == 3: # gtr points
                self.get_gtr_point_tracks()

        if len(self.tracklist) == 0:
            print("\nTrack list is empty. Try again")
            quit()

        for x in self.tracklist:
            print(self.tracklist[x])

        zf.zeepfile_Constructor(self, UIDDict = self.tracklist, filename = str(self.choicesDict["name"]), roundlength = int(self.choicesDict["roundlength"]), shuffle = self.choicesDict["shuffle"])
        input("\nDone! Press Enter to exit")

# ----------- Helper functions ---------------------

    def sort_to_tracklist(self, item):
        for x in item:
            self.tracklist[x["fileUid"]] = [x["name"], x["fileAuthor"], x["workshopId"]]

# ------------ Get GTR info -------------------------
            
    def get_popular_hashes(self):
        hashes = []
        popular_hashes = requests.get(self.gtr_popular)
        jsonfile = json.loads(popular_hashes.content)
        for x in jsonfile["levels"]:
            print(x)
            self.info_from_hash(x['level'])   

    def get_hot_hashes(self):
        hot_tracks = []
        hot = requests.get(self.gtr_hot)
        jsonfile = json.loads(hot.content)
        for x in jsonfile["levels"]:
            print(x)
            self.info_from_hash(x['level'])        
    
    def get_gtr_point_tracks(self):
        point_tracks = []
        try:
            point_tracks_with_limit = self.gtr_points.format(self.choicesDict["gtr_point_track_amount"])
        except:
            point_tracks_with_limit = self.gtr_points.format(100)
            print("you did not enter a track amount. Try again")
        point = requests.get(point_tracks_with_limit)
        jsonfile = json.loads(point.content)
        for x in jsonfile["items"]:
            print(x)
            self.info_from_hash(x['level'])

# ------------- Zworpshop callouts -------------------
            
    def info_from_hash(self, hash):
        hash_code = requests.get(self.zworp_hash.format(hash))
        jsonfile = json.loads(hash_code.content)
        self.sort_to_tracklist(jsonfile)

    def info_from_random(self, amount):
        randomtracks = requests.get(self.randomlink.format(str(amount)))
        jsonfile = json.loads(randomtracks.content)
        self.sort_to_tracklist(jsonfile)

    def info_from_workshopid(self, id):
        workshopitem = requests.get(self.workshoplink.format(id))
        jsonfile = json.loads(workshopitem.content)
        self.sort_to_tracklist(jsonfile)

    def info_from_multiple_worshopid(self, list):
        for x in list:
            print("ID = ", x)
            self.info_from_workshopid(x)
    
    def info_from_user(self, user):
        if "steamUserId" in self.choicesDict:
            userid = requests.get(self.workshoplink.format(str(user)))
            workshopfile = json.loads(userid.content)
            if "message" in workshopfile[0]:
                print("no such user")
                quit()
            user = workshopfile[0]["authorId"]
            
        usertracks = requests.get(self.userlink.format(str(user)))
        jsonfile = json.loads(usertracks.content)
        
        if "message" in jsonfile[0]:
            print("no such user")
            quit()
      
        for x in jsonfile:
            print(x)

        self.sort_to_tracklist(jsonfile)

# --------------- Searching -----------------------

    def search_ws(self, searchTerm, sorting):
        if int(sorting) == 1:
            print("relevant sorting")
            searchLink = self.searchWsLink.format(urllib.parse.quote(searchTerm))
        elif int(sorting) == 2:
            print("recent sorting")
            searchLink = self.searchWsRecent.format(urllib.parse.quote(searchTerm))
        elif int(sorting) == 3:
            print("popular sorting")
            searchLink = self.searchWsPopular.format(urllib.parse.quote(searchTerm))
        return searchLink
    
    def ws_id_from_browsing(self, browsingLink): 
        linklist = []
        idlist = []
        soup = bs(requests.get(browsingLink).text, "html.parser")
        ItemsOnPage = soup.find_all("a", class_="item_link", href=True)
        for x in ItemsOnPage:
            linklist.append(x.get("href"))
        for y in linklist:
            idlist.append(re.compile(r'\d+').search(y).group())
        return idlist

        
classy = WorkshopScraper()
classy.start()
# classy.get_popular_hashes()
# classy.get_gtr_point_tracks()