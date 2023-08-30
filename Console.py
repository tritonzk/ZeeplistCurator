class Console():
    def __init__(self) -> None:
        self.choicesDict = {}

    def console(self):
            print("----------------------------------------------------------------------------------------------------")
            print("Welcome to ZeepkistRandomizer. Python script written by Triton")
            print(r"place this program in your playlist folder at: %Appdata%\Zeepkist\Playlists")
            print("This script searches the Steam workshop using Thundernerds 'Zworpshop API' for random or specific tracks and gives you a Zeepkist playlist in return.")
            print("You can also search the workshop and get the first 30 results as a playlist\n")
            
            print("1: Download randomly")
            print("2: Download specific workshop ID")
            print("3: create playlist from steamuser")
            print("4: download 30 from searchterm")
            functionChoice = input("Enter a choice (1,2,3,4): ---> ")

            if functionChoice == "1":
                print("")
                self.choicesDict["amount"] = input("How many workshop items to download?: ---> ")
        
            elif functionChoice == "2":
                print("")
                print("for the workshop ID go to a workshop page and copy \n https://steamcommunity.com/sharedfiles/filedetails/?id=___workshop_ID___")
                self.choicesDict["idchoice"] = input("Enter workshop ID: ---> ")

            elif functionChoice == "3":
                print("")
                print("do you want to search using:")
                print("1: AuthorId (id in the zeepfile)")
                print("2: extract Authorid from a workshop item")
                self.choicesDict["userFromWorkshop"] = input("Enter a choice (1,2): ---> ")
                if int(self.choicesDict["userFromWorkshop"]) == 1:
                    self.choicesDict["authorId"] = input("enter AuthorId: ---> ")
                elif int(self.choicesDict["userFromWorkshop"]) == 2:
                    print("\ncopy a workshop Id for a track from the user you want to download from here: \nhttps://steamcommunity.com/sharedfiles/filedetails/?id=___workshop_ID___")
                    self.choicesDict["steamUserId"] = input("\nenter workshopId: ---> ")

            elif functionChoice == "4":
                print("")
                print("Search with what sorting method?")
                print("1: Relevant")
                print("2: Recent") 
                print("3: Popular (all Time)")
                self.choicesDict["sorting"] = input("Enter a choice (1,2,3): --->")
                self.choicesDict["searchTerm"] = input("enter search term: ---> ")
            
            playlistName = input("name of playlist?: ---> ")
            roundLength = input("length of round in seconds: ---> ")
            shuffleChoice = input("shuffle? (y/n): ---> ")
            if shuffleChoice == ("y" or "Y"):
                shuffleChoice = True
            elif shuffleChoice == ("n" or "N"):
                shuffleChoice = False
            

            self.choicesDict["name"] = playlistName
            self.choicesDict["roundlength"] = roundLength
            self.choicesDict["functionChoice"] = functionChoice
            self.choicesDict["shuffle"] = shuffleChoice
            
            print("\nchoices: ", self.choicesDict)
            return self.choicesDict