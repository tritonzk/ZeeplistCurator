import json
import os
import re
import urllib.parse
import questionary as q

import requests
from bs4 import BeautifulSoup as bs

from Console import console
from Formatting import ZeeplistFormat as zl


Workdirectory = os.getcwd()

# todo
# - Change dependency on Zworpshop and GTR (Have an alternative option to use Steam search or Steam ws downloader)
# - Clean up code to use return statements instead of changing the playlist themselves


class WorkshopScraper:
    def __init__(self):
        self.choicesDict = {}  # choices from console
        self.tracklist = {}  # list of tracks to add to playlist

    def start(self):
        self.choicesDict = console()

        match int(self.choicesDict["functionChoice"][0]):
            case 0:
                print("No choice given. Try again.")
                quit()
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
            if q.confirm(message="Track list is empty. Try again? press n to quit.").ask():
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

    def sort_to_tracklist(
        self, item
    ):  # NOTE: change this to use returns from other functions. call this last
        "sort track json data to tracklist"
        for x in item:
            self.tracklist[x["fileUid"]] = [x["name"], x["fileAuthor"], x["workshopId"]]


classy = WorkshopScraper()
classy.start()
# classy.get_gtr_popular_hashes()
# classy.get_gtr_point_tracks()
