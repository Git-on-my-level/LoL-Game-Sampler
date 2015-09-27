import urllib.request
import json
from os.path import join

class RiotAPI:
    call_timestamps = []

    def __init__(self, api_key, endpoint, region, version, max_requests_per_min):
        self.api_key = api_key
        self.endpoint = endpoint
        self.region = region
        self.version = version
        self.max_requests_per_min = max_requests_per_min

    def __callAPI(self, url):
        content = None
        while len(RiotAPI.call_timestamps) >= self.max_requests_per_min:
            
        try:
            body = urllib.request.urlopen(url)
            content = json.loads(body.read().decode('utf-8'))

        except urllib.error.HTTPError:
            content = None
        return content

    def match(self, match_id, params=''):
        url = join(self.endpoint, self.region, self.version, 'match',
            match_id + '?' + params + '&api_key=' + self.api_key)
        return self.__callAPI(url)

    def matchlist(self, summoner_id, params=''):
        url = join(self.endpoing, self.region, self.version, 'matchlist', 'by-summoner',
            summoner_id + '?' + params + '&api_key=' + self.api_key)
        return self.__callAPI(url)
