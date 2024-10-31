from pprint import pprint
import questionary as q

# NOTE: GTR
gtr_base = "https://api.zeepkist-gtr.com/levels/"
gtr_opt = [
    "popular",
    "hot",
    "points?SortByPoints=true&Ascending=false&Limit={}&Offset=0",
]

# NOTE: Zworpshop
zworpshopGraphHql = "https://graphql.zworpshop.com/"
zworp_base = "https://api.zworpshop.com/levels/"
zworp_opt = {
    "random": "random?Amount={}",
    "author": "author/{}?IncludeReplaced=false",
    "workshop": "workshop/{}?IncludeReplaced=false",
    "hash": "/hash/{}?IncludeReplaced=false&IncludeDeleted=false",
}

# NOTE: Steam
# WARN: order: base + browsesort + section + actualsort + page + day
search = "&searchtext={}"

browsesort = "&browsesort={s}"
searchtext = "%searchtext={}"
sort_opt = [
    "textsearch",
    "mostrecent",
    "trend",
    "playtime_trend",
    "lastupdated",
    "totaluniquesubscribers",
]

section = "&section={s}"
secton_opt = ["readytouseitems"]
actualsort = "&actualsort={s}"  # use sort_opt

page = "p={d}"
day = "days={d}"  # only for trend and playtime_trend

day_opt = [1, 7, 30, 90, 180, 365, -1]
pprint(day_opt)


# searchWsLink = baselink + "&searchtext={}&browsesort=textsearch&section=readytouseitems"
# searchWsRecent = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=mostrecent&section=&actualsort=mostrecent&p=1"
# searchWsPopular = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=trend&section=&actualsort=trend&p=1&days=-1"
#
# search = 'https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext=asdf&childpublishedfileid=0&browsesort=trend&section=readytouseitems&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0'


# search_split = search.split('&')
# pprint(search_split)


class GenLinks:
    def __init__(self) -> None:
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

    def check_connection(self ,check):
        """steam, gtr, zworpshop connection check"""
        pass

    def steam_link_console(self) -> str:
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
        if searchterm != "":
            link = (
                self.baselink
                + "&searchtext={}".format(searchterm)
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
    print(m.steam_link_console())

    # print(
    #     m.steam_link(
    #         m.sort_opt[1],
    #         page=3,
    #         days=m.daylist[3],
    #         searchterm=""
    #     )
    # )
