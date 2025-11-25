import io
import json
import os
import sqlite3 as sql
import subprocess
import sys
from ast import literal_eval
from collections import namedtuple
from datetime import datetime
from io import open
from pathlib import Path, PurePath
from pprint import pprint
from urllib import parse, request

# import click  # TODO: maybe use this? Able to run the app with "app --example" tags in terminal
# import consolemenu  # this is a UI library for menus in terminal #TODO: use this for playlist browsing
import questionary as q
import regex as re
import requests
from bs4 import BeautifulSoup as bs

# NOTE: system info
ENVIRONMENT = os.name
PROGRAM_PATH = os.getcwd()
first_start = True

HOME_FOLDER = Path.home().as_posix()
# print(f"home folder: {HOME_FOLDER}")

if ENVIRONMENT == "posix":  # linux
    ZEEPKIST_APPDATA_FOLDER = (
        HOME_FOLDER
        + "/.steam/steam/steamapps/compatdata/1440670/pfx/drive_c/users/steamuser/Application Data/Zeepkist"
    )
    STEAM_WORKSHOP_FOLDER = (
        HOME_FOLDER + "/.local/share/Steam/steamapps/workshop/content/1440670/"
    )
elif ENVIRONMENT == "nt":  # windows #TODO: test on windows
    ZEEPKIST_APPDATA_FOLDER = os.path.expandvars("%Appdata%\\Zeepkist")
    STEAM_WORKSHOP_FOLDER = (
        r"C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670"
    )
else:
    q.press_any_key_to_continue("environment unknown. quitting").ask()
    sys.exit(0)


# pprint(f"appdata folder: {ZEEPKIST_APPDATA_FOLDER}")
# pprint(f"workshop folder: {STEAM_WORKSHOP_FOLDER}")

# NOTE: Formats
ZEEPLEVEL_FORMAT = {
    "jsonVersion": 3,
    "level": {"name": "", "UID": "", "zeepHash": ""},
    "author": {
        "name": "",
        "StmID": "",
        "collaborators": "",
        "nameOverride": "",
    },
    "medals": {
        "isLegit": True,
        "author": 0,
        "gold": 0,
        "silver": 0,
        "bronze": 0,
    },
}
ZEEPLIST_FORMAT = {
    "name": "",
    "amountOfLevels": "",
    "roundLength": 480,
    "shufflePlaylist": False,
    "UID": [],
    "levels": [],
}

ZEEPLIST_LEVEL_FORMAT = {
    "UID": "",
    "WorkshopID": 0,
    "Name": "",
    "Collaborators": "",
    "OverrideAuthorName": "",
    "Author": "",
    "played": None,
}


# NOTE: configuration
CONFIG_FILE = "config.json"
CONFIG_FORMAT = {
    "playlist_defaults": {
        "time": 480.0,
        "shuffle": False,
        "default_sort": "date_modified",
        "sort_direction": "DESC",
    },
    "steam_scraper": {"max_page": 5},
    "update_db": False,
    "update_verbose": True,
    "custom_appdata_folder": "",
    "custom_workshop_folder": "",
    "first_db_update": True,
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump(CONFIG_FORMAT, f, indent=4)
        q.print("no config file found, creating a new one.")

with open(CONFIG_FILE) as f:
    CONFIG_DATA = json.loads(f.read())


# NOTE: connection checker
def check_connection() -> list[tuple]:
    """steam, gtr, zworpshop connection check"""
    connect = {
        "gtr": ("https://api.zeepkist-gtr.com", None),
        "zworpshop": ("https://api.zworpshop.com", None),
        "steam": ("https://steamcommunity.com/workshop/browse/?appid=1440670", None),
    }
    connect_status = []
    for x in connect.items():
        try:
            request.urlopen(x[1][0])
            connect_status += (x[0], True)
            # print("connected: ", x[0])
        except:
            connect_status += (x[0], False)
            # print("no connection: ", x[1][0])
    return connect_status


# check_connection()


# NOTE: --------------------------------------------START OF THE PROGRAM----------------------------------------


class ConfigManager:
    def __init__(self):
        with io.open(CONFIG_FILE, "r") as f:
            self.config = json.loads(f.read())

        self.custom_folder_paths()

    def custom_folder_paths(self):
        changed = False
        if not os.path.exists(ZEEPKIST_APPDATA_FOLDER):
            q.print("-" * 50, style="fg:ansired")
            q.print("error: could not find your appdata Zeepkist folder.")
            q.print(
                "find where your playlists and level-editor levels are stored and enter 'Zeepkist' folder below"
            )
            self.change("custom_appdata_folder", q.text("enter path: ").ask())

        if not os.path.exists(STEAM_WORKSHOP_FOLDER):
            q.print("-" * 50, style="fg:ansired")
            q.print("error: could not find your Steam's Zeepkist Workshop folder")
            q.print(
                "find where your locally downloaded tracks are stored and enter the '1440670' folder below"
            )
            self.change("custom_workshop_folder", q.text("enter path: ").ask())

        if changed:
            if q.confirm("config changed. restart now? ").ask():
                sys.exit(0)

    def change(self, input: str, change_to):
        self.config[input] = change_to
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def reset_config(self):
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG_FORMAT, f, indent=4)

    def change_playlist_defaults(self):
        shuffle_choice = q.confirm("Shuffle? ").ask()
        time_choice = q.text("Roundlength ").ask()
        self.config["playlist_defaults"]["time"] = time_choice
        self.config["playlist_defaults"]["shuffle"] = shuffle_choice
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def change_update_verbose(self):
        verbose = q.confirm("Show every track and playlist when updating? ").ask()
        if verbose:
            self.change("update_verbose", True)
        else:
            self.change("update_verbose", False)
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def change_steam_max_page(self):
        max_page = q.text("Change max page to search with steam").ask()
        self.config["steam_scraper"]["max_page"] = max_page
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)


# NOTE: run the configmanager once to catch if anything is missing
ConfigManager()


class LocalDB:
    def __init__(self) -> None:
        self.con = sql.connect("data.db")
        self.cur = self.con.cursor()

        # NOTE: create level table if none exists
        self.cur.execute(
            """
        CREATE TABLE IF NOT EXISTS levels (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE,
        workshop_id TEXT,
        workshop_name TEXT,
        workshop_author TEXT,
        track_author TEXT,
        track_author_stmid TEXT,
        track_collaborators TEXT,
        track_name TEXT,
        track_data TEXT,
        date_modified TEXT,
        sys_date_modified TEXT
        )
        """
        )

        # NOTE: create playlists table if none exists
        self.cur.execute(
            """
        CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE,
        name TEXT,
        levels TEXT,
        data TEXT,
        level_amount INT
        )
        """
        )

        global first_start
        if CONFIG_DATA["update_db"] and first_start:
            self.update_zeeplist_table()
            self.update_level_table()
            first_start = False

    def namedtuple_factory(self, cursor, row):
        """helper script to set up rows"""
        fields = [col[0] for col in cursor.description]
        Row = namedtuple("Row", fields)
        return Row(*row)

    def query_data_name(self, name: str):
        """get a list of tracks with a regex name"""
        self.con.row_factory = self.namedtuple_factory
        name_tracks = self.con.execute(
            "SELECT * FROM levels WHERE LOWER(track_name) LIKE '%' || LOWER(?) || '%' ORDER BY date_modified DESC",
            (name,),
        ).fetchall()
        return [name_tracks]

    def query_data_workshopid(self, idlist: list[int]) -> list[list]:
        """get a list of ids from the database and put the data for them in a playlist"""
        self.con.row_factory = self.namedtuple_factory
        workshop_list = []
        for id in idlist:
            workshop_list.append(
                self.con.execute(
                    """
                    SELECT * FROM levels WHERE workshop_id = ? ORDER BY date_modified DESC
                """,
                    (id,),
                ).fetchall()
            )
        return workshop_list

    def query_data_author(self, author) -> list[list]:
        """get a list of tracks from an author (based on string)"""
        self.con.row_factory = self.namedtuple_factory
        author_list = self.con.execute(
            "SELECT * FROM levels WHERE LOWER(track_author) LIKE '%' || LOWER(?) || '%' ORDER BY date_modified DESC",
            (author,),
        ).fetchall()
        return [author_list]

    def query_data_author_fuzzy(self, author) -> list[list]:
        """get a list of tracks from an author, case-insensitive, check collaboration, overwritten, author steamids.
        - check most common steam id related to author (track_author > workshop_author > collaborator)
        - once a steam id is related do another search for that steamid
        i want this one to collect all tracks the author has worked on.
        - integrate with steamcmd / steamscraper to download missing tracks from this author (get steamid first and then scrape)
        """
        self.con.row_factory = self.namedtuple_factory
        results = self.con.execute(
            """
            SELECT *
            FROM levels
            WHERE LOWER(track_author) LIKE '%' || LOWER(?) || '%'
               OR LOWER(track_collaborators) LIKE '%' || LOWER(?) || '%'
            ORDER BY date_modified DESC
        """,
            (author, author),
        ).fetchall()

        return [results]

    def query_data_fuzzy(self, author):
        """get a list of tracks based on a searchterm, could be author, trackname, case-insensitive, overwritten names, collaborators"""
        pass

    def query_data_recent_search(self):
        """get a list of recently modified tracks (aka recently downloaded)"""
        pass

    def update_zeeplist_table(self):
        playlists = list(
            Path(ZEEPKIST_APPDATA_FOLDER + "/Playlists").rglob("*.zeeplist")
        )
        # pprint(playlists)

        for x in playlists:
            plist = ZeeplistFormat(x.as_posix())
            if CONFIG_DATA["update_verbose"]:
                print(
                    f"[{plist.format}] : "
                    + plist.playlist.parent.name
                    + "/"
                    + plist.name
                )
            data = plist.data.copy()
            data.pop("levels")

            try:
                self.con.execute(
                    """INSERT OR REPLACE INTO playlists ( path, name, levels, data, level_amount ) values ( ?, ?, ?, ?, ?) """,
                    (
                        x.as_uri(),
                        plist.name,
                        str(plist.levels),
                        str(data),
                        plist.amount,
                    ),
                )
            except sql.IntegrityError:
                print(f"sql_integrity_error on {x}")
                pass

        self.con.commit()

    def update_level_table(self):
        tracks = list(Path(STEAM_WORKSHOP_FOLDER).rglob("*.zeeplevel"))

        for x in tracks:
            f = json.loads(open(x.parent.parent.as_posix() + "/metadata.json").read())
            if CONFIG_DATA["update_verbose"]:
                print(
                    "updating: {track}".format(
                        track=x.parts[-3] + x.parts[-2] + x.parts[-1]
                    )
                )
            datemodified = datetime(
                year=f["lastUpdatedYear"],
                month=f["lastUpdatedMonth"],
                day=f["lastUpdatedDay"],
                hour=f["lastUpdatedHour"],
                minute=f["lastUpdatedMinute"],
                second=f["lastUpdatedSecond"],
            )
            workshop_author = f["author"]
            sys_last_modified = os.path.getmtime(x)

            track = ZeeptrackFormat(x.as_posix())
            track_data = {}
            if track.version == 2:
                track_data = track.get_level_data_v2()
            elif track.version == 3:
                track_data = track.get_level_data_v3()
            else:
                print(track.version)
                print(f"track V{track.version}: there was an error with track {x}")
                print(open(x, "rb").read(200))
                print("track data :")
                print(track_data)

            try:
                self.con.execute(
                    """INSERT OR REPLACE INTO levels ( path, workshop_id, workshop_name, workshop_author, track_author, track_author_stmid, track_collaborators, track_name, track_data, date_modified, sys_date_modified ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                    (
                        x.as_uri(),
                        PurePath(x).parts[-3],
                        "N/A",
                        workshop_author,
                        track_data["author"]["name"],
                        track_data["author"]["StmID"],
                        track_data["author"]["collaborators"],
                        PurePath(x).parts[-2],
                        str(track_data),
                        str(datemodified),
                        sys_last_modified,
                    ),
                )
            except sql.IntegrityError:
                print(f"sql_integrity_error on {x}")
                pass

        self.con.commit()


# NOTE: run localdb once for making the tables and updating the database if "update_db" is set in config
LocalDB()


class PlaylistManager:
    def __init__(self) -> None:
        """class to manage playlist files. create, manage, change zeeplists"""
        self.con = LocalDB().con

    def merge_playlists(self, p1, p2):  # TODO:
        """merge two playlists, search playlists twice, set time or choose default time, set shuffle or default"""
        pass

    def format_playlistdict_from_levels(self, datalist) -> dict:
        """put list of items from data.db queries into zeeplist format
        takes data in Row format and outputs playlist dict"""

        levels = []
        for i, wsitem in enumerate(datalist):  # each workshop nr has their own list
            for x in range(0, len(wsitem)):  # for each level in a workshop item
                level = ZEEPLIST_LEVEL_FORMAT.copy()
                level_row = wsitem[x]
                track_data = literal_eval(
                    level_row.track_data
                )  # WARNING: this could run code if the database is changed. find some other way to do str -> dict
                level["UID"] = track_data["level"]["UID"]
                level["WorkshopID"] = int(level_row.workshop_id)
                level["Name"] = level_row.track_name
                level["Collaborators"] = level_row.track_collaborators
                level["OverrideAuthorName"] = track_data["author"]["nameOverride"]
                level["Author"] = level_row.track_author
                level["played"] = False
                levels.append(level)
                # print("added {track}".format(track=level["Name"]))
        pl = ZEEPLIST_FORMAT.copy()
        pl["amountOfLevels"] = len(levels)
        pl["levels"] = levels

        q.print(
            ("-" * 20)
            + " {} tracks found ".format(pl["amountOfLevels"])
            + ("-" * (30 - len(" {} tracks found "))),
            style="fg:ansired",
        )
        readable_level_list = []
        for level in levels:
            readable_level_list.append(level["Author"] + " - " + level["Name"])
        print(readable_level_list)
        q.print(("-" * 50), style="fg:ansired")

        return pl

    def create_and_copy_playlist(
        self,
        name: str,
        pldict: dict,
        shuffle: bool = CONFIG_DATA["playlist_defaults"]["shuffle"],
        time: float = CONFIG_DATA["playlist_defaults"]["time"],
    ):
        """write zeeplist formatted dict into a file and copy to config zeeplist_storage"""
        pldict["name"] = name
        pldict["time"] = time
        pldict["shuffle"] = shuffle

        if name == "":
            name = q.text("name your track: ").ask()

        new_list = open("{name}.zeeplist".format(name=name), "w", encoding="utf-8-sig")
        json.dump(pldict, new_list, indent=4)
        new_list.close()

        safe = ZEEPKIST_APPDATA_FOLDER.replace(" ", r"\ ")
        subprocess.run(
            "cp {cwd}/{name}.zeeplist {zlstorage}".format(
                cwd=PROGRAM_PATH, name=name, zlstorage=safe + r"/Playlists/"
            ),
            shell=True,
        )
        print()
        q.print(
            text="""created playlist {name}.zeeplist with {levels_amount} items""".format(
                name=name, levels_amount=pldict["amountOfLevels"]
            ),
            style="bold",
        )


class SteamScraper:
    def __init__(self) -> None:
        """minimum: search for a term and return a list of workshop ids
        full: filtered searching, author and search extraction, reading of popular etc.
        this class does webscraping on the zeepkist workshop. also uses steamcmd if needed.
        possible future steamapi usage but I want to reserve that for advanced stuff, it requires a key.
        """
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
        self.daylist = [1, 7, 30, 90, 180, 365, -1]  # not used
        self.author_link = (
            "https://steamcommunity.com/id/{0}/myworkshopfiles/?numperpage=30"
        )

    def start(self) -> list[int]:
        return self.get_workshop_ids_from_browse_page(self.steam_link_console())

    def bsoup(self, link) -> bs:
        """return a bs4 object from given link"""
        return bs(requests.get(link).text, "html.parser")

    def get_workshop_ids_from_author_id(self, id):
        link = self.author_link.format(id)
        try:
            request.urlopen(link)
        except:
            print(f"link: {link} does not exist")
            return [0]
        idlist = []
        max_page = int(self.get_max_page(link))
        max_page_config = int(CONFIG_DATA["steam_scraper"]["max_page"])
        for x in range(0, max_page if max_page <= max_page_config else max_page_config):
            link += f"&p={x+1}"
            soup = self.bsoup(link)
            items_on_page = soup.find_all("a", class_="ugc", href=True)
            idlist.extend([i.get("data-publishedfileid") for i in items_on_page])
        return idlist

    def get_workshop_ids_from_browse_page(
        self,
        link,
    ) -> list[int]:
        """return list of 30 workshop ids per page from the given browsing page using bs4."""
        # TODO: be able choose a limit lower than 30
        idlist = []
        max_page = int(self.get_max_page(link))
        max_page_config = int(CONFIG_DATA["steam_scraper"]["max_page"])
        for x in range(0, max_page if max_page <= max_page_config else max_page_config):
            link += f"&p={x+1}"
            soup = self.bsoup(link)
            items_on_page = soup.find_all("a", class_="item_link", href=True)
            linklist = []
            for i in items_on_page:
                linklist.append(i.get("href"))
            for y in linklist:
                idlist.append(
                    re.compile(r"\d+").search(y).group()
                )  # BUG: str|None breaks this sometimes.

        # print(f"idlist:\n {idlist}\n")
        return idlist

    def get_max_page(self, link):
        soup = self.bsoup(link)
        pages = soup.find("div", class_="workshopBrowsePagingControls")
        pages_links = pages.find_all("a", class_="pagelink")
        pages_tags = []
        for x in pages_links:
            pages_tags.append(x.get_text())
        if len(pages_tags) == 0:
            return 1
        return pages_tags[-1]

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
            use_shortcuts=True,
            instruction="use j/k, arrow keys or numbers to navigate",
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
                use_shortcuts=True,
                instruction="use j/k, arrow keys or numbers to navigate",
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
        # upto_page = int(q.text("how many pages").ask())

        if searchterm != "":
            link = (
                self.baselink
                + "&searchtext={}".format(parse.quote(searchterm))
                + self.browsesort.format(sortchoice)
                # + "&p={}".format(page)
            )
        else:
            link = self.baselink + self.browsesort.format(
                sortchoice
            )  # + "&p={}".format(page)

        if sortchoice == "playtime_trend" or sortchoice == "trend":
            link = link + "&days={}".format(days)

        return link


class SteamCMDManager:
    def __init__(self, install_dir: str | None) -> None:
        """manager for steamcmd. downloading workshop items"""
        if install_dir == None:
            self.force_install_dir = STEAM_WORKSHOP_FOLDER
        else:
            self.force_install_dir = install_dir

        self.login = "anonymous"
        self.steamcmd_path = "steamcmd"
        if ENVIRONMENT == "nt":
            # TODO: auto download steamcmd. set steamcmd_path
            pass

    def dl_workshoplist_to_folder(self, idlist: list[int]):
        dlCommand = ""
        if len(idlist) == 0:
            q.print("the workshop list is empty.")
            return False
        else:

            # NOTE: filter out local tracks
            filtered_idlist = []
            removed = []
            for x in idlist:
                workshop_query = LocalDB().query_data_workshopid([x])
                if workshop_query == [
                    []
                ]:  # NOTE: if query returns nothing add to filtered
                    filtered_idlist.append(x)
                elif (
                    len(workshop_query[0]) > 0
                ):  # if query returns row objects [[Row(), Row()]] add to removed
                    removed.append(x)
                else:
                    q.print(f"problem with dl workshoplist item {x}")

            q.print("-" * 50, style="fg:ansired")
            q.print(
                f"found {len(idlist)} tracks, removed {len(removed)} local tracks. Leaving {len(filtered_idlist)} to download"
            )
            q.print("removed: ", style="bold")
            print(removed)
            q.print("downloading: ", style="bold")
            print(filtered_idlist)
            q.print("-" * 50, style="fg:ansired")
            q.print(
                f"with an estimated download time of 3s per track your download time will be {len(filtered_idlist)*3} seconds"
            )
            q.print(
                "keep in mind that workshop items can have multiple tracks, this will increase the download time"
            )
            go_download = q.confirm("Continue downloading? ").ask()
            if not go_download:
                return False

            for id in filtered_idlist:
                dlCommand += "+workshop_download_item 1440670 {0} ".format(id)

            try:
                subprocess.run(
                    "{stm} +force_install_dir {dir} +login anonymous {cmd}+quit".format(
                        stm=self.steamcmd_path,
                        dir=self.force_install_dir,
                        cmd=dlCommand,
                    ),
                    check=True,
                    shell=True,
                )
                q.print("steam download completed.", style="bold")
                print(filtered_idlist)
                return True

            except subprocess.CalledProcessError as e:
                print("an error occured: ", e)

            return True


class ZeeptrackFormat:
    def __init__(self, track):
        """check for zeeplevel format v2 or v3 and get the data from them"""
        self.track: str = str(track)
        self.items_v2: list = []
        self.medals_v2: list = []
        self.items_v3: dict = {}
        self.version: int = 0
        self.format: str = ""
        self.data: dict = ZEEPLEVEL_FORMAT.copy()

        self.extract_data()
        # to_save = ["jsonVersion", "level", "author", "medals"]
        # print(f"medals: { self.medals_v2 }")

    def get_level_data_v3(self):
        for key, value in self.data.items():
            self.data[key] = self.items_v3.get(key)
        return self.data

    def get_level_data_v2(self):
        self.data["jsonVersion"] = 2
        self.data["level"]["UID"] = self.items_v2[2][:-1]
        self.data["author"]["name"] = self.items_v2[1]
        self.data["author"]["StmID"] = ""
        self.data["author"]["collaborators"] = ""
        self.data["medals"]["author"] = self.medals_v2[0]
        self.data["medals"]["gold"] = self.medals_v2[1]
        self.data["medals"]["silver"] = self.medals_v2[2]
        self.data["medals"]["bronze"] = self.medals_v2[3]
        return self.data

    def extract_data(self):
        """check for encoding and zeeplevel version and extract data."""
        six_bytes_sig = io.open(self.track, "rb").read(4)
        if six_bytes_sig[:3] == b"\xef\xbb\xbf":
            if six_bytes_sig == b"\xef\xbb\xbf\x4c":  # BOM leveleditor2
                self.items_v2 = (
                    io.open(self.track, "r", encoding="utf-8-sig").readline().split(",")
                )
                with io.open(self.track, "r", encoding="utf-8-sig") as f:
                    content = "".join(next(f) for _ in range(3))
                self.medals_v2 = content.split("\n")[-2].split(",")[:4]
                self.version = 2
                self.format = "utf-8-sig"
            elif six_bytes_sig == b"\xef\xbb\xbf\x7b":  # BOM json v3
                self.items_v3 = json.loads(
                    io.open(self.track, "r", encoding="utf-8-sig").read()
                )
                self.version = 3
                self.format = "utf-8-sig"
        elif six_bytes_sig.startswith(b"L"):  # leveleditor 2 without BOM
            self.items_v2 = open(self.track, "r").readline().split(",")
            with open(self.track, "r") as f:
                content = "".join(next(f) for _ in range(3))
            self.medals_v2 = content.split("\n")[-2].split(",")[:4]
            self.version = 2
            self.format = "utf-8"
        elif six_bytes_sig.startswith(b"\x7b"):  # json v3 without BOM byte code for {
            self.items_v3 = json.loads(open(self.track, "r").read())
            self.version = 3
            self.format = "utf-8"

        # NOTE: dict version 3?
        else:
            print(six_bytes_sig[0])
            print(
                "error with zeeptrackformat class on {track}".format(track=self.track)
            )
            self.version = 0
            self.items_v2 = []
            self.items_v3 = {}


class ZeeplistFormat:
    def __init__(self, plist) -> None:
        self.playlist = Path(plist)
        self.name: str
        self.amount: int
        self.round_length: float
        self.shuffle: bool
        self.uid: list = []
        self.levels: list[dict | None] = []
        self.data: dict
        self.format: str

        self.extract_data()

    def extract_data(self):
        with open(self.playlist, "rb") as f:
            start_bytes = f.read(3)
        if start_bytes.startswith(b"\xef\xbb\xbf"):  # BOM UTF-sig
            self.format = "utf-sig"
            # print(f"bom : {self.playlist.parent.name}/{self.playlist.name}")
            pl = json.loads(io.open(self.playlist, "r", encoding="utf-8-sig").read())
        elif start_bytes.startswith(b"\x7b"):  # non BOM { in bytes
            self.format = "utf"
            # print(f"non bom: {self.playlist.parent.name}/{self.playlist.name}")
            pl = json.loads(open(self.playlist).read())
        else:
            pl = {}
            q.print("-" * 50, style="fg:ansired")
            print(f"problem with loading playlist: ")
            pprint(self.playlist.parent.name + "/" + self.playlist.name)
            print(f"500 bytes ->\n{io.open(self.playlist, 'rb').read(500)}")
            q.print("-" * 50, style="fg:ansired")

        if pl:
            self.levels = pl["levels"]
            self.uid = pl["UID"] if "UID" in pl else []
            self.shuffle = pl["shufflePlaylist"]
            self.round_length = pl["roundLength"]
            self.amount = pl["amountOfLevels"]
            playlist_name = Path(self.playlist).parts[-1]
            self.name = playlist_name
            self.data = pl


class Console:
    def __init__(self) -> None:
        """CLI console class to manage the program"""
        self.db = LocalDB()
        self.pl = PlaylistManager()
        self.cm = ConfigManager()
        self.first_start = True

        if CONFIG_DATA["first_db_update"]:
            self.db.update_level_table()
            self.db.update_zeeplist_table()
            self.cm.change("first_db_update", False)

    def start(self):
        if self.first_start:
            start_screen = """
            Welcome to ZeeplistCurator. Python script written by Triton (@triton_nl)
            Your playlist folder is at: {0}

            """.format(
                ZEEPKIST_APPDATA_FOLDER + "/Playlists"
            )
            q.print(start_screen)
            self.first_start = False

        # NOTE: Main choices dictionairy
        # NOTE: 1 = command, 0 = exit
        menu_dict = {
            "Create Playlist": {
                "[local] Name": 1,
                "[local] Author (fuzzy)": 1,
                "[local] Author (strict)": 1,
                "[steam] Search": 1,
                "[steam] Author ID": 1,
                "[steam] Workshop ID": 1,
                "Back": 0,
            },
            "Playlist Manager": {
                # "Combine Playlists": 1,
                # "Filter/Split Playlists": 1,
                # "Sort Levels in Playlist": 1,
                # "Extract from Playlist": 1,  # NOTE: ?
                # "Delete playlists": 1,
                "Back": 0,
            },
            "Database Manager": {
                "Refresh Database": 1,
                "Back": 0,
            },
            "Options": {
                # "Edit config file": 1,
                "Change Playlist Defaults": 1,
                "Change Verbose Database Update": 1,
                "Change Steam Max Page": 1,
                "Back": 0,
            },
            "About": {
                "about_text": """

                This program is created by Triton (@triton_nl on discord)

        Github page: https://github.com/tritonzk/ZeeplistCurator

        Zeeplist Curator creates a database called 'data.db' where data from your local tracks and playlists is stored.
        With some clever SQL queries you can easily create new playlists and manipulate your current ones.

        If there are some specific queries you want you can suggest them to me via discord or github
        and if you have some Python/sqlite3 experience or are willing to learn, I welcome any contributors.

        Steam search will search the workshop and download any missing tracks. This may take a long time if the
        search finds a lot of results. You can change the max amount of pages (30 items per page) to check in the Option menu.
        The default is 5.

        You can also simply go to the workshop, download the ones you want, update the database using the [local] method.

        -----------------------FUTURE UPDATE PLANS----------------------------------
        I am working on a future graphics update with many more features.
        The graphics update will have a visual track browser with thumbnails for local levels.

        planned functions:
        - magic queries (combine filters, better queries)
        - tracking played tracks
        - playlistmanager (open playlistmanager menu to see planned functions)
        - rating tracks, adding tags and adding notes
        - tracking GTR times

        More info in the database will make more interesting queries possible.
        - flying/offroad/etc. gate exists in level
        - amount of gtr records
        - amount of blocks
        - has custom or certain skybox
        - has no boosters
        - etc.

        Mixing and matching these filters will make it possible to create many different playlists.
        Keep in mind that most info (especially block and level info) can only be found in locally stored levels.
        First you have to download tracks and update the database.


        -------------------------THANKS----------------------------------------
        Thanks to Thundernerd for creating GTR and Zworpshop and so much more.
        Thanks to Vei/Vulpesx for creating Zeeper which inspired me to start this project.
        """
            },
            "Exit": 0,
        }

        # TODO: setup a style for the menus
        menu_style_curator = q.Style(
            [
                ("", ""),
                ("", ""),
                ("", ""),
                ("", ""),
                ("", ""),
                ("", ""),
                ("", ""),
            ]
        )

        firstmenu = q.select(
            message="welcome to ZeeplistCurator. ",
            choices=[name for name, opc in menu_dict.items()],
            use_shortcuts=True,
            instruction="use j/k, arrow keys or numbers to navigate",
        ).ask()

        match firstmenu:
            case "Create Playlist":
                playlist_choice = q.select(
                    message="Create a Playlist",
                    choices=[
                        name for name, opc in menu_dict["Create Playlist"].items()
                    ],
                    use_shortcuts=True,
                    instruction="use j/k, arrow keys or numbers to navigate",
                ).ask()
                match playlist_choice:
                    case "[local] Name":
                        name_query = q.text(message="Search by name: ").ask()
                        formatted_name_search = self.pl.format_playlistdict_from_levels(
                            self.db.query_data_name(name_query)
                        )

                        print(
                            f"found: {formatted_name_search["amountOfLevels"]} tracks"
                        )
                        if q.confirm("continue to create playlist? ").ask():
                            self.pl.create_and_copy_playlist("", formatted_name_search)
                            q.press_any_key_to_continue().ask()
                            self.start()
                        else:
                            q.print("---- quit out of menu ----")
                            self.start()
                    case "[local] Author (fuzzy)":
                        author_query = q.text(
                            message="Search by author (fuzzy): "
                        ).ask()
                        formatted_fuzzy = self.pl.format_playlistdict_from_levels(
                            self.db.query_data_author_fuzzy(author_query)
                        )

                        q.print(
                            "found: {0} tracks".format(
                                formatted_fuzzy["amountOfLevels"]
                            )
                        )
                        if q.confirm("continue to create playlist? ").ask():
                            self.pl.create_and_copy_playlist("", formatted_fuzzy)
                            q.press_any_key_to_continue().ask()
                            self.start()
                        else:
                            q.print("---- quit out of menu ----")
                            self.start()
                    case "[local] Author (strict)":
                        author_query = q.text(
                            message="Search by author (strict): "
                        ).ask()
                        author_search = self.db.query_data_author(author_query)
                        formatted_author = self.pl.format_playlistdict_from_levels(
                            author_search
                        )
                        print(f"found: {formatted_author["amountOfLevels"]} tracks")
                        confirm_create = q.confirm(
                            "continue to create playlist? "
                        ).ask()
                        if confirm_create:
                            self.pl.create_and_copy_playlist("", formatted_author)
                            q.press_any_key_to_continue().ask()
                            self.start()
                        else:
                            q.print("---- quit out of menu ----")
                            self.start()
                    case "[steam] Search":
                        ss = SteamScraper()
                        cmd = SteamCMDManager(STEAM_WORKSHOP_FOLDER)

                        steam_search_ids = ss.get_workshop_ids_from_browse_page(
                            ss.steam_link_console()
                        )
                        workshop_dl = cmd.dl_workshoplist_to_folder(steam_search_ids)
                        if workshop_dl == False:
                            q.print("---- quit out of menu ----")
                            self.start()

                        self.db.update_level_table()

                        continue_to_create_playlist = q.confirm(
                            "Tracks downloaded. Create playlist from tracks?"
                        ).ask()
                        if continue_to_create_playlist:
                            formatted_workshop_id = (
                                self.pl.format_playlistdict_from_levels(
                                    self.db.query_data_workshopid(steam_search_ids)
                                )
                            )
                            self.pl.create_and_copy_playlist("", formatted_workshop_id)
                            q.press_any_key_to_continue().ask()
                            self.start()
                        else:
                            self.start()
                    case "[steam] Author ID":  # TODO: download from author id
                        ss = SteamScraper()
                        cmd = SteamCMDManager(STEAM_WORKSHOP_FOLDER)
                        workshop_download = True
                        q.print(
                            "go to an authors workshop page on steam or in a browser. the URL should look like this:"
                        )
                        q.print(
                            "https://steamcommunity.com/id/Triton/myworkshopfiles/",
                            style="fg:ansiyellow",
                        )
                        q.print(
                            "take the name between /id/ and /myworkshopfiles, Triton in this example, and paste it here"
                        )
                        q.print(
                            "You can use CTRL-SHIFT-V or right click to paste text in a terminal"
                        )
                        author = q.text("Enter id: ").ask()

                        author_ids = ss.get_workshop_ids_from_author_id(author)
                        if author_ids == [0]:
                            q.print("---- quit out of menu ----")
                            self.start()
                        else:
                            workshop_download = cmd.dl_workshoplist_to_folder(
                                author_ids
                            )
                        if workshop_download == True:
                            self.db.update_level_table()

                            continue_to_create_playlist = q.confirm(
                                "Tracks downloaded. Create playlist from tracks?"
                            ).ask()
                            if continue_to_create_playlist:
                                formatted_workshop_id = (
                                    self.pl.format_playlistdict_from_levels(
                                        self.db.query_data_workshopid(author_ids)
                                    )
                                )
                                self.pl.create_and_copy_playlist(
                                    "", formatted_workshop_id
                                )
                                q.press_any_key_to_continue().ask()
                                self.start()
                            else:
                                self.start()
                        else:
                            q.print("---- quit out of menu ----")
                            self.start()
                    case "[steam] Workshop ID":
                        ss = SteamScraper()
                        cmd = SteamCMDManager(STEAM_WORKSHOP_FOLDER)
                        q.print(
                            "Go to a tracks workshop page in a browser and copy the workshop ID from the URL"
                        )
                        q.print("The URL should look like this: ")
                        q.print(
                            "https://steamcommunity.com/sharedfiles/filedetails/?id=1111111111"
                        )
                        workshop_id = q.text("Enter ID: ").ask()
                        workshop_dl = cmd.dl_workshoplist_to_folder([workshop_id])
                        if workshop_dl == True:
                            self.db.update_level_table()

                            continue_to_create_playlist = q.confirm(
                                "Tracks downloaded. Create playlist from tracks?"
                            ).ask()
                            if continue_to_create_playlist:
                                formatted_workshop_id = (
                                    self.pl.format_playlistdict_from_levels(
                                        self.db.query_data_workshopid(
                                            [int(workshop_id)]
                                        )
                                    )
                                )
                                self.pl.create_and_copy_playlist(
                                    "", formatted_workshop_id
                                )
                                q.press_any_key_to_continue().ask()
                                self.start()
                            else:
                                self.start()
                        else:
                            q.print("---- quit out of menu ----")
                            self.start()

            case "Playlist Manager":
                q.print(text="This functionality is a WIP. Coming in v0.4.")
                q.print(
                    text="""
                functions: 
                - combine playlists
                - filter / split playlists
                - sort playlists
                - delete playlists
                - combine filters
                - auto updating playlists
                - set playlist profiles to hide certain ones
                - collect data about which playlists certain tracks are in
                - set up genre playlists
                """
                )
                q.press_any_key_to_continue().ask()
                self.start()
            case "Database Manager":
                manager_choices = q.select(
                    message="Database Manager",
                    choices=[x[0] for x in menu_dict["Database Manager"].items()],
                    use_shortcuts=True,
                    instruction="use j/k, arrow keys or numbers to navigate",
                ).ask()
                match manager_choices:  # TODO: give some more info on which items where updated
                    case "Refresh Database":
                        self.db.update_level_table()
                        q.print("Level table updated")
                        self.db.update_zeeplist_table()
                        q.print("Playlist table updated")
                        q.press_any_key_to_continue().ask()
                        self.start()
                    case "Back":
                        self.start()
            case "Options":
                q.print("-" * 20 + "Current settings" + "-" * 20, style="fg:ansired")
                pprint(CONFIG_DATA)
                q.print("-" * 50, style="fg:ansired")
                options_choices = q.select(
                    message="Options",
                    choices=[x[0] for x in menu_dict["Options"].items()],
                    use_shortcuts=True,
                    instruction="use j/k, arrow keys or numbers to navigate",
                ).ask()

                match options_choices:
                    case "Change Playlist Defaults":
                        config = ConfigManager()
                        config.change_playlist_defaults()
                        q.print(
                            "Config Changed. Restart program now to finalize changes."
                        )
                        if q.confirm("Restart now? ").ask():
                            sys.exit(0)
                        else:
                            self.start()
                    case "Change Verbose Database Update":
                        config = ConfigManager()
                        config.change_update_verbose()
                        q.print(
                            "Config Changed. Restart program now to finalize changes."
                        )
                        if q.confirm("Restart now? ").ask():
                            sys.exit(0)
                        else:
                            self.start()
                    case "Change Steam Max Page":
                        config = ConfigManager()
                        config.change_steam_max_page()
                        q.print(
                            "Config Changed. Restart program now to finalize changes."
                        )
                        if q.confirm("Restart now? ").ask():
                            sys.exit(0)
                        else:
                            self.start()
                    case "Back":
                        self.start()
            case "About":
                q.print(menu_dict["About"]["about_text"])
                q.press_any_key_to_continue().ask()
                self.start()
            case "Exit":
                sys.exit(0)


console = Console()
console.start()
