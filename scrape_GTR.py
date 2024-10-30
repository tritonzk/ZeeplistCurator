
    # ------------ Get GTR info -------------------------

    def get_gtr_popular_hashes(self):
        """get track json data and sort to tracklist based on gtr 'popular' sorting """
        hashes = []
        popular_hashes = requests.get(self.gtr_popular)
        jsonfile = json.loads(popular_hashes.content)
        for x in jsonfile["levels"]:
            print(x)
            self.get_zworp_hash(x["level"]) # sorts to tracklist

    def get_gtr_hot_hashes(self):
        """get track json data and sort to tracklist based on gtr 'hot' sorting """
        hot_tracks = []
        hot = requests.get(self.gtr_hot)
        jsonfile = json.loads(hot.content)
        for x in jsonfile["levels"]:
            print(x)
            self.get_zworp_hash(x["level"]) # sorts to tracklist

    def get_gtr_point_tracks(self):
        '''get track json data and sort to tracklist based on gtr points amount (top points)'''
        point_tracks = []
        try:
            point_tracks_with_limit = self.gtr_points.format(
                self.choicesDict["gtr_point_track_amount"]
            )
        except:
            point_tracks_with_limit = self.gtr_points.format(100)
            print("you did not enter a track amount. Try again")
        point = requests.get(point_tracks_with_limit)
        jsonfile = json.loads(point.content)
        for x in jsonfile["items"]:
            print(x)
            self.get_zworp_hash(x["level"]) # sorts to tracklist
