    def get_zworp_hash(self, hash):
        """get track json data from zworpshop based on hash and sort to tracklist"""
        print("----", hash)
        hash_code = requests.get(self.zworp_hash.format(hash))
        if hash_code.status_code == 404:
            print("error 404")
            print("*****", hash_code)
            pass
        else:
            jsonfile = json.loads(hash_code.content)
            self.sort_to_tracklist(jsonfile)

    def get_zworp_random(self, amount):
        '''get random track json data from zworpshop and sort to tracklist'''
        randomtracks = requests.get(self.randomlink.format(str(amount)))
        jsonfile = json.loads(randomtracks.content)
        self.sort_to_tracklist(jsonfile)

    def get_zworp_workshopid(self, id):
        '''get zworpshop json data from workshop id and sort to tracklist'''
        workshopitem = requests.get(self.workshoplink.format(id))
        jsonfile = json.loads(workshopitem.content)
        self.sort_to_tracklist(jsonfile)

    def get_zworp_workshopid_list(self, list):
        '''loop over list of workshop ids, get zworpshop json data and sort to tracklist'''
        for x in list:
            print("ID = ", x)
            self.get_zworp_workshopid(x)
