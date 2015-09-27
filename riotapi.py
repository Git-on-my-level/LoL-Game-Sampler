import urllib.request
import json
from os.path import join

class RiotAPI:

    def __init__(self, api_key, endpoint, region, version):
        self.api_key = api_key
        self.endpoint = endpoint
        self.region = region
        self.version = version

    def match(self, match_id, params=''):
        url = join(self.endpoint, self.region, self.version, 'match',
            match_id + '?' + params + '&api_key=' + self.api_key)
        return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))

    def matchlist(self, summoner_id, params=''):
        url = join(self.endpoing, self.region, self.version, 'matchlist', 'by-summoner',
            summoner_id + '?' + params + '&api_key=' + self.api_key)
        return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
