import json

'''
Structure:

match => {
    matchId
    region
    matchCreation
    queueType
    season
    matchVersion
    team1, team2 => {
        position => {
            championId
            highestAchievedSeasonTier
            spell1Id
            spell2Id
            summonerId
        }
    }
}

'''

class Match:
    team1Id = 100
    team2Id = 200

    def __init__(self, match_obj):
        self.info = {}

        self.parse_match(match_obj)

    def extract_participant_ids(self, participantIdentities_list):
        participants_by_id  = {}
        for participantIdentity in participantIdentities_list:
            participants_by_id[participantIdentity['participantId']] = participantIdentity['player']
        return participants_by_id

    def parse_match(self, match_obj):
        self.info['matchId'] = match_obj['matchId']
        self.info['region'] = match_obj['region']
        self.info['matchCreation'] = match_obj['matchCreation']
        self.info['matchDuration'] = match_obj['matchDuration']
        self.info['queueType'] = match_obj['queueType']
        self.info['season'] = match_obj['season']
        self.info['matchVersion'] = match_obj['matchVersion']
        participantIdentities = self.extract_participant_ids(match_obj['participantIdentities'])
        self.info['team1'], self.info['team2'] = self.parse_participants(match_obj['participants'], participantIdentities)

    def parse_participants(self, participants, participantIdentities):
        team1 = {}
        team2 = {}
        for participant_obj in participants:
            team = None
            if participant_obj['teamId'] == Match.team1Id:
                team = team1
            if participant_obj['teamId'] == Match.team2Id:
                team = team2
            position = participant_obj['timeline']['lane']
            if position == 'BOTTOM':
                position = participant_obj['timeline']['role']
            team[position] = {}
            participant = team[position]
            participant['championId'] = participant_obj['championId']
            participant['highestAchievedSeasonTier'] = participant_obj['highestAchievedSeasonTier']
            participant['spell1Id'] = participant_obj['spell1Id']
            participant['spell2Id'] = participant_obj['spell2Id']
            participant['summonerId'] = participantIdentities[participant_obj['participantId']]['summonerId']

        return team1, team2

    def to_json(self):
        return json.dumps(self.info)
