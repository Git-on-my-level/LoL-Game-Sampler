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

    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(args.config_file)

    return args, config

def default_config():
    logging.info('Creating default config file')
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.add_section('Riot API')
    config.set('Riot API', 'API key', '<key>')
    config.set('Riot API', 'endpoint', 'https://na.api.pvp.net/api/lol/')
    config.set('Riot API', 'region', 'na')
    config.set('Riot API', 'version', 'v2.2')
    config.set('Riot API', 'max requests per min', 50)

    config.add_section('Parameters')
    config.set('Parameters', 'include ranked solo', 1)
    config.set('Parameters', 'include ranked 5s', 1)
    config.set('Parameters', 'include ranked 4s', 0)

    config.add_section('Seasons')
    config.set('Seasons', 'SEASON2015')
    with open('config/defaults.cfg', 'wt') as configfile:
        config.write(configfile)

def gather_matches(seeds):
    frontier = seeds
    explored = set()
    for node in frontier:
        new_frontier = []
        if node not in explored:
            pass

def write_to_file(json, filename):
    logging.info('Writing data to "' + filename + '"')
    f = open(filename, 'a+')
    f.write(json)
    f.close()

def main():
    args, config = init()
    if args.reset_config:
        default_config()
        return

    logging.info('Establishing API connection with:\n' +
        '\t' + str(dict(config.items('Riot API'))))
    api = RiotAPI(
        config.get('Riot API', 'API key'),
        config.get('Riot API', 'endpoint'),
        config.get('Riot API', 'region'),
        config.get('Riot API', 'version'))

    match_obj = api.match('1778888152')
    match = Match(match_obj)
    print(match.to_json())
    filename = join('data', config.get('Riot API', 'region'), str(datetime.date.today()) + '.data')
    write_to_file(match.to_json() + "\n", filename)


main()
