import json
import os

workDirectory = os.getcwd()

zeeplistFormat = {"name" : "",
    "amountOfLevels" : 0,
    "roundLength" : 0,
    "shufflePlaylist" : False,
    "levels": []}

trackFormat = {"UID": "",
        "WorkshopID": 0,
        "Name": "",
        "Author": ""}

class ZeeplistFormat():
    def __init__(self):
        self.zeepDict = {}

    def zeeplist_constructor(self, UIDDict, filename, roundlength, shuffle):
        self.zeepDict.clear()

        for x in UIDDict.items():
            self.zeepDict = zeeplistFormat
            trackFormat = {"UID" : str(x[0]), 
                           "WorkshopID" : int(x[1][2]), 
                           "Name" : str(x[1][0]), 
                           "Author" : str(x[1][1])}
            levelList = self.zeepDict["levels"]
            levelList.append(trackFormat)
            self.zeepDict["levels"] = levelList
            self.zeepDict["name"] = filename

        self.zeepDict["amountOfLevels"] = len(UIDDict)
        self.zeepDict["roundLength"] = roundlength
        self.zeepDict["shufflePlaylist"] = shuffle

        os.chdir(workDirectory)
        playlistFile = open(filename + ".zeeplist", "w")
        json.dump(self.zeepDict, playlistFile, indent =  2)
        playlistFile.close()

    def get_json_from_zeeplist(self, file:str):
        file_open = open(file, 'r')

        zeeplist = json.loads(file_open)
        zeeplist.
        
        pass



