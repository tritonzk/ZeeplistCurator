import os
import io
import shutil
import subprocess
import re
import json
import requests

import questionary as q
import sqlite3 as sq
from bs4 import BeautifulSoup as bs
import click
#TODO: -(20) Implement click

from urllib import request, parse
from pathlib import PurePath
from glob import glob

# import csv
# from pprint import pprint


#TODO: -(3) install steamcmd if not installed yet or first opening.
#TODO: -(2) function to move downloaded tracks to local tracks folder or delete them
#TODO: -(20) SQL database
#TODO: -(10) split large playlists (find good max amount)
#TODO: -(10) better way to find authors (type their name)
#TODO: -(~) better progress display while downloading and sorting (more information)
#TODO: -(5) loading widget while waiting
#TODO: -(10) fidget and ascii art for menu's
#TODO: -() make a menu form for questionary



#TODO: First todos
#TODO: - questionary console for currently working functions

program_path = os.getcwd()
local_tracks_folder = r"C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670"
        
# NOTE: GTR

# gtr_base: str = "https://api.zeepkist-gtr.com/levels/"
# gtr_opt: list = [
#     "popular",
#     "hot",
#     "points?SortByPoints=true&Ascending=false&Limit={}&Offset=0",
# ]

# NOTE: Zworpshop

# zworpshopGraphHql: str = "https://graphql.zworpshop.com/"
# zworp_base: str = "https://api.zworpshop.com/levels/"
# zworp_opt: dict = {
#     "random": "random?Amount={}",
#     "author": "author/{}?IncludeReplaced=false",
#     "workshop": "workshop/{}?IncludeReplaced=false",
#     "hash": "/hash/{}?IncludeReplaced=false&IncludeDeleted=false",
# }
#

zeeplistFormat = {
    "name": "",
    "amountOfLevels": 0,
    "roundLength": 0,
    "shufflePlaylist": False,
    "UID": [],
    "levels": [],
}

trackFormat = {"UID": "", "WorkshopID": 0, "Name": "", "Author": "", "played": False}

#TODO: is this obsolete?
choicesDict = {
    "amount": 0,
    "functionChoice": "",
    "workshopid": "",
    "authorId": "",
    "pages": 0,
    "steamUserId": "",
    "searchTerm": "",
    "roundlength": 0.0,
    "shuffle": False,
}


class ZeeplistCurator:
    def __init__(self):
        self.start()
        # self.tracklist = {}  # list of tracks to add to playlist
        
        self.playlist_form = [
            {'type': 'text',
             'name': 'playlist_name',
             'message': 'Name of the playlist'},
            {'type': 'text',
             'name': 'playlist_round_length',
             'message': 'Round lenght in seconds'},
            {'type': 'confirm',
             'name': 'playlist_shuffle',
             'message': 'shuffle?'}
        ]

    def start(self):
        self.console()

    def menu(self):
        pass


    def console(self):
        #TODO: make this cleaner and do all functionality
        appdatapath = os.path.expandvars("%Appdata%\\Zeepkist\\Playlists")

        start_screen = """
        Welcome to ZeeplistCurator. Python script written by Triton
        Type 'ZeeplistCurator -h' for help and to learn how to use this as a CLI application.
        
        This project uses Steam page Web-scraping so it should work even if the GTR API is down.
        Once the GTR API is back up I plan to implement functionality for it as well.

        Thanks to Thundernerd for creating GTR and Zworpshop.
        Thanks to Vei/Vulpesx for creating Zeeper and inspiring me to start this project.

        Place this program in your playlist folder at:
        {0}
        """.format(
            appdatapath
        )

        print(start_screen)

        firstchoice = ["Create Playlist", "Manage Playlists", "Options", "Exit"]
        firstmenu = q.select(message="Startmenu", choices=firstchoice).ask()

        #NOTE: main menu
        match firstmenu:
            case "Create Playlist":
                playlist_menu = [
                    "Local Tracks",
                    "Workshop User",
                    "Steam Search",
                    "SteamCMD Downloads"
                    # "Pseudo Random",
                ]

                playlist_query = q.select(
                    message="Create Playlist From:", choices=playlist_menu
                ).ask()

                if playlist_query == "Steam Search" or playlist_query == "Workshop User":
                    link = GenLinks().steam_link_console()

                    match playlist_query:
                        case "Steam Search":
                            idlist = SteamScrape().get_workshop_ids_from_browse_page(link)
                        case "Workshop User":
                            pages = int( q.text(message="how many user pages to download? default is 1 (30 items)", default="1").ask() )
                            idlist = SteamScrape().get_workshop_ids_from_user_page(link, pages)
                    try:
                        SteamScrape().steamCMD_downloader(idlist)
                    except:
                        print("Download did not work. Probably because of an empty list")
                    ZeeplistFormat().zeeplist_constructor()


                elif playlist_query == "Local Tracks":
                    print("not implemented yet")  #TODO:
                    files = ZeeplistFormat().get_dict_from_local_tracks(path="local")


                elif playlist_query == "Playlists":
                    print("not implemented yet")  #TODO:
                elif playlist_query == "SteamCMD Downloads":
                    print("not implemented yet")



            case "Manage Playlists": #TODO:
                manage_menu = [
                    "Combine Playlists", #TODO:
                    "Sort Playlist", #TODO:
                    "Extract from Playlist", #TODO: author, regex, etc.
                ]
            case "Options":
                print("option menu not implemented yet")
                quit()
            case "Exit":
                print("program exiting....")
                quit()


        playlist_info = q.prompt(playlist_form)

        # choicesDict["name"] = q.text(message="name of playlist").ask()
        # choicesDict["roundlength"] = q.text(message="round length in seconds").ask()
        # choicesDict["shuffle"] = q.confirm(message="shuffle?").ask()

        return choicesDict, playlist_info

    def steam_search_console(self, playlist_query):
        match playlist_query:
            case "Workshop User":
                print(
                    """Go to the Steam Workshop. Click on a user workshop profile and enter the ID in the url.
                    it should look like this:\n https://steamcommunity.com/id/___STEAM_ID___/myworkshopfiles/?appid=1440670"""
                )
                choicesDict["steamUserId"].text(message="Enter ID").ask()
                choicesDict["pages"]
            case "Steam Search":
                choicesDict["sorting"] = q.select(
                    message="Search with what sorting method?",
                    choices=[
                        "Relevant",
                        "Recent",
                        "Popular (All Time)",
                    ],
                    use_shortcuts=True,
                ).ask()
                choicesDict["searchTerm"] = q.text(message="Enter search term").ask()

        return link

    def playlist_from_workshop_user(self, usr: str, pages=1):
        """Download tracks and create a playlist from a steam user.
        for pages enter -1 to download all
        """
        steam = SteamScrape
        steam.steamCMD_downloader(
            self=steam(),
            idlist=steam.get_workshop_ids_from_user_page(
                self=steam(),
                user=usr,
                pages=pages,
            ),
        )

        ZeeplistFormat().zeeplist_constructor(
            UIDDict=ZeeplistFormat.get_dict_from_local_tracks(
                ZeeplistFormat(), path="steamcmd"
            ),
            filename="steamsearch",
            roundlength=7200,
            shuffle=True,
        )


class GenLinks:
    def __init__(self) -> None:
        """Class to generate steam, gtr and zworpshop links for Web scraping and API calls"""
        self.baselink = "https://steamcommunity.com/workshop/browse/?appid=1440670"
        self.sort_opt = [
            "textsearch",
            "mostrecent",
            "trend",
            "playtime_trend",
            "lastupdated",
            "totaluniquesubscribers",
        ]

        self.browsesort = "&browsesort={0}&section=readytouseitems&actualsort={0}"
        self.steam_search = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=textsearch&section=readytouseitems"
        self.daylist = [1, 7, 30, 90, 180, 365, -1]

    def check_connection(self) -> None:
        """steam, gtr, zworpshop connection check"""
        #TODO: make this return a list of tuples [(gtr, False), ....]
        connect = {
            "gtr": ("https://api.zeepkist-gtr.com", None),
            "zworpshop": ("https://api.zworpshop.com", None),
            "steam": (self.baselink, None),
        }

        for x in connect.items():
            try:
                request.urlopen(x[1][0])
                print("connected: ", x[0])
            except:
                print("no connection: ", x[1][0])

    def get_workshop_link_from_username(self, user: str, page=1) -> str:
        """return published tracks list from steam username"""
        return "https://steamcommunity.com/id/{0}/myworkshopfiles/?appid=1440670&p={1}&numperpage=30".format(
            user, page
        )

    def steam_link_console(self) -> str:
        """questionary console to generate a steam search workshop link"""
        sortchoice = q.select(
            message="select sorting method",
            choices=[
                "Popular",
                "Playtime",
                "Total Subscribers",
                "Recent",
                "Last Update",
            ],
        ).ask()

        match sortchoice:
            case "Popular":
                sortchoice = "trend"
            case "Playtime":
                sortchoice = "playtime_trend"
            case "Total Subscribers":
                sortchoice = "totaluniquesubscribers"
            case "Recent":
                sortchoice = "mostrecent"
            case "Last Update":
                sortchoice = "lastupdated"

        if sortchoice == "Popular" or "Playtime":
            days = q.select(
                message="In what timeframe?",
                choices=[
                    "All Time",
                    "1 day",
                    "1 week",
                    "1 month",
                    "3 months",
                    "1 year",
                ],
            ).ask()
            match days:
                case "All Time":
                    days = -1
                case "1 day":
                    days = 1
                case "1 week":
                    days = 7
                case "1 month":
                    days = 30
                case "3 months":
                    days = 90
                case "1 year":
                    days = 365
        else:
            days = 0

        searchterm = q.text(
            message="Enter a term to search for (leave empty to search full library)",
            default="",
        ).ask()
        page = int(q.text("What page?").ask())

        return self.steam_link(
            sort=sortchoice, page=page, days=days, searchterm=searchterm
        )

    def steam_link(self, sort: str, page: int, days: int, searchterm: str = "") -> str:
        """return a steam workshop link for the given arguments.
        Use steam_link_console to generate using questionary console.
        sort terms: textsearch, mostrecent, trend, playtime_trend,
        lastupdated, totaluniquesubscribers
        days: 1, 7, 30, 90, 180, 365, -1"""

        if searchterm != "":
            link = (
                self.baselink
                + "&searchtext={}".format(parse.quote(searchterm))
                + self.browsesort.format(sort)
                + "&p={}".format(page)
            )
        else:
            link = self.baselink + self.browsesort.format(sort) + "&p={}".format(page)

        if sort == "playtime_trend" or sort == "trend":
            link = link + "&days={}".format(days)

        return link


# NOTE: Steam
# WARN: order: base + browsesort + section + actualsort + page + day


class SteamScrape:
    def __init__(self) -> None:
        """get data from steam using Steam API, SteamCMD and Webscraping"""

    # NOTE: Utils

    def bsoup(self, link) -> bs:
        """return a bs4 object from given link"""
        return bs(requests.get(link).text, "html.parser")

    def get_max_workshop_page(self, wsLink: str) -> int:
        """return last page number of Steam items page"""
        #TODO: Make this work for User and Workshop pages
        soup = self.bsoup(wsLink)
        pageNumberLinks = soup.find_all("a", class_="pagelink")
        maxPage = bs.get_text(pageNumberLinks[-1])
        return int(maxPage)

    # NOTE: Steam Scraping
    #TODO: Make a function for getting id's from multiple pages for both workshop and user.
    def get_workshop_ids_from_browse_page(
        self,
        link,
    ) -> list[int]:
        """return list of 30 track ids per page from the given browsing page using bs4."""
        idlist = []
        # maxpage = self.get_max_workshop_page(link)

        soup = self.bsoup(link)
        linklist = []
        items_on_page = soup.find_all("a", class_="item_link", href=True)

        for x in items_on_page:
            linklist.append(x.get("href"))
        for y in linklist:
            idlist.append(re.compile(r"\d+").search(y).group())

        print(f"idlist: {idlist}")

        return idlist

    def get_workshop_ids_from_user_page(
        self,
        user,
        pages=1,
    ) -> list[int]:
        """Return 30 tracks per page from the given author page using bs4.
        Enter page-number for multiple pages. enter -1 for all pages"""
        idlist = []
        maxpage = self.get_max_workshop_page(
            GenLinks().get_workshop_link_from_username(user=user)
        )

        if pages == -1:
            pages = maxpage + 1
        elif pages > maxpage:
            print(f"there are only {maxpage} pages")
        else:
            pages += 1

        for x in range(1, pages):
            link = GenLinks().get_workshop_link_from_username(user, x)
            print(f"")
            # print(link)
            soup = self.bsoup(link)
            linklist = []
            items_on_page = soup.find_all("a", class_="ugc", href=True)
            for x in items_on_page:
                linklist.append(x.get("href"))
            for y in linklist:
                idlist.append(re.compile(r"\d+").search(y).group())
        return idlist

    def steamCMD_downloader(self, idlist: list[int]) -> None:
        """download all items from a workshop ID list."""
        #TODO: split the command with better error messaging and info per download

        dlCommand = ""

        for id in idlist:
            dlCommand += " +workshop_download_item 1440670 {0}".format(id)

        print(f"length dlcommand: {len(dlCommand)}")
        local_workshop_path = (
            "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670"
        )

        try:
            subprocess.run(
                "{0}\\SteamCmd\\steamcmd +login anonymous +force_install_dir {1}{2} +quit".format(
                    program_path, local_workshop_path, dlCommand
                ),
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print("an error occured: ", e)

    def download_steam_item(self, workshopid):
        dlCommand = " +workshop_download_item 1440670 {}".format(workshopid)
        subprocess.run(
            "{}\\SteamCmd\\steamcmd +login anonymous{} +quit".format(
                program_path, dlCommand
            )
        )


class ZeeplistFormat:
    def __init__(self):
        """Class for dealing with *.zeeplevel and *.zeeplist formats"""
        self.zeepDict = {}

        self.zeeplistFormat = {
            "name": "",
            "amountOfLevels": 0,
            "roundLength": 0,
            "shufflePlaylist": False,
            "UID": [],
            "levels": [],
        }

        self.trackFormat = {"UID": "", "WorkshopID": 0, "Name": "", "Author": "", "played": False}

        self.choicesDict = {
            "amount": 0,
            "functionChoice": "",
            "workshopid": "",
            "authorId": "",
            "pages": 0,
            "steamUserId": "",
            "searchTerm": "",
            "roundlength": 0.0,
            "shuffle": False,
        }


    def tracklist_formatter(self, authorid:str, workshopid:int, name:str, author:str) -> dict:
        track = self.trackFormat
        track["UID"] = authorid
        track["WorkshopID"] = int( workshopid )
        track["Name"] = name
        track["Author"] = author
        track["played"] = False
        return track

    def zeeplist_constructor(self, UIDDict:dict, filename:str, roundlength:float, shuffle:bool):
        self.zeepDict.clear()

        for x in UIDDict.items():
            self.zeepDict = self.zeeplistFormat
            trackFormat = {
                "UID": str(x[1]["authorid"]),
                "WorkshopID": int(x[1]["workshopid"]),
                "Name": str(x[1]["name"]),
                "Author": str(x[1]["author"]),
                "played": False,
            }
            levelList = self.zeepDict["levels"]
            levelList.append(trackFormat)
            self.zeepDict["levels"] = levelList
            self.zeepDict["name"] = filename

        self.zeepDict["amountOfLevels"] = len(UIDDict)
        self.zeepDict["roundLength"] = float(roundlength)
        self.zeepDict["shufflePlaylist"] = shuffle

        os.chdir(program_path)
        with io.open(
            filename + ".zeeplist", "w", encoding="utf-8-sig", newline=""
        ) as playlistFile:
            json.dump(self.zeepDict, playlistFile, indent=4, ensure_ascii=False)

    def get_dict_from_local_tracks(self, path: str, custom=""):
        """create dictionary with Workshop ID, Author and UID extracted from zeepfiles
        path vars: 'steamcmd', 'local', 'custom'. If custom enter a custom path."""
        workshop_path = (
            program_path + "\\SteamCmd\\steamapps\\workshop\\content\\1440670\\"
        )
        zeeplevelfile_path = {}
        uid_dict = {}

        match path:
            case "steamcmd":
                workshop_path = (
                    program_path + "\\SteamCmd\\steamapps\\workshop\\content\\1440670\\"
                )
            case "local":
                workshop_path = "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670\\"
            case "custom":
                workshop_path = custom

        #TODO: learn glob. This is so much faster and easy.
        zeeplevels = [
            y
            for x in os.walk(workshop_path)
            for y in glob(os.path.join(x[0], "*.zeeplevel"))
        ]

        #TODO: seperate lists so they don't get too large
        for x in range(len(zeeplevels)):
            workshop_item = PurePath(zeeplevels[x]).parts[-3]
            fullpath = zeeplevels[x]
            zeeplevelfile_path[workshop_item] = fullpath

        print("\n--------------------- Path finding done --------------------------\n")

        #NOTE: extract UID and Author from zeeplevel files to uid_dict
        #TODO: change this to be to trackformat
        for x in zeeplevelfile_path.keys():
            print("keys: ", x)
            items = []
            with io.open(
                zeeplevelfile_path[x], "r", encoding="utf-8-sig"
            ) as zeeplevel_file_open:
                items = zeeplevel_file_open.readline().split(",")
                try:
                    print(f"items: {items}")
                except:
                    print("couldn't print line")

            name = os.path.split(zeeplevelfile_path[x])[1].split(".")[0]
            uid_dict[x + " " + name] = {
                "workshopid": x,
                "name": name,
                "author": items[1],
                "authorid": items[2][:-1],
            }

        for x in uid_dict.items():
            print(x)

        # print("\nfile_path", zeeplevelfile_path)
        # print("\n___UID dict: ", uid_dict)
        # print("\n___Workshop Id's: ", items, "\n")
        return uid_dict

    # NOTE: ------------------- Helper scripts -------------------------------

    def put_uid_dict_in_db(self, UID: dict[str, dict[str, str]]):
        #NOTE: still a WIP
        con = sq.connect(program_path + "\\data.db")
        cur = con.cursor()

        tracks = []

        for x in UID.items():
            data = x[1]
            tracks.append(
                (
                    data["authorid"],
                    data["workshopid"],
                    data["name"],
                    data["author"],
                    "0",
                )
            )
            print(f"track: {tracks}")

        cur.executemany("INSERT OR IGNORE INTO tracks VALUES(?,?,?,?,?)", tracks)
        con.commit()

        # res = cur.execute("SELECT * FROM track")
        # print(res.fetchall())

    def get_dict_from_zeeplist(self, file: str) -> dict:
        #NOTE: not a UIDdict format but a raw json
        with io.open(file, "r", encoding="utf-8-sig", newline="") as file_open:
            json_data = json.load(file_open)
        uiddict = {}
        return json_data

    def move_playlist_to_local(self, file: str) -> None:
        shutil.copy(
            file,
            os.path.expandvars("%AppData%\\Zeepkist\\Playlists"),
        )

    def get_track_amount_from_playlist(self):
        pass




if __name__ == "__main__":
    m = ZeeplistCurator()
    # m.start()
    m.menu()
