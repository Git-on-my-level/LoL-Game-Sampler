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
    parser.add_argument('--config_file', default=join('config', 'defaults.cfg'), help='Specify which config file to use')
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

    config.add_section('Seed summoner IDs')
    config.set('Seed summoner IDs', 38978082)
    config.set('Seed summoner IDs', 19839634)
    config.set('Seed summoner IDs', 37073409)
    config.set('Seed summoner IDs', 25856104)
    config.set('Seed summoner IDs', 37497048)
    config.set('Seed summoner IDs', 20132258) # Doublelift
    config.set('Seed summoner IDs', 21397689)
    config.set('Seed summoner IDs', 59411974)

    with open('config/defaults.cfg', 'wt') as configfile:
        config.write(configfile)

def gather_matches(seeds, api, config, max_matches_per_summoner = 5, batch_write = 50):
    rankedQueues = ','.join([kv[0] for kv in config.items('rankedQueues')])
    seasons = ','.join([kv[0] for kv in config.items('seasons')])
    beginTime = config.get('Other Constraints', 'beginTime')
    params = 'rankedQueues=' + rankedQueues + '&seasons=' + seasons + '&beginTime=' + beginTime
    # the frontier is a list of summonerIds
    frontier = seeds
    matches_explored = set()
    summoners_explored = set()
    # temporary storage for matches
    matches_to_write = []

    # stats
    summoners_processed = 0
    degrees_of_separation = 0
    tier_distribution = {}
    summoner_collisions = 0
    summoner_uniques = 1
    match_collisions = 0
    match_uniques = 1

    while frontier:
        new_frontier = []
        # logging for each degree of separation
        print('Frontier size: ' + str(len(frontier)))
        logging.info('Frontier size: ' + str(len(frontier)))
        logging.info('Degrees of separation: ' + str(degrees_of_separation))
        logging.info('Valid calls: ' + str(api.valid_calls) + ' | Invalid calls: ' + str(api.invalid_calls))
        logging.info('Distribution: ' + str(tier_distribution))
        logging.info('Summoner collision rate on this frontier: ' + str(summoner_collisions/(summoner_collisions+summoner_uniques)))
        logging.info('Match collision rate on this frontier: ' + str(match_collisions/(match_collisions+match_uniques)))
        summoner_collisions = 0
        summoner_uniques = 0
        match_collisions = 0
        match_uniques = 0
        for summonerId in frontier:
            print('API calls made in past 10 mins: ' + str(len(api.call_timestamps_10_mins)))
            print('Summoners_processed: ' + str(summoners_processed))
            print('Distribution: ' + str(tier_distribution))
            print('Valid calls: ' + str(api.valid_calls) + ' | Invalid calls: ' + str(api.invalid_calls))
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
                continue
            if matchlist_obj['totalGames'] == 0:
                continue

            matchlist = matchlist_obj['matches']
            matchIds_list = []

            matches_for_summoner = 0
            for match in matchlist:
                if matches_for_summoner >= max_matches_per_summoner:
                    break
                if int(match['timestamp']) < int(beginTime):
                    continue
                matchIds_list.append(match['matchId'])
                matches_for_summoner += 1

            for matchId in matchIds_list:
                if matchId in matches_explored:
                    match_collisions += 1
                    continue
                match_uniques += 1

                match = Match(api.match(matchId))
                if not match.isValid:
                    continue

                matches_explored.add(match.id)
                matches_to_write.append(match)
                for new_summonerId in match.summonerIds:
                    if new_summonerId in summoners_explored:
                        summoner_collisions += 1
                        continue
                    summoner_uniques += 1
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
        degrees_of_separation += 1

def write_to_file(data, filename):
    f = open(filename, 'a+')
    f.write(data)
    f.close()

def main():
    args, config, api = init()
    seeds = [kv[0] for kv in config.items('Seed summoner IDs')]
    gather_matches(seeds, api, config)

main()
