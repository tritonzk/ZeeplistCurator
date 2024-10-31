from pprint import pprint
import questionary as q
from urllib import request, parse

# NOTE: GTR
gtr_base: str = "https://api.zeepkist-gtr.com/levels/"
gtr_opt: list = [
    "popular",
    "hot",
    "points?SortByPoints=true&Ascending=false&Limit={}&Offset=0",
]

# NOTE: Zworpshop
zworpshopGraphHql: str = "https://graphql.zworpshop.com/"
zworp_base: str = "https://api.zworpshop.com/levels/"
zworp_opt: dict = {
    "random": "random?Amount={}",
    "author": "author/{}?IncludeReplaced=false",
    "workshop": "workshop/{}?IncludeReplaced=false",
    "hash": "/hash/{}?IncludeReplaced=false&IncludeDeleted=false",
}

# NOTE: Steam
# WARN: order: base + browsesort + section + actualsort + page + day


class GenLinks:
    def __init__(self) -> None:
        '''Class to generate steam, gtr and zworpshop links for Web scraping and API calls'''
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
        self.daylist = [1, 7, 30, 90, 180, 365, -1]

    def check_connection(self) -> None:
        """steam, gtr, zworpshop connection check"""
        connect = {
            "gtr": ("https://api.zeepkist-gtr.com", None),
            "zworpshop": ("https://api.zworpshop.com/levels/", None),
            "steam": (self.baselink, None),
        }

        for x in connect:
            try:
                request.urlopen(x)
                print("connected to: ", x)
            except:
                print("no connection: ", x)

    def get_workshop_link_from_username(self, user:str, page=1) -> str:
        '''return published tracks list from steam username '''
        return "https://steamcommunity.com/id/{0}/myworkshopfiles/?appid=1440670&p={1}&numperpage=30".format(user, page)


    def steam_link_console(self) -> str:
        '''questionary console to generate a steam workshop link'''
        sortchoice = q.select(
            message="select sorting method",
            choices=[
                "Popular",
                "Playtime",
                "Total Subscribers",
                "Recent",
                "Last Update",
            ],
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
        page = int(q.text("What page?").ask())

        return self.steam_link(
            sort=sortchoice, page=page, days=days, searchterm=searchterm
        )

    def steam_link(self, sort: str, page: int, days: int, searchterm: str) -> str:
        '''return a steam workshop link for the given arguments. Use steam_link_console to generate using
        questionary console'''
        if searchterm != "":
            link = (
                self.baselink
                + "&searchtext={}".format(parse.quote(searchterm))
                + self.browsesort.format(sort)
                + "&p={}".format(days)
            )
        else:
            link = self.baselink + self.browsesort.format(sort) + "&p={}".format(page)

        if sort == ("playtime_trend" or "trend"):
            link = link + "&days={}".format(days)

        return link


if __name__ == "__main__":
    m = GenLinks()
    print(m.check_connection())

    # print(
    #     m.steam_link(
    #         m.sort_opt[1],
    #         page=3,
    #         days=m.daylist[3],
    #         searchterm=""
    #     )
    # )
