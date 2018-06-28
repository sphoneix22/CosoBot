import asyncio
import random
import time
from configparser import ConfigParser

import discord
from discord.ext import commands

parser = ConfigParser()  # Configparser start
parser.read('secret.ini')  # Configparser read file

BOT_PREFIX = ("?", "!", ',')
TOKEN = parser.get(section='secret', option='discord_token')
EXTENSION_LIST = ['cogs.rocket', 'cogs.error_handler', 'cogs.chat', 'cogs.tournaments']

client = commands.Bot(command_prefix=BOT_PREFIX)


def main():
    for extension in EXTENSION_LIST:
        try:
            client.load_extension(extension)
            print("Loaded {}".format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))


start_time = time.time()


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


@client.command(name='uptime')
async def uptime(ctx):
    tempo = time.time() - start_time
    minute, second = divmod(tempo, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    week, day = divmod(day, 7)
    embed = discord.Embed(title='Bot attivo da:', description="{} settimane, {} giorni, "
                                                              "{} ore, "
                                                              "{} minuti, {} secondi".format(int(week), int(day),
                                                                                             int(hour), int(minute),
                                                                                             int(second)))
    embed.set_footer(text='Last time started:', icon_url='https://png.icons8.com/color/1600/raspberry-pi.png')
    await ctx.send(embed=embed)


client.loop.create_task(servers())
client.loop.create_task(game())

if __name__ == '__main__':
    main()

client.run(TOKEN)
