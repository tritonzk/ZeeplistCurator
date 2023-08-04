import json
import os

# ------- planned functionality---------------------------------------------------------

# imported by zeepkistrandomizer
# creates a playlist from a folder with ws-files


workDirectory = r'C:\Users\Thijmen\scripts'

zeeplistFormat = {"name" : "",
    "amountOfLevels" : 0,
    "roundLength" : 0,
    "shufflePlaylist" : False,
    "levels": []}

trackFormat = {"UID": "",
        "WorkshopID": 0,
        "Name": "",
        "Author": ""}


class ZeepfileFormatting():
    def __init__(self):
        self.zeepDict = {}

    def zeepfile_Constructor(self, UIDDict, filename):

        for x in UIDDict.items():
            self.zeepDict = zeeplistFormat
            trackFormat = {"UID" : str(x[1][2]), "WorkshopID" : int(x[1][0]), "Name" : "{}".format(x[0]), "Author" : "{}".format(x[1][1])}
            levelList = self.zeepDict["levels"]
            levelList.append(trackFormat)
            self.zeepDict["levels"] = levelList
            self.zeepDict["name"] = filename
            
        self.zeepDict["amountOfLevels"] = len(UIDDict)

        # y = json.dumps(self.zeepDict)
        
        os.chdir(workDirectory)
        playlistFile = open(filename + ".zeeplist", "w")
        json.dump(self.zeepDict, playlistFile, indent =  2)
        playlistFile.close()

        




# classy = ZeepfileFormatting()
# classy.zeepfile_Constructor(10, "test", "playlist_test.json")