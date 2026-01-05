menu_dict = {
    "Create Playlist": {
        "[local] Name": 1,
        "[local] Author (fuzzy)": 1,
        "[local] Author (strict)": 1,
        "[steam] Search": 1,
        "[steam] Author ID": 1,
        "[steam] Workshop ID": 1,
        "Back": 0,
    },
    "Playlist Manager": {
        # "Combine Playlists": 1,
        # "Filter/Split Playlists": 1,
        # "Sort Levels in Playlist": 1,
        # "Extract from Playlist": 1,  # NOTE: ?
        # "Delete playlists": 1,
        "Back": 0,
    },
    "Database Manager": {
        "Refresh Database": 1,
        "Back": 0,
    },
    "Options": {
        # "Edit config file": 1,
        "Change Playlist Defaults": 1,
        "Change Verbose Database Update": 1,
        "Change Steam Max Page": 1,
        "Back": 0,
    },
    "About": {
        "about_text": """

        This program is created by Triton (@triton_nl on discord)

Github page: https://github.com/tritonzk/ZeeplistCurator

Zeeplist Curator creates a database called 'data.db' where data from your local tracks and playlists is stored.
With some clever SQL queries you can easily create new playlists and manipulate your current ones.

If there are some specific queries you want you can suggest them to me via discord or github
and if you have some Python/sqlite3 experience or are willing to learn, I welcome any contributors.

Steam search will search the workshop and download any missing tracks. This may take a long time if the
search finds a lot of results. You can change the max amount of pages (30 items per page) to check in the Option menu.
The default is 5.

Alternatively you can subscribe to tracks with steam. Go to Database Manager. Update database. Create playlist with [local] methods.

-----------------------FUTURE UPDATE PLANS----------------------------------
I am working on a future graphics update with many more features.
The graphics update will have a visual track browser with thumbnails for local levels.

planned functions:
- magic queries (combine filters, better queries)
- tracking played tracks
- playlistmanager (open playlistmanager menu to see planned functions)
- rating tracks, adding tags and adding notes
- tracking GTR times

More info in the database will make more interesting queries possible.
- flying/offroad/etc. gate exists in level
- amount of gtr records
- amount of blocks
- has custom or certain skybox
- has no boosters
- etc.

Mixing and matching these filters will make it possible to create many different playlists.
Keep in mind that most info (especially block and level info) can only be found in locally stored levels.
First you have to download tracks and update the database.


-------------------------THANKS----------------------------------------
Thanks to Thundernerd for creating GTR and Zworpshop and so much more.
Thanks to Vei/Vulpesx for creating Zeeper which inspired me to start this project.
"""
    },
    "Exit": 0,
}
