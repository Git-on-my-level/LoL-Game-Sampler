import urllib.request
import json
from datetime import datetime
from collections import deque
from os.path import join

# A wrapper for making calls to the RiotAPI
# Throttles requests per minute to max_requests_per_min
class RiotAPI:

    def __init__(self, api_key, endpoint, region, version, max_requests_per_10_secs, max_requests_per_10_mins):
        self.api_key = api_key
        self.endpoint = endpoint
        self.region = region
        self.version = version
        self.max_requests_per_10_secs = max_requests_per_10_secs
        self.max_requests_per_10_mins = max_requests_per_10_mins

        self.call_timestamps_10_secs = deque()
        self.call_timestamps_10_mins = deque()
        self.valid_calls = 0
        self.invalid_calls = 0

    def __callAPI(self, url):
        content = None
        # if we've hit the cap, just idle until more requests become available
        while len(self.call_timestamps_10_secs) >= self.max_requests_per_10_secs \
            or len(self.call_timestamps_10_mins) >= self.max_requests_per_10_mins:
            if self.call_timestamps_10_secs and (datetime.now() - self.call_timestamps_10_secs[0]).total_seconds() > 11:
                self.call_timestamps_10_secs.popleft()
            if self.call_timestamps_10_mins and (datetime.now() - self.call_timestamps_10_mins[0]).total_seconds() > 601:
                self.call_timestamps_10_mins.popleft()
        try:
            # This must go before the request, since bad requests count towards the limit
            self.call_timestamps_10_secs.append(datetime.now())
            self.call_timestamps_10_mins.append(datetime.now())
            body = urllib.request.urlopen(url)
            content = json.loads(body.read().decode('utf-8'))
            self.valid_calls += 1
        except urllib.error.HTTPError:
            content = None
            self.invalid_calls += 1
        return content

    def match(self, match_id, params=''):
        url = join(self.endpoint, self.region, self.version, 'match',
            str(match_id) + '?' + params + '&api_key=' + self.api_key)
        return self.__callAPI(url)

    def matchlist(self, summoner_id, params=''):
        url = join(self.endpoint, self.region, self.version, 'matchlist', 'by-summoner',
            str(summoner_id) + '?' + params + '&api_key=' + self.api_key)
        return self.__callAPI(url)
