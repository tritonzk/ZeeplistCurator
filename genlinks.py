from pprint import pprint

# GTR
gtr_base = "https://api.zeepkist-gtr.com/levels/"
gtr_opt = ["popular", "hot", "points?SortByPoints=true&Ascending=false&Limit={}&Offset=0"]

# Zworpshop
zworpshopGraphHql = "https://graphql.zworpshop.com/"
zworp_base = "https://api.zworpshop.com/levels/"
zworp_opt = {"random":"random?Amount={}", 
             "author":"author/{}?IncludeReplaced=false", 
             "workshop": "workshop/{}?IncludeReplaced=false", 
             "hash" : "/hash/{}?IncludeReplaced=false&IncludeDeleted=false"}

# Steam
baselink = 'https://steamcommunity.com/workshop/browse/?appid=1440670'
search = "&searchtext={}"

browsesort= "&browsesort={s}"
sort_opt = ["textsearch", "mostrecent", "trend", "playtime_trend", "lastupdated", "totaluniquesubscribers"]

section = "&section={s}"
secton_opt = ["readytouseitems"]
actualsort = "&actualsort={s}" #use sort_opt

page = "p={d}"
day = "days={d}" # only for trend and playtime_trend
day_opt = ["1", "7", "30"]



searchWsLink = baselink + "&searchtext={}&browsesort=textsearch&section=readytouseitems"
searchWsRecent = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=mostrecent&section=&actualsort=mostrecent&p=1"
searchWsPopular = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=trend&section=&actualsort=trend&p=1&days=-1"

search = 'https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext=asdf&childpublishedfileid=0&browsesort=trend&section=readytouseitems&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0'



search_split = search.split('&')
pprint(search_split)

#NOTE: order: base + browsesort + section + actualsort + page + day


class GenLinks:
    def __init__(self) -> None:
        self.steam_app_id = 1440670
        self.steam_browse_sort = ["textsearch", "mostrecent", "trend"]

        self.steam_search = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=textsearch&section=readytouseitems"
        pass

    def check_connection(self):
        '''steam, gtr, zworpshop connection check'''
        pass

    def steam_link(sort, page, days):






