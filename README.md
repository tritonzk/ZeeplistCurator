# ZeepkistRandomizer

------------------------Base functionality V0.1a-------------------------------------

***Workshopscraper() -> zeeplist playlist***

- (X)   generate random WS page
- ( )   extract info from page (( ) workshop metadata, (V) workshop ID)
- (X)   download WS files using SteamCMD and WS id list
- (X)   extract info from file (_author, authorUID, filename_)      
- (X)   format and export info into zeepfile/json format
- ( )   download a specific WS ID and add to playlist
- ( )   delete WS files when done
- ( )   simple console interface
- ( )   ignore WS pages that do not have _"1 level"_ in their description

-------------------------------extra functionality V0.2-----------------------------------
- ( )   download and install SteamCMD automatically or make helper script.

**interface**
- ( )   better console interface (use simple term menu?)

**move files to correct place**
- ( )   move the playlist file to local storage
- ( )   move downloaded WS files to steam folder?

**filters**
- ( )   ignore WS pages above a certain "N level" in their description
- ( )   add a random amount from each downloaded WS item to the playlist
- ( )   add all WS items downloaded via steamCMD into playlists (option to limit amount per playlist)

**alternate ways to search**
- ( )   crawl until finding a WS item that contains more than N items --> add to a playlist
- ( )   search a specific range of pages
- ( )   search popular or other sorting methods


---------------------------------------------FUTURE-Version-?---------------------------------------
create binary to reduce dependencies
make it into a Bepinx mod? (might require rewrite into c#)

random map challenge functionality (maybe separate mod)
    - timer
    - customizable rules
    - point counter
