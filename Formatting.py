import json
import os
import csv
from glob import glob
from pathlib import Path, PurePath
import shutil
import io
import sqlite3 as sq

from ZeeplistCurator import program_path

zeeplistFormat = {
    "name": "",
    "amountOfLevels": 0,
    "roundLength": 0,
    "shufflePlaylist": False,
    "UID": [],
    "levels": [],
}

trackFormat = {"UID": "", "WorkshopID": 0, "Name": "", "Author": "", "played": False}


class ZeeplistFormat:
    def __init__(self):
        """Class for dealing with *.zeeplevel and *.zeeplist formats"""
        self.zeepDict = {}

    def zeeplist_constructor(self, UIDDict, filename, roundlength, shuffle):
        self.zeepDict.clear()

        for x in UIDDict.items():
            self.zeepDict = zeeplistFormat
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

        # TODO: learn glob. This is so much faster and easy.
        zeeplevels = [
            y
            for x in os.walk(workshop_path)
            for y in glob(os.path.join(x[0], "*.zeeplevel"))
        ]

        # TODO: seperate lists so they don't get too large
        for x in range(len(zeeplevels)):
            workshop_item = PurePath(zeeplevels[x]).parts[-3]
            fullpath = zeeplevels[x]
            zeeplevelfile_path[workshop_item] = fullpath

        print("\n--------------------- Path finding done --------------------------\n")

        # NOTE:  extract UID and Author from zeeplevel files to uid_dict
        for x in zeeplevelfile_path.keys():
            print("keys: ", x)
            items = []
            with io.open(zeeplevelfile_path[x], "r", encoding="utf-8-sig") as csvfile:
                items = csvfile.readline().split(",")
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
    def put_uid_dict_in_db(self, UID:dict[str, dict[str, str]]):
        con = sq.connect(program_path + "\\data.db")
        cur = con.cursor()
        # cur.execute("CREATE TABLE track(UID, WorkshopID, Name, Author, played)")

        # data = [
        #     ("234235467-asldkfjoweifn-2382748", 2342243425, 'moretrack', 'Triton', False),
        # ]

        tracks = []

        for x in UID.items():
            data = x[1]
            tracks.append((data["authorid"], data["workshopid"] , data["name"] ,data["author"] , "0"))
            print(f"track: {tracks}")

        cur.executemany("INSERT OR IGNORE INTO tracks VALUES(?,?,?,?,?)", tracks)
        con.commit()

        # cur.executemany("INSERT INTO track VALUES(?,?,?,?,?)", data)
        # con.commit()

        # res = cur.execute("SELECT * FROM track")
        # print(res.fetchall())

    def get_dict_from_zeeplist(self, file: str) -> dict:
        with io.open(file, "r", encoding="utf-8-sig", newline="") as file_open:
            json_data = json.load(file_open)
        return json_data

    def move_playlist_to_local(self, file: str) -> None:
        shutil.copy(
            file,
            os.path.expandvars("%AppData%\\Zeepkist\\Playlists"),
        )


if __name__ == "__main__":
    m = ZeeplistFormat()
    # m.get_dict_from_local_tracks(path="C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670\\3058108746\\ZSL - Arashi")
    # m.get_dict_from_zeeplist("sfad.zeeplist")
    # m.zeeplist_constructor(
    #     filename="zls_pop_test",
    #     UIDDict=m.get_dict_from_local_tracks(
    #         path="steamcmd",
    #         custom="C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670\\3050923416\\ZSL - Arashi",
    #     ),
    #     roundlength=480,
    #     shuffle=False,
    # )
    m.put_uid_dict_in_db(
        m.get_dict_from_local_tracks(
            path = "custom",
            custom = "C:\\Users\\Thijmen\\Documents\\GitHub\\ZeepkistRandomizer\\SteamCmd\\steamapps\\workshop\\content\\1440670",
            

        ))
