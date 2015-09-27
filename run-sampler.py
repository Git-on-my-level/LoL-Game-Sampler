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
        config.get('Riot API', 'version'))

    return args, config, api

def default_config():
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.add_section('Riot API')
    config.set('Riot API', 'API key', '<key>')
    config.set('Riot API', 'endpoint', 'https://na.api.pvp.net/api/lol/')
    config.set('Riot API', 'region', 'na')
    config.set('Riot API', 'version', 'v2.2')
    config.set('Riot API', 'max requests per min', 50)

    config.add_section('rankedQueues')
    config.set('rankedQueues', 'RANKED_SOLO_5x5')
    config.set('rankedQueues', 'RANKED_TEAM_5x5')

    config.add_section('seasons')
    config.set('seasons', 'SEASON2015')
    with open('config/defaults.cfg', 'wt') as configfile:
        config.write(configfile)


def gather_matches(seeds, api, config):
    rankedQueues = [item for item in dict(config.items('rankedQueues'))]
    seasons = [item for item in dict(config.items('seasons'))]
    print(seasons)
    params = 'rankedQueues=' ','.join(rankedQueues) + '&seasons=' + ','.join(seasons)
    print(params)
    # the frontier is a list of summonerIds
    frontier = seeds
    explored = set()
    for summonerId in frontier:
        new_frontier = []
        if summonerId in explored:
            next
        api.matchlist(summonerId, params)
        

def write_to_file(json, filename):
    logging.info('Writing data to "' + filename + '"')
    f = open(filename, 'a+')
    f.write(json)
    f.close()

def main():
    args, config, api = init()


    match_obj = api.match('1778888152')
    match = Match(match_obj)
    print(match.to_json())
    filename = join('data', config.get('Riot API', 'region'), str(datetime.date.today()) + '.data')
    write_to_file(match.to_json() + "\n", filename)


main()
