import urllib.request
import json
from datetime import datetime
from collections import deque
from os.path import join

# A wrapper for making calls to the RiotAPI
# Throttles requests per minute to max_requests_per_min
class RiotAPI:
    call_timestamps_10_secs = deque()
    call_timestamps_10_mins = deque()
    calls_made = 0

    def __init__(self, api_key, endpoint, region, version, max_requests_per_10_secs, max_requests_per_10_mins):
        self.api_key = api_key
        self.endpoint = endpoint
        self.region = region
        self.version = version
        self.max_requests_per_10_secs = max_requests_per_10_secs
        self.max_requests_per_10_mins = max_requests_per_10_mins

    def __callAPI(self, url):
        content = None
        # if we've hit the cap, just idle until more requests become available
        while len(RiotAPI.call_timestamps_10_secs) >= self.max_requests_per_10_secs \
            or len(RiotAPI.call_timestamps_10_mins) >= self.max_requests_per_10_mins:
            if RiotAPI.call_timestamps_10_secs and (datetime.now() - RiotAPI.call_timestamps_10_secs[0]).total_seconds() > 11:
                RiotAPI.call_timestamps_10_secs.popleft()
            if RiotAPI.call_timestamps_10_mins and (datetime.now() - RiotAPI.call_timestamps_10_mins[0]).total_seconds() > 601:
                RiotAPI.call_timestamps_10_mins.popleft()
        try:
            # This must go before the request, since bad requests count towards the limit
            RiotAPI.call_timestamps_10_secs.append(datetime.now())
            RiotAPI.call_timestamps_10_mins.append(datetime.now())
            RiotAPI.calls_made += 1
            body = urllib.request.urlopen(url)
            content = json.loads(body.read().decode('utf-8'))
        except urllib.error.HTTPError:
            content = None
        return content

    def match(self, match_id, params=''):
        url = join(self.endpoint, self.region, self.version, 'match',
            str(match_id) + '?' + params + '&api_key=' + self.api_key)
        return self.__callAPI(url)

    def matchlist(self, summoner_id, params=''):
        url = join(self.endpoint, self.region, self.version, 'matchlist', 'by-summoner',
            str(summoner_id) + '?' + params + '&api_key=' + self.api_key)
        return self.__callAPI(url)
