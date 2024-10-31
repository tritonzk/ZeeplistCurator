from urllib.request import urlopen
import requests
from urllib import request
import re
import subprocess
import json

from bs4 import BeautifulSoup as bs
from genlinks import GenLinks

g = GenLinks()


class SteamScrape:
    def __init__(self) -> None:
        """get data from steam using Steam API, SteamCMD and Webscraping"""
        pass

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

    def get_workshop_ids_from_steam_page(
        self,
        user,
        pagetype,
        pages=1,
    ) -> list[int]:
        """return 30 tracks per page from the given author page. enter -1 for all pages"""
        idlist = []
        maxpage = self.get_max_workshop_page(g.get_workshop_link_from_username(user))

        match pagetype:
            case "browse":
                c = "item_link"
            case "user":
                c = "ugc"
            case _:
                print("incorrect pagetype. enter 'browse' or 'user'")
                quit()

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
            items_on_page = soup.find_all("a", class_=c, href=True)
            for x in items_on_page:
                linklist.append(x.get("href"))
            for y in linklist:
                idlist.append(re.compile(r"\d+").search(y).group())
        return idlist

    def get_workshop_item_metadata(self, workshopId: str):
        """get steam workshop item metadata"""
        pass

        # wsMetadata = subprocess.run(
        #     r"steamctl --anonymous workshop info {}".format(workshopId)
        # )


if __name__ == "__main__":
    m = SteamScrape()
    # print(m.get_workshop_ids_from_user_page("Shadynook", 6))
    m.get_workshop_item_metadata("3196209568")
