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


from bs4 import BeautifulSoup as bs

Workdirectory = os.getcwd()
zf = ZeepfileFormatting()

# install Steamcmd if not installed yet
if "steam.dll" not in os.listdir("SteamCmd/"):
    print('first time install for SteamCMD')
    subprocess.run("SteamCmd/steamcmd.exe")

# container for Todo's
def comments():
    # _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-Base functionality V0.1a_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
    # - Workshopscraper (amount, ) -> zeeplist playlist

    # [V] generate random WS page
    # [V] extract info from page ([V] workshopID, [V] workshop description)
    # [V] download WS files using SteamCMD and WS id list
    # [V] extract info from file (author, authorUID, track name)      
    # [V] format and export info into zeepfile/json format
    # [V] download a specific WS ID and add to playlist
    # [V] delete WS files when done
    # [V] simple console interface
    # [] ignore WS pages that do not have "1 level" in their description

    # _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-extra functionality V0.2_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
    # [] download and install SteamCMD automatically or make helper script.

    # ------interface
    # [] better console interface (use simple term menu?)

    # -------move files to correct place
    # [] move the playlist file to local storage
    # [] move downloaded WS files to steam folder?

    # -------filters
    # [] ignore WS pages above a certain "N level" in their description
    # [] add a random amount from each downloaded WS item to the playlist
    # [] add all WS items downloaded via steamCMD into playlists (option to limit amount per playlist)

    # -------alternate ways to search
    # [V] download first 30 relevant from search term
    # [] crawl until finding a WS item that contains more than N items --> add to a playlist
    # [] search a specific range of pages
    # [] search popular or other sorting methods


    # [] search metadata using WebApi (requires an API key). This allow me to check with more accuracy how many tracks a workshop item has.
    #           The user has to provide their own API key.

    # _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-FUTURE-Version-?_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
    # create binary to reduce dependencies (use pyinstaller?)
    # make it into a Bepinx mod? (might require rewrite into c#)

    # random map challenge functionality (maybe separate mod)
        # timer
        # customizable rules
        # point counter


    # ------------------------------------------BUGS/ISSUES-------------------------------------------
    # how to close out from steamCMD after install?
    # extract_info_from_steamCMD is broken. find better way to format, store and iterate over filepaths.

    pass


class WorkshopScraper():
    def __init__(self):
        # dicts and lists
        self.zeeplevelIDs = []
        self.UID_dict = {} 
        self.zeeplevel_file_path = {}
        self.choicesDict = {}

        # variables
        self.zeepLink = r"https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext=&childpublishedfileid=0&browsesort=mostrecent&section=readytouseitems&requiredtags%5B0%5D=1+Level&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0&actualsort=mostrecent&"
        self.wsLinkTemplate = r"https://steamcommunity.com/sharedfiles/filedetails/?id="
        self.searchWsLink = r"https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&childpublishedfileid=0&browsesort=textsearch&section=readytouseitems&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0"
        
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

        self.extract_info_from_steamCMD_downloads()
        zf.zeepfile_Constructor(self.UID_dict, filename = "{}".format(self.choicesDict["name"]), roundlength = int(self.choicesDict["roundlength"]), shuffle = self.choicesDict["shuffle"])

        if self.choicesDict["delete"] == True:
            shutil.rmtree(Workdirectory + self.steamCMDWorkshopLocation)


    def console(self):
        print("----------------------------------------------------------------------------------------------------")
        print("Welcome to ZeepkistScraper. Python script written by Triton")
        print("This script searches the Steam workshop for random or specific tracks and gives you a Zeepkist playlist in return.\n")

        print("1: Download randomly")
        print("2: Download specific workshop ID")
        print("3: create playlist from currently downloaded files")
        print("4: create playlist from first 30 searchresults")
        functionChoice = input("Enter a choice (1,2,3,4): ---> ")

        

        if functionChoice == "2":
            idChoice = input("Enter workshop ID: ---> ")
            self.choicesDict["idchoice"] = idChoice
            print("")

        elif functionChoice == "4":
            print("")
            searchTerm = input("enter search term: ---> ")
            self.choicesDict["searchTerm"] = searchTerm
        
        elif functionChoice == "3":
            print("")
            pass


        elif functionChoice == "1":
            print("")

            # print("Sometimes a workshop item has multiple tracks. How do you want to proceed?\n")
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

    # what number is the last workshop page? -> int
    def find_max_page(self, wsLink):
        soup = bs(requests.get(wsLink).text, "html.parser")
        pageNumberLinks = soup.find_all("a", class_="pagelink")
        regSearch = re.compile("\>(\\d+)")
        match = regSearch.search(str(pageNumberLinks[-1]))
        maxPage = int(match.group()[1:])
        return maxPage
    
    def extract_id_from_wslink(self, wsLink):
        return re.compile(r'\d+').search(wsLink).group()

    def get_workshop_description(self, workshopId):
        fullWorkshopLink = self.wsLinkTemplate + workshopId
        print(fullWorkshopLink)
        response = requests.get(fullWorkshopLink)
        soup = bs(response.text, "html.parser")
        descriptionSearch = soup.find("div", class_="workshopItemDescription")
        workshopDescription = descriptionSearch.get_text()
        return workshopDescription


#-------------randomizer and filter elements-------------------------------------------------------------------------------------
    
    def random_page(self):
        return self.zeepLink + "p={}".format(rand.randint(0, self.find_max_page(self.zeepLink + "p=1")))


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


    # return random WS id
    def workshop_random_link(self):   
        linklist = []
        rPageNumber = rand.randint(0, self.find_max_page(self.zeepLink + "p=1"))
        response = requests.get(self.zeepLink +  "p={}".format(rPageNumber))
        soup = bs(response.text, "html.parser")
        ItemsOnPage = soup.find_all("a", class_="item_link", href=True)

        for x in ItemsOnPage:
            linklist.append(x.get("href"))
     
        return self.extract_id_from_wslink(linklist[rand.randint(0,29)])


    # might do this dynamically. When a WS item comes up as non default, what to do?
    def check_default_description():
        pass
    
    # try to get the amount of levels from WS items through WebApi. 
    # Maybe steamctl is not necessary for this? Find alternative.
    def web_api_metadata(self, workshopId):
        
        wsMetadata = subprocess.run(r'steamctl --anonymous workshop info {}'.format(workshopId))

        # https://api.steampowered.com/IPublishedFileService#RankedByPublicationDate/QueryFiles/v1/?key=6AF761D8AAFC379024BB5DBA0F5070A8&appid=1440670&page=50%numberpage=3%return_tags=true
        # count=3
        
        
        
        # query_type=k_PublishedFileQueryType_RankedByPublicationDate
        # numberpage=
        # page=50
        # https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=440&count=3

        # search_text	string	✔	Text to match in the item's title or description



        print(wsMetadata)

    # create a link from a searchterm
    def search_ws(self, searchTerm):
        searchLink = self.searchWsLink.format(urllib.parse.quote(searchTerm))
        return searchLink

    # filter for "N levels"
    def filter_level_amount(self):
        randomLink = self.workshop_random_link()
        description = self.get_workshop_description(randomLink)
        print(re.compile(r'/^(.*?)levels/').search(description))
        print(description[0])
        

# --------------------download-------------------------------------------------------------------
# options: ignore multiple levels (description?), sorting rules (currently only recent)

    # download files using a list of workshop Id's
    def steamCMD_downloader(self, IdList):
        os.chdir(Workdirectory + "/steamcmd")
        dlCommand = ""

        for x in range(0, len(IdList)):
            dlCommand += " +workshop_download_item 1440670 {workshopId}".format(workshopId = IdList[x])

        subprocess.run("steamcmd +login anonymous{} +quit".format(dlCommand))

    # [V] create dict with workshop Id, author and UID extracted from zeepfiles
    def extract_info_from_steamCMD_downloads(self):    
        os.chdir(self.steamCMDWorkshopLocation)
        # print(self.steamCMDWorkshopLocation)
        items = os.listdir(".")

        #change dir to ws folder
        for x in range(0, len(items)):
            os.chdir(self.steamCMDWorkshopLocation + items[x])

        #   
            for y in os.listdir("."):
                if os.path.isdir(y):
                    os.chdir(self.steamCMDWorkshopLocation + items[x] + "\\" + y)
                    for z in os.listdir("."):
                        
                        if z[-10:] == ".zeeplevel":
                            # print(z)
                            self.zeeplevel_file_path[y] = self.steamCMDWorkshopLocation + items[x] + "\\" + y + "\\" + z

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

# print(classy.steamCMDWorkshopLocation)

# classy.extract_info_from_steamCMD_downloads()
# classy.ws_id_from_browsing(classy.search_ws(/\"flore#"))

# classy.web_api_metadata("2804222316")


# test = 'C:\\Users\\Thijmen\\Documents\\GitHub\\ZeepkistRandomizer\\SteamCmd\\steamapps\\workshop\\content\\1440670\\2981839136\\flore#10\\flore#10 .zeeplevel'

# splitTest = test.split('1440670')
# print(splitTest[1][1:11])


# classy.filter_level_amount()