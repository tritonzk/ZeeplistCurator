import os
import questionary as q

from bs4 import BeautifulSoup as bs

from Console import Console
from Formatting import ZeeplistFormat as zl
from scrape_Steam import SteamScrape as steam
from genlinks import GenLinks as gen

Workdirectory = os.getcwd()

# todo
# - Change dependency on Zworpshop and GTR (Have an alternative option to use Steam search or Steam ws downloader)
# - Clean up code to use return statements instead of changing the playlist themselves


functionChoices = [
    "Random",  # 1
    "Workshop ID",  # 2
    "Steam User",  # 3
    "Search Term",  # 4
    "GTR Sorting",  # 5
    "--Exit--"
]

class WorkshopScraper:
    def __init__(self):
        self.choicesDict = {} # choices from console
        self.tracklist = {}  # list of tracks to add to playlist

    def start(self):
        self.choicesDict = Console().console()

        match self.choicesDict["functionChoice"]:
            case "Random":
                pass
            case "Workshop ID":
                pass
            case "Steam User":
                pass
            case "Search Term":
                pass
            case "GTR Sorting":
                pass
            case _:
                pass

            # case 1:
            #     self.get_zworp_random(int(self.choicesDict["amount"]))
            # case 2:
            #     self.get_zworp_workshopid(str(self.choicesDict["idchoice"]))
            # case 3:
            #     if "steamUserId" in self.choicesDict:
            #         self.info_from_user(str(self.choicesDict["steamUserId"]))
            #     elif "authorId" in self.choicesDict:
            #         self.info_from_user(str(self.choicesDict["authorId"]))
            # case 4:
            #     self.get_zworp_workshopid_list(
            #         self.get_workshopid_list_from_browse(
            #             self.get_browse_from_searchterm(
            #                 self.choicesDict["searchTerm"], self.choicesDict["sorting"]
            #             )
            #         )
            #     )
            # case 5:
            #     if int(self.choicesDict["gtr_choice"]) == 1:  # popular
            #         self.get_gtr_popular_hashes()
            #     elif int(self.choicesDict["gtr_choice"]) == 2:  # hot
            #         self.get_gtr_hot_hashes()
            #     elif int(self.choicesDict["gtr_choice"]) == 3:  # gtr points
            #         self.get_gtr_point_tracks()

        if len(self.tracklist) == 0:
            if q.confirm(
                message="Track list is empty. Try again? press n to quit."
            ).ask():
                self.start()
            else:
                quit()

        zl().zeeplist_constructor(
            UIDDict=self.tracklist,
            filename=str(self.choicesDict["name"]),
            roundlength=int(self.choicesDict["roundlength"]),
            shuffle=self.choicesDict["shuffle"],
        )

    # ----------- Helper functions ---------------------

    def sort_to_tracklist(self, item):
        # NOTE: change this to use returns from other functions. call this last
        "sort track json data to tracklist"
        for x in item:
            self.tracklist[x["fileUid"]] = [x["name"], x["fileAuthor"], x["workshopId"]]


classy = WorkshopScraper()
classy.start()
# classy.get_gtr_popular_hashes()
# classy.get_gtr_point_tracks()
