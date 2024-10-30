import json
import requests

workshoplink = "https://api.zworpshop.com/levels/workshop/{}?IncludeReplaced=false"
Userlink = "https://api.zworpshop.com/levels/author/{}?IncludeReplaced=false"


def create_bulk_list_from_authors():
    testlist = []
    author = ""
    jsonfile = open("ZeepCreatorlist.json", 'r')
    creators = json.load(jsonfile)

    for x in creators:
        for y in creators[x]:
            testlist.append(creators[x][y])

    print(testlist, "\n")

    for x in testlist:
        workshopitem = requests.get(workshoplink.format(x))
        jsonfile = json.loads(workshopitem.content)
    # print(jsonfile)

        user = jsonfile[0]["authorId"]
    # print("user: ",user)

        usertracks = requests.get(Userlink.format(str(user))) # get levels from author from zworpshop
        jsonUsertracks = json.loads(usertracks.content) # load json data

        
        for y in jsonUsertracks:
            print(y["fileAuthor"], y["name"], y["workshopId"], "\n")
            author = y["fileAuthor"]

        print("-----------------------{}-------------------------".format(author))
    