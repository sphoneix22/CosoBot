#!/usr/bin/python3

import sys
import asyncio
import logging
import os
import random
import shutil
import time
from configparser import ConfigParser
from os import name
import discord

from discord.ext import commands
from git import Repo

BOT_PREFIX = (";", ',')
EXTENSION_LIST = ['cogs.rocket', 'cogs.error_handler', 'cogs.chat', 'cogs.tournaments', 'cogs.google', 'cogs.music']

client = commands.Bot(command_prefix=BOT_PREFIX)


def main():
    get_secret()
    cogs_loader()
    logger()
    client.start_time = time.time()
    linux()
    if get_flags() == '--test':
        exit(0)
    branch()

def get_secret():
    """
    Load secret.ini and make it bot variable.
    """
    config = ConfigParser()
    config.read('secret.ini')
    client.secrets = dict(config.items('secret'))

def get_flags():
    """
    Checks if in test mode.
    """
    try:
        return sys.argv[1]
    except IndexError:
        client.flags = None


def cogs_loader():
    """
    Load cogs. OMG!
    """
    for extension in EXTENSION_LIST:
        try:
            client.load_extension(extension)
            print("Loaded {}".format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))


def linux():
    """
    Checks if on linux.
    """
    if name == 'nt':
        client.linux = False
    else:
        client.linux = True


def logger():
    """
    Starts logging
    """
    logger_DEBUG = logging.getLogger('discord')
    logger_DEBUG.setLevel(logging.DEBUG)
    handler_DEBUG = logging.FileHandler(filename='./data/cache/debug.log', encoding='utf-8', mode='w')
    handler_DEBUG.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger_DEBUG.addHandler(handler_DEBUG)


def branch():
    """
    Checks git branch.
    """
    repo = Repo('.')
    client.version = repo.active_branch


@client.event
async def cleaner():
    """
    Cache cleaner. When cache folder is over 200 mb.
    """
    def get_size(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    client.current_cache_size = get_size(f"{os.getcwd()}/data/cache")
    if client.current_cache_size > 209715200:
        await shutil.rmtree(f"{os.getcwd()}/data/cache/music")
        await shutil.rmtree(f"{os.getcwd()}/data/cache/images")
    await asyncio.sleep(180)


@client.event
async def servers():
    """
    Prints to console connected servers and time.
    """
    await client.wait_until_ready()
    while client.is_closed() is False:
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('----------')
        print('Sono online su:')
        for server in client.guilds:
            print(server.name)
        print(time.strftime("%H:%M:%S"), '\n', time.strftime("%d-%m-%Y"))
        print(" \n \n \n \n")
        await asyncio.sleep(300)


@client.event
async def game():
    """
    Changes presence every 1000 seconds.
    """
    await client.wait_until_ready()
    while not client.is_closed():
        playing_list = ['Ma quanto è bello sto bot?',
                        'Sono il migliore di tutti',
                        'Sono troppo pro!',
                        'Facciamo un torneo?',
                        'Emacor fa schifo',
                        'Viva Brawlhalla',
                        'Il mio padrone è il migliore',
                        'Col Raspberry']
        await client.change_presence(activity=(discord.Game(random.choice(playing_list))))
        await asyncio.sleep(1000)


client.loop.create_task(servers())
client.loop.create_task(game())
client.loop.create_task(cleaner())

if __name__ == '__main__':
    main()

client.run(client.secrets['discord_token'])
