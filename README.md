
# ZeepkistRandomizer
In an effort to create a game-mode for Zeepkist similar to RMC (random map challenge) from Trackmania and to make creating playlists less cumbersome, I created this Python script. The script searches the steam workshop using BeautifulSoup4 and downloads workshop items using SteamCMD. For a full list of planned functionality look at the bottom of this page. Not everything functions on Linux for now. I might make a Linux compatible version if there is a want for it.

## How to install/use
*this script is created using Python3.11. It should function with any Python3 release*
Download either through console: `git clone https://github.com/tritonzk/ZeepkistRandomizer` or simply clone through the browser. 

Download SteamCMD here https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip and place `steamcmd.exe` in the SteamCMD folder.

Install BeautifulSoup4 through pip 
`pip install beautifulsoup4`

Then open the ZeepkistRandomizer folder in your console and run
`python3 ZeepkistRandomizer.py`  **or**  `python ZeepkistRandomizer.py`

## Planned functionality
items with (X) are finished and (~) are partially finished.

### V.0.1

- (X)   generate random WS page
- (~)   extract info from page ((  ) workshop metadata, (V) workshop ID)
- (X)   download WS files using SteamCMD and WS id list
- (X)   extract info from file (_author, authorUID, filename_)      
- (X)   format and export info into zeepfile/json format
- ( )   download a specific WS ID and add to playlist
- ( )   delete WS files when done
- ( )   simple console interface
- ( )   ignore WS pages that do not have _"1 level"_ in their description

### V.0.2

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


## Possible future version?
- create standalone *.exe with interface
- make a separate Bepinx RMC mod
    - timer
    - customizable rules
    - point counter
