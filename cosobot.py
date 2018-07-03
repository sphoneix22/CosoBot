#!/usr/local/bin/python3.6

import asyncio
import logging
import os
import random
import time
from configparser import ConfigParser
import os
import discord
from discord.ext import commands

parser = ConfigParser()
parser.read('{}/secret.ini'.format(os.getcwd()))

BOT_PREFIX = (";", ',')
TOKEN = parser.get(section='secret', option='discord_token')
EXTENSION_LIST = ['cogs.rocket', 'cogs.error_handler', 'cogs.chat', 'cogs.tournaments', 'test_music']

client = commands.Bot(command_prefix=BOT_PREFIX)


def main():
    for extension in EXTENSION_LIST:
        try:
            client.load_extension(extension)
            print("Loaded {}".format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    logger()
    client.start_time = time.time()
    cleaner()


def logger():
    logger_DEBUG = logging.getLogger('discord')
    logger_DEBUG.setLevel(logging.DEBUG)
    handler_DEBUG = logging.FileHandler(filename='./data/cache/debug.log', encoding='utf-8', mode='w')
    handler_DEBUG.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger_DEBUG.addHandler(handler_DEBUG)


def cleaner():
    file_list = [f for f in os.listdir("./data/cache/music")]
    for f in file_list:
        os.remove("./data/cache/music/{}".format(f))


@client.event
async def servers():
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

if __name__ == '__main__':
    main()

client.run(TOKEN)
