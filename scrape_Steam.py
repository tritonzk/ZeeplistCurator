from urllib.request import urlopen
import requests
from urllib import request
import re
import subprocess
import json
import os.path

from Console import program_path
from bs4 import BeautifulSoup as bs
from genlinks import GenLinks

g = GenLinks()


class SteamScrape:
    def __init__(self) -> None:
        """get data from steam using Steam API, SteamCMD and Webscraping"""
        self.local_tracks_folder = (
            r"C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\1440670"
        )

    # NOTE: Utils

    def bsoup(self, link) -> bs:
        """return a bs4 object from given link"""
        return bs(requests.get(link).text, "html.parser")

    def get_max_workshop_page(self, wsLink: str) -> int:
        """return last page number of Steam items page"""
        soup = self.bsoup(wsLink)
        pageNumberLinks = soup.find_all("a", class_="pagelink")
        maxPage = bs.get_text(pageNumberLinks[-1])
        return int(maxPage)

    # NOTE: Steam Scraping
    def get_workshop_ids_from_browse_page(
        self,
        link,
        ) -> list[int]:
        '''return list of 30 track ids per page from the given browsing page.'''
        idlist = []
        # maxpage = self.get_max_workshop_page(link)

        soup = self.bsoup(link)
        linklist = []
        items_on_page = soup.find_all("a", class_="item_link", href=True)
        for x in items_on_page:
            linklist.append(x.get("href"))
        for y in linklist:
            idlist.append(re.compile(r"\d+").search(y).group())
        return idlist

    def get_workshop_ids_from_user_page(
        self,
        user,
        pages=1,
    ) -> list[int]:
        """Return 30 tracks per page from the given author page. 
        Enter page-number for multiple pages. enter -1 for all pages"""
        idlist = []
        maxpage = self.get_max_workshop_page(g.get_workshop_link_from_username(user))

        if pages == -1:
            pages = maxpage + 1
        elif pages > maxpage:
            print(f"there are only {maxpage} pages")
        else:
            pages += 1

        for x in range(1, pages):
            link = g.get_workshop_link_from_username(user, x)
            print(link)
            soup = self.bsoup(link)
            linklist = []
            items_on_page = soup.find_all("a", class_="ugc", href=True)
            for x in items_on_page:
                linklist.append(x.get("href"))
            for y in linklist:
                idlist.append(re.compile(r"\d+").search(y).group())
        return idlist

    def get_workshop_item_metadata(self, workshopId: str):
        """get steam workshop item metadata"""
        pass

    # NOTE: Steamcmd downloading

    def steamCMD_downloader(self, idlist: list[int]) -> None:
        """download all items from a workshop ID list"""
        os.chdir(self.local_tracks_folder)
        dlCommand = ""

        newlist = []
        idlen = len(idlist)
        move = 20
        idx = move
        running = True
        while running:
            newlist.append(idlist[idx - move : idx])
            if (idx + move) > idlen:
                break
            else:
                idx += move

        if idx > move:
            for lst in newlist:
                for y in range(0, len(lst)):
                    dlCommand += " +workshop_download_item 1440670 {workshopId}".format(
                        workshopId=idlist[y]
                    )
                subprocess.run("{}\\SteamCmd\\steamcmd +login anonymous{} +quit".format(program_path, dlCommand))

    def download_steam_item(self, workshopid):
        dlCommand = " +workshop_download_item 1440670 {}".format(workshopid)
        subprocess.run("{}\\SteamCmd\\steamcmd +login anonymous{} +quit".format(program_path, dlCommand))

        # wsMetadata = subprocess.run(
        #     r"steamctl --anonymous workshop info {}".format(workshopId)
        # )


if __name__ == "__main__":
    m = SteamScrape()
    m.local_tracks_folder
    # print(m.get_workshop_ids_from_user_page("Shadynook", 6))
    # m.get_workshop_item_metadata("3196209568")
    # m.download_steam_item(3196209568)
