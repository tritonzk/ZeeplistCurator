import io
import json
import os
import sqlite3 as sql
import subprocess
from ast import literal_eval
from collections import namedtuple
from datetime import datetime
from io import open
from pathlib import Path, PurePath
from pprint import pprint
from sys import exit
from urllib import parse, request

# import click  # TODO: maybe use this? Able to run the app with "app --example" tags in terminal
# import consolemenu  # this is a UI library for menus in terminal #TODO: use this for playlist browsing
import questionary as q
import regex as re
import requests
from bs4 import BeautifulSoup as bs

import menudict

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
    exit()

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
    "roundLength": 480.0,
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
    "steam_scraper": {"max_page": 99},
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
            changed = True

        if not os.path.exists(STEAM_WORKSHOP_FOLDER):
            q.print("-" * 50, style="fg:ansired")
            q.print("error: could not find your Steam's Zeepkist Workshop folder")
            q.print(
                "find where your locally downloaded tracks are stored and enter the full path for the '1440670' folder below"
            )
            self.change("custom_workshop_folder", q.text("enter path: ").ask())
            changed = True

        if changed:
            q.print("Config changed. Restarting the program now. ")
            q.press_any_key_to_continue()
            exit()

    def change(self, input: str, change_to):
        self.config[input] = change_to
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        q.print(f"changed {input} to {change_to}")

    def reset_config(self):
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG_FORMAT, f, indent=4)
        q.print("Config reset to default. Restarting the program now. ")
        q.press_any_key_to_continue()
        exit()

    def change_playlist_defaults(self):
        shuffle_choice = q.confirm("Shuffle? ").ask()
        time_choice = q.text("Roundlength ").ask()
        self.config["playlist_defaults"]["time"] = time_choice
        self.config["playlist_defaults"]["shuffle"] = shuffle_choice
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

        shuffle_choice = ["false", "true"][shuffle_choice]

        q.print(
            f"changed playlist defaults to {round( time_choice )} second rounds with shuffle = {shuffle_choice}"
        )

    def change_update_verbose(self):
        verbose = q.confirm("Show every track and playlist when updating? ").ask()
        self.change("update_verbose", verbose)
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        verbose = ["false", "true"][verbose]
        q.print(f"Changed verbose database updating to {verbose}.")

    def change_steam_max_page(self):
        max_page = q.text("Change max page to search with steam").ask()
        self.config["steam_scraper"]["max_page"] = int(max_page)
        with io.open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        q.print(f"changed steam max page to {max_page}")


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
        # TODO: work in progress

        # self.cur.execute(
        #     """
        # CREATE TABLE IF NOT EXISTS playlists (
        # id INTEGER PRIMARY KEY AUTOINCREMENT,
        # path TEXT UNIQUE,
        # name TEXT,
        # levels TEXT,
        # data TEXT,
        # """
        # )

        global first_start
        if CONFIG_DATA["update_db"] and first_start:
            self.update_level_table()
            # self.update_zeeplist_table()
            first_start = False

    def namedtuple_factory(self, cursor, row):
        """helper script to set up rows"""
        fields = [col[0] for col in cursor.description]
        Row = namedtuple("Row", fields)
        return Row(*row)

    def query_sort(self) -> list:
        """Sorting method of the sqlite queries. returns [method, direction]"""
        sort_method_options = {
            "Level name": "track_name",
            "Date modified": "date_modified",
            "Author name": "track_author",
        }
        sort_order_options = {"Ascending": "ASC", "Descending": "DESC"}

        sortbool = q.confirm(
            "Sort by default? current sorting = {0}".format(
                CONFIG_DATA["playlist_defaults"]["default_sort"]
                + " "
                + CONFIG_DATA["playlist_defaults"]["sort_direction"]
            )
        ).ask()

        if not sortbool:
            sorting_method = q.select(
                message="Sorting Method",
                choices=[
                    q.Choice(title=k, value=v) for k, v in sort_method_options.items()
                ],
            ).ask()
            sorting_order = q.select(
                message="Sorting Order?",
                choices=[
                    q.Choice(title=k, value=v) for k, v in sort_order_options.items()
                ],
            ).ask()

            return [sorting_method, sorting_order]
        else:
            return [
                CONFIG_DATA["playlist_defaults"]["default_sort"],
                CONFIG_DATA["playlist_defaults"]["sort_direction"],
            ]

    def query_data_name(self, name: str, sorting):
        """get a list of tracks with a regex name"""
        self.con.row_factory = self.namedtuple_factory
        sort = sorting
        name_tracks = self.con.execute(
            "SELECT * FROM levels WHERE LOWER(track_name) LIKE '%' || LOWER(?) || '%' ORDER BY {method} {order}".format(
                method=sort[0], order=sort[1]
            ),
            (name,),
        ).fetchall()
        return [name_tracks]

    def query_data_workshopid(self, idlist: list[int], sorting) -> list[list]:
        """get a list of ids from the database and put the data for them in a list"""
        self.con.row_factory = self.namedtuple_factory
        # sort = self.query_sort()
        sort = sorting
        if sort == "":
            sort = ["date_modified", "DESC"]
        workshop_list = []

        for id in idlist:
            workshop_list.append(
                self.con.execute(
                    """
                    SELECT * FROM levels WHERE workshop_id = ? ORDER BY {method} {order}
                """.format(
                        method=sort[0], order=sort[1]
                    ),
                    (id,),
                ).fetchall()
            )
        return workshop_list

    def query_data_author(self, author, sorting) -> list[list]:
        """get a list of tracks from an author (based on string)"""
        self.con.row_factory = self.namedtuple_factory
        sort = sorting
        author_list = self.con.execute(
            "SELECT * FROM levels WHERE LOWER(track_author) LIKE '%' || LOWER(?) || '%' ORDER BY {method} {order}".format(
                method=sort[0], order=sort[1]
            ),
            (author,),
        ).fetchall()
        return [author_list]

    def query_data_author_fuzzy(self, author, sorting) -> list[list]:
        # WARNING: work in progress
        """get a list of tracks from an author, case-insensitive, check collaboration, overwritten, author steamids.
        - check most common steam id related to author (track_author > workshop_author > collaborator)
        - once a steam id is related do another search for that steamid
        i want this one to collect all tracks the author has worked on.
        - integrate with steamcmd / steamscraper to download missing tracks from this author (get steamid first and then scrape)
        """
        self.con.row_factory = self.namedtuple_factory
        sort = sorting
        results = self.con.execute(
            """
            SELECT *
            FROM levels
            WHERE LOWER(track_author) LIKE '%' || LOWER(?) || '%'
               OR LOWER(track_collaborators) LIKE '%' || LOWER(?) || '%'
            ORDER BY {method} {order}
            """.format(
                method=sort[0], order=sort[0]
            ),
            (author,),
        ).fetchall()
        # data.pop("levels")
        return [results]

    # WARNING: not working
    # def update_zeeplist_table(self):
    #
    #     try:
    #         self.con.execute(
    #             """INSERT OR REPLACE INTO playlists ( path, name, levels, data, level_amount ) values ( ?, ?, ?, ?, ?) """,
    #             (
    #                 x.as_uri(),
    #                 plist.name,
    #                 str(plist.levels),
    #                 str(data),
    #                 plist.amount,
    #             ),
    #         )
    #     except sql.IntegrityError:
    #         print(f"sql_integrity_error on {x}")
    #         pass
    #
    #     self.con.commit()

    def update_level_table(self):
        """update level database in data.db"""
        # TODO: only update changed tracks. Better info
        tracks = list(Path(STEAM_WORKSHOP_FOLDER).rglob("*.zeeplevel"))

        for x in tracks:
            f = json.loads(
                open(x.parent.parent.as_posix() + "/metadata.json").read()
            )  # TODO: check if exist.
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
                        x.as_uri(),  # path
                        PurePath(x).parts[-3],  # workshop_id
                        "N/A",  # workshop_name #TODO: find a way to get the workshop name
                        workshop_author,  # workshop_author
                        track_data["author"]["name"],  # track_author
                        track_data["author"]["StmID"],  # track_author_stmid
                        track_data["author"]["collaborators"],  # track_collaborators
                        PurePath(x).parts[-2],  # track_name
                        str(track_data),  # track_data
                        str(datemodified),  # date_modified
                        sys_last_modified,  # sys_date_modified
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
        self.playlist_backup_folder_name = "generated_lists"
        if not Path.exists(Path(PROGRAM_PATH + "/" + self.playlist_backup_folder_name)):
            os.mkdir(
                "{cwd}/{pld}".format(
                    cwd=PROGRAM_PATH, pld=self.playlist_backup_folder_name
                )
            )

    # TODO: make this work
    def merge_playlists(self, p1, p2):
        """merge two playlists, search playlists twice, set time or choose default time, set shuffle or default"""
        pass

    def format_playlistdict_from_levels(self, datalist) -> dict:
        """put list of items from data.db queries into zeeplist format
        takes data in Row format and outputs playlist dict"""
        errors = []
        levels = []
        for _, wsitem in enumerate(datalist):  # each workshop nr has their own list
            for x in range(0, len(wsitem)):  # for each level in a workshop item
                level = ZEEPLIST_LEVEL_FORMAT.copy()
                level_row = wsitem[x]
                track_data = literal_eval(
                    level_row.track_data
                )  # WARNING: this could run code if the database is changed. find some other way to do str -> dict
                level["UID"] = track_data["level"]["UID"]
                try:
                    level["WorkshopID"] = int(level_row.workshop_id)
                except ValueError:
                    errors.append(
                        f"path: {level_row.path}. track: {level_row.track_author} - {level_row.track_name}. [[value={level_row.workshop_id}]]"
                    )
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
            ("-" * 20) + " {} tracks found ".format(pl["amountOfLevels"]) + ("-" * 20),
            style="fg:ansired",
        )
        readable_level_list = []
        for level in levels:
            readable_level_list.append(level["Author"] + " - " + level["Name"])
        print(readable_level_list)
        q.print((("-" * 40) + str(len(levels)) + " levels found" + ("-" * 30)), style="fg:ansired")
        if errors:
            q.print("Errors on these tracks:")
            print(errors)
            q.print("-" * 70, style="fg:ansired")
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

        new_list = open(
            "{pld}/{name}.zeeplist".format(
                name=name, pld=self.playlist_backup_folder_name
            ),
            "w",
            encoding="utf-8-sig",
        )
        json.dump(pldict, new_list, indent=4)
        new_list.close()

        safe = ZEEPKIST_APPDATA_FOLDER.replace(" ", r"\ ")
        subprocess.run(
            "cp {cwd}/{pld}/{name}.zeeplist {zlstorage}".format(
                cwd=PROGRAM_PATH,
                pld=self.playlist_backup_folder_name,
                name=name,
                zlstorage=safe + r"/Playlists/",
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
            "https://steamcommunity.com/profiles/{0}/myworkshopfiles/?numperpage=30"
        )

    def bsoup(self, link) -> bs:
        """return a bs4 object from given link"""
        return bs(requests.get(link).text, "html.parser")

    def get_workshop_ids_from_author_id(self, id):
        # TODO: make this work with links (isolate the id from url)
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
        """return list of all workshop ids from the given browsing page using bs4."""
        # TODO: be able choose a page limit
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
                id = (
                    re.compile(r"\d+").search(y).group()
                )  # BUG: breaks if none are found (str|None)
                idlist.append(id)
        return idlist

    def get_max_page(self, link):
        soup = self.bsoup(link)
        pages = soup.find("div", class_="workshopBrowsePagingControls")
        if pages == None:
            print("pages is None")

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
    def __init__(self, install_dir: str | None = None) -> None:
        """manager for steamcmd. downloading workshop items"""
        if install_dir == None:
            # NOTE: test this. make sure the path is correct
            self.force_install_dir = Path(
                STEAM_WORKSHOP_FOLDER
            ).parent.parent.parent.parent
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
            q.print("The workshop list given to steamcmd is empty.")
            return False
        else:
            # NOTE: filter out local tracks
            filtered_idlist = []
            removed = []
            for x in idlist:
                workshop_query = LocalDB().query_data_workshopid([x], "")
                # NOTE: if query returns nothing add to filtered
                if workshop_query == [[]]:
                    filtered_idlist.append(x)
                elif (
                    len(workshop_query[0]) > 0
                ):  # if query returns row objects [[Row(), Row()]] add to removed
                    removed.append(x)
                else:
                    q.print(f"Problem with query for workshop item {x}")

            q.print("-" * 50, style="fg:ansired")
            q.print(
                f"Found {len(idlist)} tracks, removed {len(removed)} local tracks. Leaving {len(filtered_idlist)} to download"
            )
            q.print("removed: ", style="bold")
            print(removed)
            q.print("downloading: ", style="bold")
            print(filtered_idlist)
            q.print("-" * 50, style="fg:ansired")
            q.print(f"Estimated download time of {len(filtered_idlist)*3} seconds")
            q.print(
                "Keep in mind that workshop items can have multiple tracks, this will increase the download time"
            )
            if len(filtered_idlist) != 0:
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
                q.print("Steam download completed.", style="bold")
                print(filtered_idlist)
                return True

            except subprocess.CalledProcessError as e:
                print("An error occured with subprocess: ", e)

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
                "Error with zeeptrackformat class on {track}".format(track=self.track)
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
        self.pm = PlaylistManager()
        self.cm = ConfigManager()
        self.ss = SteamScraper()
        self.cmd = SteamCMDManager()
        self.first_start = True
        self.menudict = menudict.menu_dict

        if CONFIG_DATA["first_db_update"]:
            self.db.update_level_table()
            # self.db.update_zeeplist_table()
            self.cm.change("first_db_update", False)

    def start(self):
        # TODO: set a questionary style for the menus
        if self.first_start:
            start_screen = """
            Welcome to ZeeplistCurator. Python script written by Triton (@triton_nl)
            The default location for playlists is set to: {0}
            The default location for workshop items is set to: {1}
            If this is incorrect, change this in the options menu. Or edit config.json manually.

            """.format(
                ZEEPKIST_APPDATA_FOLDER + "/Playlists", STEAM_WORKSHOP_FOLDER
            )
            q.print(start_screen)
            self.first_start = False

        firstmenu = q.select(
            message="Welcome to ZeeplistCurator",
            choices=[name for name, opc in self.menudict.items()],
            use_shortcuts=True,
            instruction="use j/k, arrow keys or numbers to navigate",
        ).ask()

        match firstmenu:
            case "Create Playlist":
                self.create_playlist_menu()
            case "Playlist Manager":
                self.playlist_manager()
            case "Database Manager":
                self.database_manager()
            case "Options":
                self.options()
            case "About":
                print(self.menudict["About"]["about_text"])
                q.press_any_key_to_continue().ask()
                self.start()
            case "Exit":
                exit()

    def create_playlist(self, formatted_tracks):
        if q.confirm("Create Playlist? ").ask():
            self.pm.create_and_copy_playlist("", formatted_tracks)
            q.press_any_key_to_continue().ask()
            self.start()
        else:
            q.print("---- quit out of menu ----")
            self.start()

    def create_playlist_menu(self):
        """create playlists."""
        playlist_choice = q.select(
            message="Create a Playlist",
            choices=[name for name, opc in self.menudict["Create Playlist"].items()],
            use_shortcuts=True,
            instruction="use j/k, arrow keys or numbers to navigate",
        ).ask()

        # NOTE: ---------------------CREATE PLAYLISTS ----------------------------
        match playlist_choice:
            # NOTE: ---------------- [local] Name -------------------------------
            case "[local] Name":
                name_query = q.text(message="Search by name: ").ask()
                formatted_name = self.pm.format_playlistdict_from_levels(
                    self.db.query_data_name(name_query, self.db.query_sort())
                )

                self.create_playlist(formatted_name)

            # NOTE: --------- [local] Author(fuzzy) -----------------------------
            case "[local] Author (fuzzy)":
                author_query = q.text(message="Search by author (fuzzy): ").ask()
                formatted_fuzzy = self.pm.format_playlistdict_from_levels(
                    self.db.query_data_author_fuzzy(author_query, self.db.query_sort())
                )

                self.create_playlist(formatted_fuzzy)

            # NOTE: -------------- [local] Author (strict) -------------------
            case "[local] Author (strict)":
                author_query = q.text(message="Search by author (strict): ").ask()
                formatted_author = self.pm.format_playlistdict_from_levels(
                    self.db.query_data_author(author_query, self.db.query_sort())
                )

                self.create_playlist(formatted_author)

            # NOTE: ---------------- [steam] Search ----------------------
            case "[steam] Search":
                steam_search_ids = self.ss.get_workshop_ids_from_browse_page(
                    self.ss.steam_link_console()
                )
                steamdl = self.cmd.dl_workshoplist_to_folder(steam_search_ids)
                if steamdl:
                    self.db.update_level_table()

                formatted_steam_search = self.pm.format_playlistdict_from_levels(
                    self.db.query_data_workshopid(
                        steam_search_ids, self.db.query_sort()
                    )
                )

                self.create_playlist(formatted_steam_search)

            # NOTE: ---------------------- [steam] Author ID -------------
            case "[steam] Author ID":
                q.print(
                    """
go to an authors workshop page on steam or in a browser. the URL should look like this:
https://steamcommunity.com/profiles/Triton/myworkshopfiles/
take the name between /profiles/ and /myworkshopfiles, Triton in this example, and paste it.
You can use CTRL-SHIFT-V or right click to paste text in a terminal"""
                )
                author_id = q.text("enter ID:").ask()
                author_workshop_ids = self.ss.get_workshop_ids_from_author_id(author_id)
                steamdl = self.cmd.dl_workshoplist_to_folder(author_workshop_ids)
                if steamdl:
                    self.db.update_level_table()

                formatted_steam_author = self.pm.format_playlistdict_from_levels(
                    self.db.query_data_workshopid(
                        author_workshop_ids, self.db.query_sort()
                    )
                )

                self.create_playlist(formatted_steam_author)

            # NOTE: -------------------- [steam] Workshop ID ---------------------------
            case "[steam] Workshop ID":
                q.print(
                    """Go to the workshop page for an item and copy the id in the link. 
The URL should look like this: https://steamcommunity.com/sharedfiles/filedetails/?id=1111111111
Paste the numbers after id= below."""
                )
                workshop_id = q.text("enter Workshop ID: ").ask()
                steamdl = self.cmd.dl_workshoplist_to_folder([int(workshop_id)])

                if steamdl:
                    self.db.update_level_table()

                formatted_steam_workshop_id = self.pm.format_playlistdict_from_levels(
                    self.db.query_data_workshopid(
                        [int(workshop_id)], self.db.query_sort()
                    )
                )

                self.create_playlist(formatted_steam_workshop_id)

    def playlist_manager(self):
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

    def database_manager(self):
        manager_choices = q.select(
            message="Database Manager",
            choices=[x[0] for x in self.menudict["Database Manager"].items()],
            use_shortcuts=True,
            instruction="use j/k, arrow keys or numbers to navigate",
        ).ask()
        match manager_choices:  # TODO: give some more info on which items where updated
            case "Refresh Database":
                self.db.update_level_table()
                q.print("Level table updated", style="bold")
                q.press_any_key_to_continue().ask()
                self.start()
            case "Back":
                self.start()

    def options(self):
        # TODO: do some testing if this all works. sometimes the playlist defaults do not work.
        q.print("-" * 20 + "Current settings" + "-" * 20, style="fg:ansired")
        pprint(CONFIG_DATA)
        q.print("-" * 50, style="fg:ansired")
        config = self.cm
        options_choices = q.select(
            message="Options",
            choices=[x[0] for x in self.menudict["Options"].items()],
            use_shortcuts=True,
            instruction="use j/k, arrow keys or numbers to navigate",
        ).ask()

        match options_choices:
            case "Change Playlist Defaults":
                config.change_playlist_defaults()
                q.print("Config Changed. Restart program now to finalize changes.")
                if q.confirm("Restart now? ").ask():
                    exit()
                else:
                    self.start()
            case "Change Verbose Database Update":
                config.change_update_verbose()
                q.print("Config Changed. Restart program now to finalize changes.")
                if q.confirm("Restart now? ").ask():
                    exit()
                else:
                    self.start()
            case "Change Steam Max Page":
                config.change_steam_max_page()
                q.print("Config Changed. Restart program now to finalize changes.")
                if q.confirm("Restart now? ").ask():
                    exit()
                else:
                    self.start()
            case "Back":
                self.start()
            case "About":
                q.print(self.menudict["About"]["about_text"])
                q.press_any_key_to_continue().ask()
                self.start()


console = Console()
console.start()
