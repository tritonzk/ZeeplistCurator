gtr_popular = "https://api.zeepkist-gtr.com/levels/popular"
gtr_hot = "https://api.zeepkist-gtr.com/levels/hot"
gtr_points = "https://api.zeepkist-gtr.com/levels/points?SortByPoints=true&Ascending=false&Limit={}&Offset=0"

# Zworpshop
zworpshopGraphHql = "https://graphql.zworpshop.com/"
randomlink = "https://api.zworpshop.com/levels/random?Amount={}"
userlink = "https://api.zworpshop.com/levels/author/{}?IncludeReplaced=false"
workshoplink = "https://api.zworpshop.com/levels/workshop/{}?IncludeReplaced=false"

zworp_hash = "https://api.zworpshop.com/levels/hash/{}?IncludeReplaced=false&IncludeDeleted=false"

searchWsLink = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=textsearch&section=readytouseitems"
searchWsRecent = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=mostrecent&section=&actualsort=mostrecent&p=1"
searchWsPopular = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=trend&section=&actualsort=trend&p=1&days=-1"

search = 'https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext=asdf&childpublishedfileid=0&browsesort=trend&section=readytouseitems&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0'

search_split = search.split('&')
pprint(search_split)

#NOTE: order: base + browsesort + section + actualsort + page + day

baselink = 'https://steamcommunity.com/workshop/browse/?appid=1440670'
search = "&searchtext={}"

browsesort= "&browsesort={s}"
browsesort_opt = ["textsearch", "mostrecent", "trend", "playtime_trend", "lastupdated", "totaluniquesubscribers"]

section = "&section={s}"
secton_opt = ["readytouseitems"]

actualsort = "actualsort={s}"
actualsort_opt = ["textsearch", "mostrecent", "trend", "playtime_trend", "lastupdated", "totaluniquesubscribers"]

page = "p={d}"
day = "days={d}" # only for trend and 


class GenLinks:
    def __init__(self) -> None:
        self.steam_app_id = 1440670
        self.steam_browse_sort = ["textsearch", "mostrecent", "trend"]

        self.steam_search = "https://steamcommunity.com/workshop/browse/?appid=1440670&searchtext={}&browsesort=textsearch&section=readytouseitems"
        pass

    def check_connection(self):
        '''steam, gtr, zworpshop connection check'''
        pass



