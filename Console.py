import os
from os import path
import questionary as q
from pprint import pprint

choicesDict = {
    "amount":0,
    "functionChoice":"",
    "workshopid":"",
    "authorId":"",
    "pages":0,
    "steamUserId":"",
    "searchTerm":"",
    "roundlength":0.0,
    "shuffle":False,
}


program_path = os.getcwd()

class Console():
    def __init__(self) -> None:
        pass

    def console(self):
        # print("----------------------------------------------------------------------")
        # print("Welcome to ZeeplistCurator. Python script written by Triton")
        # appdatapath = path.expandvars("%Appdata%\\Zeepkist\\Playlists")
        # print(f"Place this program in your playlist folder at:\n {appdatapath}")
        # print("\nThis script creates playlists and downloads Zeepkist tracks using: ")
        # print("- Thundernerds 'Zworpshop' and 'GTR' API") #NOTE: on hold
        # print("- Steam API, SteamCMD") #NOTE: download done
        # print("- Steam Webscraping using BeautifulSoup4") #NOTE: done
        # print("- Searching through local playlist and track files") #NOTE: done
        # print("\n")


        appdatapath = path.expandvars("%Appdata%\\Zeepkist\\Playlists")

        start_screen = """
        Welcome to ZeeplistCurator. Python script written by Triton
        Type 'ZeeplistCurator -h' to learn how to use this as a CLI application.

        Place this program in your playlist folder at:
        {0}
        """.format(appdatapath)
        print(start_screen)

        # firstmenu = q.select(message="")




        # print("\nstatus of services:")

        playlist_menu = [
            "Local Tracks",
            "Workshop User",
            "Steam Search",
        ]

        start = q.select(message="Create Playlist From:", choices=playlist_menu).ask()

        match start:
            case "Workshop User":
                print("Go to the Steam Workshop. Click on a user workshop profile and enter the ID in the url.")
                print("it should look like this:\n https://steamcommunity.com/id/___STEAM_ID___/myworkshopfiles/?appid=1440670")
                choicesDict["steamUserId"].text(message="Enter ID").ask()
                choicesDict["pages"]
            case "Steam Search":
                choicesDict["sorting"] = q.select(
                    message="Search with what sorting method?",
                    choices=[
                        "Relevant",
                        "Recent",
                        "Popular (All Time)",
                    ],
                    use_shortcuts=True,
                ).ask()
                choicesDict["searchTerm"] = q.text(message="Enter search term").ask()


        # functionChoices = [
        #     "Random",  # 1
        #     "Workshop ID",  # 2
        #     "Steam User",  # 3
        #     "Search Term",  # 4
        #     "GTR Sorting",  # 5
        #     "--Exit--"
        # ]

        # function = q.select(
        #     "Create Playlist",
        #     choices=functionChoices,
        #     use_shortcuts=True,
        # ).ask()

        # if function == "Random":
        #     # print("")
        #     n = q.text(message="How many items to download?", default="30").ask()
        #     choicesDict["amount"] = int(n)
        #
        # elif function == "Workshop ID":
        #     print(
        #         "for the workshop ID go to a workshop page and copy \n https://steamcommunity.com/sharedfiles/filedetails/?id=___workshop_ID___"
        #     )
        #     choicesDict["wsidchoice"] = q.text(message="Enter Workshop ID").ask()
        #
        # elif function == "Steam User":
        #     if q.confirm("Do you know the author ID?").ask():
        #         choicesDict["authorId"] = q.text(message="enter Author Id")
        #     else:
        #         print(
        #             "\ncopy a workshop Id for a track from the user you want to download from here: \nhttps://steamcommunity.com/sharedfiles/filedetails/?id=___workshop_ID___"
        #         )
        #         choicesDict["steamUserId"] = q.text(message="enter workshop Id").ask()
        #
        # elif function == "Search Term":
        #
        # elif function == "GTR Sorting":
        #     print("unfortunately the GTR API is down currently so this functionality is broken. \nI will release a new version once it is up again.")
        #     # choicesDict["gtr_choice"] = q.select(
        #     #     message="Sorting Method",
        #     #     choices=["Popular", "Hot", "GTR Points"],
        #     #     use_shortcuts=True,
        #     # ).ask()
        #     # if choicesDict["gtr_choice"] == "GTR Points":
        #     #     n = q.text(message="how many tracks?").ask()
        #     #     choicesDict["gtr_point_track_amount"] = int(n)
        #
        # elif function == "--Exit--":
        #     print("quiting program")
        #     quit()
        #
        #
        # choicesDict["name"] = q.text(message="name of playlist").ask()
        # choicesDict["roundlength"] = q.text(message="round length in seconds").ask()
        # choicesDict["shuffle"] = q.confirm(message="shuffle?").ask()
        # choicesDict["functionChoice"] = (
        #     [i for i, x in enumerate(functionChoices) if x == function][0],
        #     function,
        # )
        #
        # pprint("choices: {}".format(choicesDict))
        return choicesDict


if __name__ == "__main__":
    Console().console()

