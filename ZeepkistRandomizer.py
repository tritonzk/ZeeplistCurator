from Formatting import ZeepfileFormatting

from pathlib import Path
import subprocess
import requests
import random as rand
import re
import os
import json
import csv
import shutil
import urllib.parse
import zipfile


from bs4 import BeautifulSoup as bs

Workdirectory = os.getcwd()
zf = ZeepfileFormatting()

SteamCmdLink = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"

# create SteamCmd folder if none is found
if "SteamCmd" not in os.listdir(Workdirectory):
    print("creating SteamCmd folder")
    os.mkdir("SteamCmd")

# install Steamcmd if not installed yet
if "steam.dll" not in os.listdir("SteamCmd/"):
    print('first time install for SteamCMD')
    os.chdir(Workdirectory + "SteamCmd")
    response = requests.get(SteamCmdLink)
    file = open("SteamCmd.zip", "wb")
    file.write(response.content)
    file.close()
    with zipfile.ZipFile(Workdirectory + "\\tmp\\SteamCmd.zip", 'r') as zip_ref:
        zip_ref.extractall(Workdirectory + "\\tmp")
    os.remove(Workdirectory + "\\tmp\\SteamCmd.zip")
    subprocess.run("SteamCmd/steamcmd.exe")


# container for Todo's
def comments():
    # ------------------------------------------BUGS/ISSUES/TO-DO---------------------------------------------------------------
    # [9] download multiple pages from a steamuser workshop page.

    # [1] how to close out from steamCMD after install?
    # [1] the download command can be too long. After a certain amount the command stops working. might be another issue? requires more testing
    pass


class WorkshopScraper():
    def __init__(self):
        # dicts and lists
        self.zeeplevelIDs = [] # list of all workshop ids
        self.UID_dict = {} # info for playlist
        self.zeeplevel_file_path = {} # file path by track name
        self.choicesDict = {} #choices from console

        # variables
        self.zeepLink = r"https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext=&childpublishedfileid=0&browsesort=mostrecent&section=readytouseitems&requiredtags%5B0%5D=1+Level&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0&actualsort=mostrecent&"
        self.wsLinkTemplate = r"https://steamcommunity.com/sharedfiles/filedetails/?id="
        self.searchWsLink = r"https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=textsearch&section=readytouseitems"
        self.steamuserWorkshop = r"https://steamcommunity.com/id/{user}/myworkshopfiles/?appid=1440670&p={page}&numperpage=30".format(user = "", page = 1)
        
        self.steamCMDWorkshopLocation = Workdirectory + "\\SteamCmd\\steamapps\\workshop\\content\\1440670\\"

        
        # Zeepfile formatting dicts
        self.ZeeplistFormat = {
            "name" : "",
            "amountOfLevels" : 0,
            "roundLength" : 0,
            "shufflePlaylist" : False,
            "levels": [
            ]
        }
        self.ZeepWSFormat = {
            "UID": "",
            "WorkshopID": 0,
            "Name": "",
            "Author": ""
        }

    # start function
    def start(self):
        self.console()

        if int(self.choicesDict["functionChoice"]) == 2:
            dlSingle = [self.choicesDict['idchoice']]
            self.steamCMD_downloader(dlSingle)
        elif int(self.choicesDict["functionChoice"]) == 1:
            for _ in range(0, int(self.choicesDict["amount"])):
                self.zeeplevelIDs.append(self.workshop_random_link())
            self.steamCMD_downloader(self.zeeplevelIDs)
        elif int(self.choicesDict["functionChoice"]) == 4:
            self.steamCMD_downloader(self.ws_id_from_browsing(self.search_ws(self.choicesDict["searchTerm"])))
        elif int(self.choicesDict["functionChoice"]) == 5:
            if int(self.choicesDict["steamUserPage"]) == 1:
                self.steamCMD_downloader(self.get_user_tracks(self.choicesDict["steamUser"], 1))
            else:    
                for x in range(1, int(self.choicesDict["steamUserPage"])):
                    self.steamCMD_downloader(self.get_user_tracks(self.choicesDict["steamUser"], x))

        self.extract_info_from_steamCMD_downloads()
        zf.zeepfile_Constructor(self.UID_dict, filename = "{}".format(self.choicesDict["name"]), roundlength = int(self.choicesDict["roundlength"]), shuffle = self.choicesDict["shuffle"])

        if self.choicesDict["delete"] == True:
            shutil.rmtree(self.steamCMDWorkshopLocation)

    # terminal interface
    def console(self):
        print("----------------------------------------------------------------------------------------------------")
        print("Welcome to ZeepkistRandomizer. Python script written by Triton")
        print("This script searches the Steam workshop for random or specific tracks and gives you a Zeepkist playlist in return.\n")

        print("1: Download randomly")
        print("2: Download specific workshop ID")
        print("3: create playlist from currently downloaded files")
        print("4: create playlist from first 30 searchresults")
        print("5: create playlist from first 30 from steamuser")
        functionChoice = input("Enter a choice (1,2,3,4,5): ---> ")

        

        if functionChoice == "2":
            print("")
            self.choicesDict["idchoice"] = input("Enter workshop ID: ---> ")
            

        elif functionChoice == "4":
            print("") 
            self.choicesDict["searchTerm"] = input("enter search term: ---> ")
        
        elif functionChoice == "3":
            print("")
            pass

        elif functionChoice == "5":
            print("for the steamuserID go to a steamuser workshop page and copy \n https://steamcommunity.com/profiles/___SteamUserId___/myworkshopfiles/")
            self.choicesDict["steamUser"] = input("enter SteamUserId: ---> ")
            maxpage = self.find_max_page(self.steamuserWorkshop.format(user = self.choicesDict["steamUser"], page = 1))
            print("Steampage has {} ".format(maxpage) + "pages. How many do you want to download?")
            self.choicesDict["steamUserPage"] = input("enter amount of pages: ---> ")

        elif functionChoice == "1":
            print("")

            # print("Somet imes a workshop item has multiple tracks. How do you want to proceed?\n")
            # print("1: No filter (Purely random, use at your own risk. Sometimes workshop items have 50+ tracks.)")
            # print("2: No filter. But choose a max number N of tracks per workshop item that are randomly added to the playlist.")
            # print("3: Ignore workshop items that do not state \"1 level\" in their description.")
            # print("4: Ignore workshop items above a certain N \"N level\" in their description.")
            # filterChoice = input("Enter a choice (1,2,3,4): ---> ")


            # filterChoice = input("use \"1 level\" in description filter? (y/n) ---> ")
            # self.choicesDict["filter"] = filterChoice

            #pagerange

            workshopAmountChoice = input("How many workshop items to download?: ---> ")
            self.choicesDict["amount"] = workshopAmountChoice

        playlistName = input("name of playlist?: ---> ")
        roundLength = input("length of round in seconds: ---> ")
        shuffleChoice = input("shuffle? (y/n): ---> ")
        if shuffleChoice == ("y" or "Y"):
            shuffleChoice = True
        elif shuffleChoice == ("n" or "N"):
            shuffleChoice = False
        
        deleteAfter = input("delete workshop files after download? (y/n): ---> ")
        if deleteAfter == ("y" or "Y"):
            deleteAfter = True
        elif deleteAfter == ("n" or "N"):
            deleteAfter = False

        # movePlaylist = input("__EXPERIMENTAL__ try copying the playlist file to local appdata zeepkist storage? (y/n): ---> ")

        self.choicesDict["name"] = playlistName
        self.choicesDict["roundlength"] = roundLength
        self.choicesDict["functionChoice"] = functionChoice
        self.choicesDict["shuffle"] = shuffleChoice
        self.choicesDict["delete"] = deleteAfter
        
        print("choices: ", self.choicesDict)


# ------------- webscraping and extracting info------------------------------------------------------------------


    # [V] what number is the last workshop page? -> int
    def find_max_page(self, wsLink):
        soup = bs(requests.get(wsLink).text, "html.parser")
        pageNumberLinks = soup.find_all("a", class_="pagelink")
        regSearch = re.compile("\>(\\d+)")
        match = regSearch.search(str(pageNumberLinks[-1]))
        maxPage = int(match.group()[1:])
        return maxPage
    
    # [V]
    def extract_id_from_wslink(self, wsLink):
        return re.compile(r'\d+').search(wsLink).group()
    
    # [V]
    def get_workshop_description(self, workshopId):
        fullWorkshopLink = self.wsLinkTemplate + workshopId
        print(fullWorkshopLink)
        response = requests.get(fullWorkshopLink)
        soup = bs(response.text, "html.parser")
        descriptionSearch = soup.find("div", class_="workshopItemDescription")
        workshopDescription = descriptionSearch.get_text()
        return workshopDescription
    
    # [V]
    def random_page(self):
        return self.zeepLink + "p={}".format(rand.randint(0, self.find_max_page(self.zeepLink + "p=1")))

    # [V] Download all items from a browser URL
    def ws_id_from_browsing(self, browsingLink): 
        # check for multiple pages
        # extract links from page
        linklist = []
        idlist = []
        soup = bs(requests.get(browsingLink).text, "html.parser")
        ItemsOnPage = soup.find_all("a", class_="item_link", href=True)
        for x in ItemsOnPage:
            linklist.append(x.get("href"))
            #extract all links
        for y in linklist:
            idlist.append(self.extract_id_from_wslink(y))
        return idlist

    # [V] return random WS id
    def workshop_random_link(self):   
        linklist = []
        rPageNumber = rand.randint(0, self.find_max_page(self.zeepLink + "p=1"))
        response = requests.get(self.zeepLink +  "p={}".format(rPageNumber))
        soup = bs(response.text, "html.parser")
        ItemsOnPage = soup.find_all("a", class_="item_link", href=True)
        for x in ItemsOnPage:
            linklist.append(x.get("href"))
        return self.extract_id_from_wslink(linklist[rand.randint(0,29)])

    # [X] might do this dynamically. When a WS item comes up as non default, what to do?
    def check_default_description():
        pass
    
    # Maybe steamctl is not necessary for this? Find alternative. 
    # [~] try to get the amount of levels from WS items through WebApi. 
    def web_api_metadata(self, workshopId):
        
        wsMetadata = subprocess.run(r'steamctl --anonymous workshop info {}'.format(workshopId))

        print(wsMetadata)

    # [V] create a link from a searchterm
    def search_ws(self, searchTerm):
        searchLink = self.searchWsLink.format(urllib.parse.quote(searchTerm))
        return searchLink

    # [~] filter for "N levels"
    def filter_level_amount(self):
        randomLink = self.workshop_random_link()
        description = self.get_workshop_description(randomLink)
        print(re.compile(r'/^(.*?)levels/').search(description))
        print(description[0])
    
    # Downloads stop working for an N? amount, split op the command to fix?
    # [V] download files using a list of workshop Id's
    def steamCMD_downloader(self, IdList):
        os.chdir(Workdirectory + "/steamcmd")
        dlCommand = ""
        for x in range(0, len(IdList)):
            dlCommand += " +workshop_download_item 1440670 {workshopId}".format(workshopId = IdList[x])
        subprocess.run("steamcmd +login anonymous{} +quit".format(dlCommand))

    def get_user_tracks(self, user, page):
       
        tracklist = []
        soup = bs(requests.get(self.steamuserWorkshop.format(user = user, page = page)).text, "html.parser")
        tracks = soup.find_all("a", class_="ugc", href=True)
        # print(tracks)
        for x in tracks:
            tracklist.append(x.get("data-publishedfileid"))
        return tracklist

    # [V] create dict with workshop Id, author and UID extracted from zeepfiles
    def extract_info_from_steamCMD_downloads(self):    

        os.chdir(self.steamCMDWorkshopLocation)
        # print(self.steamCMDWorkshopLocation)
        items = os.listdir(".")
        print("items ", items)
        files = folders = 0
       
        # count amount of folders
        for _, dirnames, filenames in os.walk("."):
            files += len(filenames)
            folders += len(dirnames)
        amountOfTracks = folders - len(items)
        print("amount of tracks: ", amountOfTracks)

        for x in items:
            os.chdir(self.steamCMDWorkshopLocation + x)
            tracks = os.listdir(".")
            print("tracks ", tracks)
            for y in tracks:
                print("track", y)
                if os.path.isdir(self.steamCMDWorkshopLocation + x + "\\" + y):
                    os.chdir(self.steamCMDWorkshopLocation + x + "\\" + y) 
                    for z in os.listdir("."):
                        if z[-10:] == ".zeeplevel":
                            self.zeeplevel_file_path[y] = self.steamCMDWorkshopLocation + x + "\\" + y + "\\" + z

        # extract UID and Author from zeepfiles to UID_dict
        for x in self.zeeplevel_file_path.keys():
        
            with open(self.zeeplevel_file_path[x]) as csvfile:
                csvObject = csv.reader(csvfile, delimiter = ',')
                zeepUserData = next(csvObject)[1:]
            self.UID_dict[x] = zeepUserData
            splitPath = self.zeeplevel_file_path[x].split('1440670')
            self.UID_dict[x].insert(0, splitPath[1][1:11])
        

        

        print("\nfile_path", self.zeeplevel_file_path)        
        print("\n___UID dict: ", self.UID_dict)
        print("\n___Workshop Id's: ", items, "\n")
    
classy = WorkshopScraper()
classy.start()

