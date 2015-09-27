import urllib.request
import json
from os.path import join

class RiotAPI:

    def __init__(self, api_key, endpoint, region, version):
        self.api_key = api_key
        self.endpoint = endpoint
        self.region = region
        self.version = version

    def match(self, match_id):
        opt_params = '?' # [TODO] implement
        url = join(self.endpoint, self.region, self.version, 'match', match_id, opt_params + 'api_key=' + self.api_key)
        return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
