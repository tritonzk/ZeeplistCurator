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
        self.steamCMDWorkshopLocation = r"/steamcmd/steamapps/workshop/content/1440670/"
        self.wsLinkTemplate = r"https://steamcommunity.com/sharedfiles/filedetails/?id="
        
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

        self.extract_info_from_steamCMD_downloads()
        zf.zeepfile_Constructor(self.UID_dict, filename = "{}".format(self.choicesDict["name"]), roundlength = int(self.choicesDict["roundlength"]), shuffle = self.choicesDict["shuffle"])

        if self.choicesDict["delete"]:
            shutil.rmtree(Workdirectory + self.steamCMDWorkshopLocation)


    def console(self):
        print("----------------------------------------------------------------------------------------------------")
        print("Welcome to ZeepkistScraper. Python script written by Triton")
        print("This script searches the Steam workshop for random or specific tracks and gives you a Zeepkist playlist in return.\n")

        print("1: Download randomly")
        print("2: Download specific workshop ID")
        print("3: create playlist from currently downloaded files")
        functionChoice = input("Enter a choice (1,2, 3): ---> ")

        print("")

        if functionChoice == "2":
            idChoice = input("Enter workshop ID: ---> ")
            self.choicesDict["idchoice"] = idChoice
            print("")
        
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

            # if filterChoice == "2" or "4":
            #     print("")
            #     nAmount = input("N?: ---> ")
            # elif filterChoice == "1" or "2" or "3" or "4":
            #     print("")
            #     workshopAmountChoice = input("How many workshop items to download?: ---> ")
            # else:
            #     print("not a valid input.")
            #     quit()

            filterChoice = input("use \"1 level\" in description filter? (y/n) ---> ")

            workshopAmountChoice = input("How many workshop items to download?: ---> ")
            self.choicesDict["amount"] = workshopAmountChoice

        playlistName = input("name of playlist?: ---> ")
        roundLength = input("length of round in seconds: ---> ")
        shuffleChoice = input("shuffle? (y/n): ---> ")
        if shuffleChoice == "y" or "Y":
            shuffleChoice = True
        elif shuffleChoice == "n" or "N":
            shuffleChoice = False
        
        deleteAfter = input("delete workshop files after download? (y/n)")
        if deleteAfter == "y" or "Y":
            deleteAfter = True
        elif deleteAfter == "n" or "N":
            deleteAfter = False

        # movePlaylist = input("__EXPERIMENTAL__ try copying the playlist file to local appdata zeepkist storage? (y/n): ---> ")

        self.choicesDict["name"] = playlistName
        self.choicesDict["roundlength"] = roundLength
        self.choicesDict["functionChoice"] = functionChoice
        self.choicesDict["shuffle"] = shuffleChoice
        self.choicesDict["delete"] = deleteAfter
        self.choicesDict["filter"] = filterChoice
      
        print("choices: ", self.choicesDict)


# ------------- webscraping and extracting info------------------------------------------------------------------
 
    # what number is the last workshop page? -> int
    def find_max_page(self):
        soup = bs(requests.get(self.zeepLink + "p=1").text, "html.parser")
        pageNumberLinks = soup.find_all("a", class_="pagelink")
        regSearch = re.compile("\>(\\d+)")
        match = regSearch.search(str(pageNumberLinks[-1]))
        maxPage = int(match.group()[1:])
        return maxPage


#-------------randomizer elements-------------------------------------------------------------------------------------
# create a random workshop ID
# deal with ws items that have multiple tracks
# choices: include all, choose random(n) per ws item, ignore ws items that don't start with 1,   

    # add option to ignore when description doesn't start with 1
    def workshop_random_link(self):   
        linklist = []
        rPageNumber = rand.randint(0, self.find_max_page())
        response = requests.get(self.zeepLink +  "p={}".format(rPageNumber))
        soup = bs(response.text, "html.parser")
        ItemsOnPage = soup.find_all("a", class_="item_link", href=True)

        for x in ItemsOnPage:
            linklist.append(x.get("href"))
     
        return re.compile(r'\d+').search(linklist[rand.randint(0,29)]).group()

    def get_workshop_description(self, workshopId):
        fullWorkshopLink = self.wsLinkTemplate + workshopId
        print(fullWorkshopLink)
        response = requests.get(fullWorkshopLink)
        soup = bs(response.text, "html.parser")
        descriptionSearch = soup.find("div", class_="workshopItemDescription")
        workshopDescription = descriptionSearch.get_text()
        return workshopDescription

    # might do this dynamically. When a WS item comes up as non default, what to do?
    def check_default_description():
        pass
    
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
        os.chdir(Workdirectory + self.steamCMDWorkshopLocation)
        items = os.listdir(".")

        # check files in each WS folder
        for x in range(0, len(os.listdir("."))):
            os.chdir(Workdirectory + self.steamCMDWorkshopLocation + items[x])

            # add location of zeepfile to dict if items are folders
            for y in os.listdir("."):
                if os.path.isdir(y):
                    self.zeeplevel_file_path[y] = items[x] + "/" + y + "/" + y + ".zeeplevel"

        # extract UID and Author from zeepfiles to UID_dict
        for x in self.zeeplevel_file_path.keys():
            with open(Workdirectory + self.steamCMDWorkshopLocation + "/" + self.zeeplevel_file_path[x]) as csvfile:
                csvObject = csv.reader(csvfile, delimiter = ',')
                zeepUserData = next(csvObject)[1:]
            self.UID_dict[x] = zeepUserData
            self.UID_dict[x].insert(0, self.zeeplevel_file_path[x][:10])
            

        #print("file_path", self.zeeplevel_file_path)        
        print("UID dict ", self.UID_dict)
        print("items ", items)
    
classy = WorkshopScraper()
classy.start()

# classy.filter_level_amount()