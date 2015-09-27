#!/usr/bin/python3
# Library
import configparser
import argparse
# Local
from riotapi import RiotAPI

def init():
    parser = argparse.ArgumentParser(description='Runner script for LoL-Game-Sampler')
    parser.add_argument('--reset_config', action='store_true', help='Reset defaults.cfg to defaults (removes your API key)')
    parser.add_argument('--config_file', default='defaults.cfg', help='Specify which config file to use')
    args = parser.parse_args()

    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(args.config_file)

    return args, config

def default_config():
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.add_section('Riot API')
    config.set('Riot API', 'API key', '<key>')
    config.set('Riot API', 'endpoint', 'https://na.api.pvp.net/api/lol/')
    config.set('Riot API', 'region', 'na')
    config.set('Riot API', 'version', 'v2.2')

    config.add_section('Parameters')
    config.set('Parameters', 'include ranked solo', 1)
    config.set('Parameters', 'include ranked 5s', 1)
    config.set('Parameters', 'include ranked 4s', 0)

    config.add_section('Seasons')
    config.set('Seasons', 'SEASON2015')
    with open('defaults.cfg', 'wt') as configfile:
        config.write(configfile)

def main():
    args, config = init()
    if args.reset_config:
        default_config()
        return

    api = RiotAPI(
        config.get('Riot API', 'API key'),
        config.get('Riot API', 'endpoint'),
        config.get('Riot API', 'region'),
        config.get('Riot API', 'version'))
    print(api.match('1778888152'))


main()
