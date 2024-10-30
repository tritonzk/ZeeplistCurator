import urllib.parse
from pathlib import Path
import subprocess
import requests
import random as rand
import re
import os
import json
import csv
import shutil
import urllib.parse
import zipfile

from bs4 import BeautifulSoup as bs


def info_from_user(self, user):
    """checks if user exists on zworpshop and sorts tracks to tracklist"""

    if "steamUserId" in self.choicesDict:
        userid = requests.get(self.workshoplink.format(str(user)))
        workshopfile = json.loads(userid.content)
        if "message" in workshopfile[0]:
            print("no such user")
            quit()
        user = workshopfile[0]["authorId"]

    usertracks = requests.get(self.userlink.format(str(user)))
    jsonfile = json.loads(usertracks.content)

    if "message" in jsonfile[0]:
        print("no such user")
        quit()

    for x in jsonfile:
        print(x)

    self.sort_to_tracklist(jsonfile)

# --------------- Searching -----------------------

def get_browse_from_searchterm(self, searchTerm, sorting):
    """search Steam workshop for searchTerm and choice sorting. Returns the URL of the search using bsd4"""

    if int(sorting) == 1:
        print("relevant sorting")
        searchLink = self.searchWsLink.format(urllib.parse.quote(searchTerm))
    elif int(sorting) == 2:
        print("recent sorting")
        searchLink = self.searchWsRecent.format(urllib.parse.quote(searchTerm))
    elif int(sorting) == 3:
        print("popular sorting")
        searchLink = self.searchWsPopular.format(urllib.parse.quote(searchTerm))
    else:
        searchLink = None
    return searchLink

def get_workshopid_list_from_browse(self, browsingLink):
    """takes a Steam page of track items and returns a list of Track Workshop ID's using bsd4"""

    linklist = []
    idlist = []
    if browsingLink == None:
        "issue with browsingLink"
        quit()
    soup = bs(requests.get(browsingLink).text, "html.parser")
    ItemsOnPage = soup.find_all("a", class_="item_link", href=True)

    for x in ItemsOnPage:
        linklist.append(x.get("href"))
    for y in linklist:
        idlist.append(re.compile(r"\d+").search(y).group())
    return idlist




