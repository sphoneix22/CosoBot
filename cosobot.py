#!/usr/bin/python3

import sys
import asyncio
import logging
import os
import random
import shutil
import time
import datetime
import asyncpg
from configparser import ConfigParser
from os import name
import discord
import json

from discord.ext import commands

BOT_PREFIX = (";", ',')
EXTENSION_LIST = ['cogs.error_handler', 'cogs.chat', 'cogs.tournaments', 'cogs.google', 'cogs.music', 'cogs.casino']

client = commands.Bot(command_prefix=BOT_PREFIX)


def main():
    cogs_loader()
    logger()
    client.start_time = time.time()
    linux()
    if get_flags() == '--test':
        exit(0)
    get_secret()

    client.loop.create_task(servers())
    client.loop.create_task(game())
    client.loop.create_task(cleaner())
    client.loop.create_task(dj_loop())

    for to_be_disabled_command in client.disabled_commands:
        command = client.get_command(to_be_disabled_command)
        command.enabled = False


def get_secret():
    """
    Load secret.ini and make it bot variable.
    """
    config = ConfigParser()
    config.read('secret.ini')
    client.parser = config
    client.secrets = dict(config.items('secret'))
    client.config = dict(config.items('config'))
    client.disabled_commands = json.loads(config.get("commands", "disabled"))
    client.db = dict(config.items('db'))


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


@client.event  # NON SI CAPISCE NULLA MA FUNZIONA
async def dj_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        conn = await asyncpg.connect(
            f"postgres://{client.db['user']}:{client.db['password']}@{client.db['host']}:5432/cosobot")

        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type = 'BASE TABLE'")

        if len(tables) == 0:
            await conn.close()
            await asyncio.sleep(120)
        else:
            for table in tables:
                dj_ends = await conn.fetch(
                    f"SELECT user_id, dj_end FROM {table['table_name']} WHERE dj_end IS NOT NULL")
                if not len(dj_ends) == 0:
                    now = datetime.datetime.now(tz=datetime.timezone.utc)
                    server = client.get_guild(int(table['table_name'].split('_')[1]))
                    role = discord.utils.get(server.roles, name="CosoBot DJ")
                    for rec in dj_ends:
                        if now > rec['dj_end']:
                            user_dsc = server.get_member(int(rec['user_id']))
                            await user_dsc.remove_roles(role)
                            await conn.execute(
                                f"UPDATE {table['table_name']} SET dj_end = null WHERE user_id = '{rec['user_id']}'")

            await conn.close()
            await asyncio.sleep(120)


if __name__ == '__main__':
    main()

try:
    client.run(client.secrets['discord_token'])
except Exception:
    client.run("hey we arrrre testing! Arr!")
