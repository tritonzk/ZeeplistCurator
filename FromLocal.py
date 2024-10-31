import os
import os.path
import sqlite3 as s3

from pprint import pprint


class LocalTracks:
    def __init__(self) -> None:
        """class to collect data from locally downloaded tracks"""
        self.local_playlists = os.path.expandvars("%AppData%\\Zeepkist\\Playlists")
        self.local_tracks = (
            r"C:\Program Files (x86)\Steam\steamapps\workshop\content\1440670"
        )

    def get_playlist_paths(self):
        playlist_dirs = [
            self.local_playlists + "\\" + x
            for x in os.listdir(self.local_playlists)
            if os.path.isdir(self.local_playlists + "\\" + x)
        ]
        
        playlist_dirs.append(self.local_playlists)
        playlist_paths = []
        for d in playlist_dirs:
            if d == self.local_playlists:
                pass

            files = os.listdir(d)

            for f in files:
                if os.path.isfile(d + "\\" + f):
                    playlist_paths.append(d + "\\" + f)

        for p in playlist_paths:
            print(p.split("\\")[-1])

        return playlist_paths

    def get_zeeplist_data(self, playlist):
        with open(playlist) as p:
            first_line = p.readline()
        print(first_line)

    def from_author(self, author):
        """get track data from downloaded tracks of author"""
        pass


if __name__ == "__main__":
    m = LocalTracks()
    m.get_playlist_data(m.get_playlist_paths()[0])
