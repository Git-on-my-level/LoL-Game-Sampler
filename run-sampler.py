#!/usr/bin/python3
# Library
import configparser
import argparse
import datetime
import logging
from os.path import join
# Local
from riotapi import RiotAPI
from match import Match

def init():
    logging.basicConfig(
        filename=join('logs', str(datetime.date.today()) + '.log'),
        level=logging.DEBUG,
        format='[%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('Initializing')

    parser = argparse.ArgumentParser(description='Runner script for LoL-Game-Sampler')
    parser.add_argument('--reset_config', action='store_true', help='Reset defaults.cfg to defaults (removes your API key)')
    parser.add_argument('--config_file', default='defaults.cfg', help='Specify which config file to use')
    args = parser.parse_args()

    # the reset config file flag was given, so we reset the config file and exit
    if args.reset_config:
        logging.info('Creating default config file')
        default_config()
        logging.info('Finished creating default config file, exiting')
        exit()

    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(args.config_file)

    logging.info('Establishing API connection with:\n' +
        '\t' + str(dict(config.items('Riot API'))))
    api = RiotAPI(
        config.get('Riot API', 'API key'),
        config.get('Riot API', 'endpoint'),
        config.get('Riot API', 'region'),
        config.get('Riot API', 'version'),
        config.getint('Riot API', 'max requests per 10 secs'),
        config.getint('Riot API', 'max requests per 10 mins'))

    return args, config, api

def default_config():
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.add_section('Riot API')
    config.set('Riot API', 'API key', '<key>')
    config.set('Riot API', 'endpoint', 'https://na.api.pvp.net/api/lol/')
    config.set('Riot API', 'region', 'na')
    config.set('Riot API', 'version', 'v2.2')
    config.set('Riot API', 'max requests per 10 secs', 10)
    config.set('Riot API', 'max requests per 10 mins', 500)

    config.add_section('rankedQueues')
    config.set('rankedQueues', 'RANKED_SOLO_5x5')
    config.set('rankedQueues', 'RANKED_TEAM_5x5')

    config.add_section('seasons')
    config.set('seasons', 'SEASON2015')

    config.add_section('Other Constraints')
    config.set('Other Constraints', 'beginTime', 1441152000000)
    with open('config/defaults.cfg', 'wt') as configfile:
        config.write(configfile)

def gather_matches(seeds, api, config, batch_write = 50):
    rankedQueues = ','.join([item for item in dict(config.items('rankedQueues'))])
    seasons = ','.join([item for item in dict(config.items('seasons'))])
    beginTime = config.get('Other Constraints', 'beginTime')
    params = 'rankedQueues=' + rankedQueues + '&seasons=' + seasons + '&beginTime=' + beginTime
    # the frontier is a list of summonerIds
    frontier = seeds
    matches_explored = set()
    summoners_explored = set()
    # temporary storage for matches
    matches_to_write = []

    # stats
    valid_matches = 0
    invalid_matches = 0
    successful_matchlist_calls = 0
    failed_matchlist_calls = 0
    summoners_processed = 0
    tier_distribution = {}

    while frontier:
        new_frontier = []
        print('Frontier size: ' + str(len(frontier)))
        for summonerId in frontier:
            logging.info('Valid matches: ' + str(valid_matches) + ' | Invalid matches: ' + str(invalid_matches))
            logging.info('Distribution: ' + str(tier_distribution))
            print('API calls made in past 10 mins: ' + str(len(api.call_timestamps_10_mins)))
            print('Summoners_processed: ' + str(summoners_processed))
            print('Distribution: ' + str(tier_distribution))
            if len(matches_to_write) > batch_write:
                res = ''
                for match_to_write in matches_to_write:
                    res += match_to_write.to_json() + "\n"
                filename = join('data', config.get('Riot API', 'region'), str(datetime.date.today()) + '.data')
                write_to_file(res, filename)
                matches_to_write = []

            # batch write our matches to storage
            matchlist_obj = api.matchlist(summonerId, params)
            if matchlist_obj == None:
                failed_matlist_calls += 1
                continue
            successful_matchlist_calls += 1
            if matchlist_obj['totalGames'] == 0:
                continue

            matchlist = matchlist_obj['matches']
            matchIds_list = []

            for match in matchlist:
                if int(match['timestamp']) < int(beginTime):
                    continue
                matchIds_list.append(match['matchId'])

            for matchId in matchIds_list:
                print('Valid calls: ' + str(valid_matches) + ' | Invalid calls: ' + str(invalid_matches))
                if matchId in matches_explored:
                    continue

                match = Match(api.match(matchId))
                if not match.isValid:
                    invalid_matches += 1
                    print(match.to_json())
                    continue

                valid_matches += 1
                matches_explored.add(match.id)
                matches_to_write.append(match)
                for new_summonerId in match.summonerIds:
                    if new_summonerId in summoners_explored:
                        continue
                    new_frontier.append(new_summonerId)
                for tier in match.highestAchievedSeasonTiers:
                    if tier not in tier_distribution:
                        tier_distribution[tier] = 1
                    else:
                        tier_distribution[tier] += 1
                matches_explored.add(matchId)
            summoners_explored.add(summonerId)
            summoners_processed += 1
        frontier = new_frontier

def write_to_file(data, filename):
    f = open(filename, 'a+')
    f.write(data)
    f.close()

def main():
    args, config, api = init()
    gather_matches(['38978082'], api, config)
'''
    match_obj = api.match('1778888152')
    match = Match(match_obj)
    print(match.to_json())
    filename = join('data', config.get('Riot API', 'region'), str(datetime.date.today()) + '.data')
    write_to_file(match.to_json() + "\n", filename)
'''


main()
