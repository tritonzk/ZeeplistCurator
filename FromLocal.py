import os
import os.path

class LocalTracks:
    def __init__(self) -> None:
        """class to collect data from locally downloaded tracks"""
        local_data = os.path.expandvars("~%AppData%\\Zeepkist")
        local_tracks = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\1440670"

    def from_author(self, author):
        """get track data from downloaded tracks of author"""
        pass

if __name__ == "__main__":
    m = LocalTracks()



