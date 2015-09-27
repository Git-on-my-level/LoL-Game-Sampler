
class Match():
    team1Id = 100
    team2Id = 200

    def __init__(self, match_obj):
        self.parse_match(match_obj)

    def parse_match(self, match_obj):
        self.matchId = match_obj['matchId']
        self.region = match_obj['region']
        self.queueType = match_obj['queueType']
        self.season = match_obj['season']
        self.matchVersion = match_obj['matchVersion']
        self.team1, self.team2 = self.parse_participants(match_obj['participants'])

    def parse_participants(self, participants):
        for participant_obj in participants:
            if participant_obj['teamId'] == Match.team1Id:
                participant = {}
                participant
