from os import path
import questionary as q

choicesDict = {}

functionChoices = [
    "Random",  # 1
    "Workshop ID",  # 2
    "Steam User",  # 3
    "Search Term",  # 4
    "GTR Sorting",  # 5
]


def console():
    print("----------------------------------------------------------------------")
    print("Welcome to ZeepkistRandomizer. Python script written by Triton")
    appdatapath = path.expandvars("%Appdata%\\Zeepkist\\Playlists")
    print(f"place this program in your playlist folder at:\n {appdatapath}")
    print(
        "This script searches for tracks using Thundernerds 'Zworpshop API' and creates a playlist in return."
    )
    print("You can also search the workshop and get the first 30 results as a playlist\n")

    function = q.select(
        "Create Playlist",
        qmark="With: ",
        choices=functionChoices,
        use_shortcuts=True,
    ).ask()

    # for i, x in enumerate(function.choices):
    #     print(i, x)

    match function:
        case "Random":
            print("random")


    if function == "Random":
        # print("")
        n = q.text(message="How many items to download?", default="30").ask()
        choicesDict["amount"] = int(n)

    elif function == "Workshop ID":
        print(
            "for the workshop ID go to a workshop page and copy \n https://steamcommunity.com/sharedfiles/filedetails/?id=___workshop_ID___"
        )
        choicesDict["idchoice"] = q.text(message="Enter Workshop ID").ask()

    elif function == "Steam User":
        if q.confirm("Do you know the author ID?").ask():
            choicesDict["authorId"] = q.text(message="enter Author Id")
        else:
            print(
                "\ncopy a workshop Id for a track from the user you want to download from here: \nhttps://steamcommunity.com/sharedfiles/filedetails/?id=___workshop_ID___"
            )
            choicesDict["steamUserId"] = q.text(message="enter workshop Id").ask()

    elif function == "Search Term":
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

    elif function == "GTR Sorting":
        choicesDict["gtr_choice"] = q.select(
            message="Sorting Method",
            choices=["Popular", "Hot", "GTR Points"],
            use_shortcuts=True,
        ).ask()
        if choicesDict["gtr_choice"] == "GTR Points":
            n = q.text(message="how many tracks?").ask()
            choicesDict["gtr_point_track_amount"] = int(n)


    choicesDict["name"] = q.text(message="name of playlist").ask()
    choicesDict["roundlength"] = q.text(message="round length in seconds").ask()
    choicesDict["shuffle"] = q.confirm(message="shuffle?").ask()
    choicesDict["functionChoice"] = (
        [i for i, x in enumerate(functionChoices) if x == function][0],
        function,
    )

    print(choicesDict)
    return choicesDict





if __name__ == "__main__":
    console()

