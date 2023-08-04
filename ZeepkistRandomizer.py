from Formatting import ZeepfileFormatting

from pathlib import Path
import subprocess
import requests
import random as rand
import re
import os
import json
import csv

from bs4 import BeautifulSoup as bs

Workdirectory = os.getcwd()
zf = ZeepfileFormatting()

# container for Todo's
def comments():
    # _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-Base functionality V0.1a_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
    # - Workshopscraper (amount, ) -> zeeplist playlist

    # [V] generate random WS page
    # [~] extract info from page ([~] workshop metadata, [V] workshop ID)
    # [V] download WS files using SteamCMD and WS id list
    # [V] extract info from file (author, authorUID, filename)      
    # [V] format and export info into zeepfile/json format
    # [] download a specific WS ID and add to playlist
    # [] delete WS files when done
    # [] simple console interface
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


    # _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-FUTURE-Version-?_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
    # create binary to reduce dependencies
    # make it into a Bepinx mod? (might require rewrite into c#)

    # random map challenge functionality (maybe separate mod)
        # timer
        # customizable rules
        # point counter
    pass


# Input questions
def console_prompt():
    print("----------------------------------------------------------------------------------------------------")
    print("Welcome to ZeepkistScraper. Python script written by Triton")
    print("This script searches the Steam workshop for random or specific tracks and gives you a Zeepkist playlist in return.\n")
    
    print("1: Download randomly")
    print("2: Download specific workshop ID")
    functionChoice = input("Enter a choice (1,2): ---> ")
    
    print(functionChoice, type(functionChoice))

    if "1" or "2" not in functionChoice:
        print("invalid input")
        quit()

    print("")

    if int(functionChoice) == 2:
        idChoice = input("Enter workshop ID: ---> ")
        print("")
    
    else:

        print("Sometimes a workshop item has multiple tracks. How do you want to proceed?\n")
        print("1: No filter (Purely random, use at your own risk. Sometimes workshop items have 50+ tracks.)")
        print("2: No filter. But choose a max number N of tracks per workshop item that are randomly added to the playlist.")
        print("3: Ignore workshop items that do not state \"1 level\" in their description.")
        print("4: Ignore workshop items above a certain N \"N level\" in their description.")
        filterChoice = input("Enter a choice (1,2,3,4): ---> ")

        if filterChoice == "2" or "4":
            print("")
            nAmount = input("N?: ---> ")
        elif filterChoice == "1" or "2" or "3" or "4":
            print("")
            workshopAmountChoice = input("How many workshop items to download?: ---> ")
        else:
            print("not a valid input.")
            quit()

    playlistName = input("name of playlist?: ---> ")
    roundLength = input("length of round in seconds: ---> ")
    shuffleChoice = input("shuffle? (y/n): ---> ")
    movePlaylist = input("__EXPERIMENTAL__ try copying the playlist file to local appdata zeepkist storage? (y/n): ---> ")

console_prompt()

class WorkshopScraper():
    def __init__(self):
        #obsolete?
        self.zeeplevelIDs = []
      
        # dicts and lists
        self.UID_dict = {} 
        self.zeeplevel_file_path = {}

        # variables
        self.zeepLink = r"https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext=&childpublishedfileid=0&browsesort=mostrecent&section=readytouseitems&requiredtags%5B0%5D=1+Level&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0&actualsort=mostrecent&"
        self.steamCMDWorkshopLocation = r"/steamcmd/steamapps/workshop/content/1440670/"
        

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

    #input function that accepts the info and calls all other functions.
    def start(self, amount : int):
        for _ in range(0, amount):
            self.zeeplevelIDs.append(self.workshop_random_link())
        
        self.steamCMD_downloader(self.zeeplevelIDs)
        self.extract_info_from_steamCMD_downloads()
        print(self.UID_dict)

        zf.zeepfile_Constructor(self.UID_dict, filename = "_generatedTest_{}_".format(rand.randint(0,1000)))
        

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

# 

    # add option to ignore when description doesn't start with 1
    def workshop_random_link(self):   
        linklist = []
        rPageNumber = rand.randint(0, self.find_max_page())
        response = requests.get(self.zeepLink +  "p={}".format(rPageNumber))
        soup = bs(response.text, "html.parser")
        ItemsOnPage = soup.find_all("a", class_="item_link", href=True)
        # re.compile(r'\d+').search(linklist[rand.randint(0,29)]).group()
        # randomItem = ItemsOnPage[rand.randint(0,29)].get("href")
        # print(randomItem)
        # soup = bs(requests.get(randomItem).text, "html.parser")
        # wsDescription = soup.find_all("div", class_="workshopItemDescription")

        # print(wsDescription)
        # if 

        for x in ItemsOnPage:
        #     soup = bs(x.group().text, "html.parser")
        #     description = soup.find_all("levels", class_="workshopItemDescription")
        #     if  description.group()[0] == 1:
            linklist.append(x.get("href"))
        #     else:
        #         pass

        # return re.compile(r'\d+').search(linklist[rand.randint(0,29)]).group()
       
    
        




# --------------------download-------------------------------------------------------------------
# options: ignore multiple levels (description?), sorting rules (currently only recent)

    # download files using a list of workshop Id's
    def steamCMD_downloader(self, IdList):
        os.chdir(Workdirectory + "/steamcmd")
        steamCMDWorkshopString = ""

        for x in range(0, len(IdList)):
            steamCMDWorkshopString += " +workshop_download_item 1440670 {workshopId}".format(workshopId = IdList[x])

        subprocess.run("steamcmd +login anonymous{} +quit".format(steamCMDWorkshopString))

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
            

                
        
        print("file_path", self.zeeplevel_file_path)        
        print("UID dict ", self.UID_dict)
        print("items ", items)
    

    # container for obsolete stuff
    def old_stuff():
# -------------------old steamctl code --------------------------------------------OBSOLETE----------------------------------

        # extract ws id from weblink
        def ws_id_from_link(self):
            match = re.compile(r'\d+').search(self.workshop_random_link()).group()
        

        # download multiple tracks from a tracklist
        # replace this with steamcmd
        def ctl_downloader(self, amount):
            trackl = self.multiple_downloader(amount) 
            print(trackl)
            os.chdir(r'steamws')
            for r in range(len(trackl)):
                subprocess.run(r'steamctl --anonymous workshop download {}'.format(trackl[r]))
            os.chdir(Workdirectory)
            
            # filelist = os.listdir('.')
            # print (filelist)

        # move to formatting class in different file?--------V---V---V------------------------------------------------------------------
        # input: Workshop folder
                                                
        # get zeepfile location
        def get_playlist_info(self, cf, zll, lof):
            os.chdir(Workdirectory + "\steamws" + "\\" + cf)
            zeepwsfiles = os.listdir('.')
            zll.append(lof + "\\" + zeepwsfiles[0])

        # filter info from downloaded tracks for creation of playlist
        def get_track_info(self):
            os.chdir(Workdirectory + "\steamws")
            print("cwd: ", os.getcwd())
            listOfFiles = os.listdir('.')
            # print(listOfFiles)
            
            listOfFolders = []

            for x in range(len(listOfFiles)):
                if os.path.isdir(Workdirectory + "\steamws" + "\\" + listOfFiles[x]):
                    current_file = listOfFiles[x]
                    listOfFolders.append(current_file)
                    self.get_playlist_info(current_file, self.zeeplevellist, listOfFiles[x])
                    os.chdir(Workdirectory + "\steamws")
                else:
                    os.chdir(Workdirectory + "\steamws")
            
            # print(self.zeeplevellist)
            return self.zeeplevellist
        
        def get_player_info(self):
        

            for x in range(len(self.get_track_info())):
                # print(Workdirectory + "\steamws" + "\\" + zeeplevellist[x])
                with open(Workdirectory + "\steamws" + "\\" + self.zeeplevellist[x]) as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',')
                    # print(next(spamreader))
                    self.UID_dict["UID_{}".format(x)] = next(spamreader)

                self.UID_list.append((self.UID_dict.get("UID_{}".format(x))[2]))
            
            print(self.UID_list)

classy = WorkshopScraper()
