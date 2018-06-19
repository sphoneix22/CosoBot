from configparser import ConfigParser
from discord.ext import commands
import random
import discord
import asyncio
import time
import rls.rocket
import steam.steamid

parser = ConfigParser()  # Configparser start
parser.read('secret.ini')  # Configparser read file

BOT_PREFIX = ("?", "!", ',')
TOKEN = parser.get(section='secret', option='discord_token')
ROCKET_LEAGUE_API_KEY = parser.get(section='secret', option='rocket_league_api_key')
ROCKET_LEAGUE_TIERS = {0: 'Unranked', 1: 'Bronze I', 2: 'Bronze II', 3: 'Bronze III', 4: 'Silver I', 5: 'Silver II',
                       6: 'Silver III',
                       7: 'Gold I', 8: 'Gold II', 9: 'Gold III', 10: 'Platinum I', 11: 'Platinum II',
                       12: 'Platinum III', 13: 'Diamond I',
                       14: 'Diamond II', 15: 'Diamond III', 16: 'Champion I', 17: 'Champion II', 18: 'Champion III',
                       19: 'Grand Champion'}
ROCKET_LEAGUE_POINTS = (
0, 192, 256, 316, 376, 443, 492, 555, 615, 692, 772, 852, 932, 1012, 1092, 1192, 1292, 1392, 1513, 1855)

client = commands.Bot(command_prefix=BOT_PREFIX)


# EVENTS AT THE START
@client.event  # Scrive su console i server in cui è online
async def online():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Sono online su:")
        for server in client.servers:
            print(server.name)
        print(time.strftime("%H:%M:%S"), '\n', time.strftime("%d-%m-%Y"))
        print("---------------")
        await asyncio.sleep(300)


@client.event  # GAME AUTO
async def playing_auto():
    await client.wait_until_ready()
    while not client.is_closed:
        playing_list = ['Ma quanto è bello sto bot?',
                        'Sono il migliore di tutti',
                        'Sono troppo pro!',
                        'Facciamo un torneo?',
                        'Emacor fa schifo',
                        'Viva Brawlhalla',
                        'Il mio padrone è il migliore']
        await client.change_presence(game=discord.Game(name=random.choice(playing_list)))
        await asyncio.sleep(1000)


# COMMANDS
@client.command(name='rl_stats',  # STATS ROCKET LEAGUE
                description='Restituisce le statistiche di Rocket League dando il custom URL',
                brief='Restituisce le stats di RL',
                pass_context=True)
async def rocket(context):
    custom_url = context.message.content[10:]
    id_64 = steam.steamid.steam64_from_url('https://steamcommunity.com/id/' + custom_url)
    razzo = rls.rocket.RocketLeague(ROCKET_LEAGUE_API_KEY)
    try:
        giocatore = razzo.players.player(id=id_64, platform=1).json()
        em = discord.Embed(title='Rocket League Stats', colour=discord.Colour(2041),description=f"Statistiche di {giocatore['displayName']}" )
        em.set_thumbnail(url="https://i.imgur.com/qqX4qjb.png")
        em.add_field(name='Vittorie',value=giocatore['stats']['wins'],inline=True)
        em.add_field(name='Goals',value=giocatore['stats']['goals'],inline=True)
        em.add_field(name='Parate',value=giocatore['stats']['saves'],inline=True)
        em.add_field(name='Assist',value=giocatore['stats']['assists'],inline=True)
        await client.say(f"Ecco, {context.message.author.mention}.", embed=em)
    except:
        await client.say(f"Giocatore non trovato, {context.message.author.mention} \n ```rl_stats <custom_url>```")



@client.command(name='rl_rank',
                description="Restituisce il ranking di RL durante l'attuale stagione",
                brief='Per vedere ranking RL',
                pass_context=True)
async def rocket_rank(context):
    custom_url = context.message.content[9:]
    id_64 = steam.steamid.steam64_from_url('https://steamcommunity.com/id/' + custom_url)
    razzo = rls.rocket.RocketLeague(ROCKET_LEAGUE_API_KEY)
    try:
        giocatore = razzo.players.player(id=id_64, platform=1).json()
        em = discord.Embed(title='Rocket League Ranks', colour=discord.Colour(2041),
                           description=f"Statistiche di {giocatore['displayName']}")
        em.set_thumbnail(url="https://i.imgur.com/qqX4qjb.png")
        em.add_field(name='__1vs1__',value=f"{ROCKET_LEAGUE_TIERS[giocatore['rankedSeasons']['8']['10']['tier']]} divisione {giocatore['rankedSeasons']['8']['10']['division']} \n"
                                           f"**{giocatore['rankedSeasons']['8']['10']['rankPoints'] - min(ROCKET_LEAGUE_POINTS,key=lambda x:abs(x-8))}** punti per salire di rank :up:",inline=True)
        em.add_field(name='__2vs2__',value=f"{ROCKET_LEAGUE_TIERS[giocatore['rankedSeasons']['8']['11']['tier']]} divisione {giocatore['rankedSeasons']['8']['11']['division']} \n"
                                           f"**{giocatore['rankedSeasons']['8']['11']['rankPoints'] - min(ROCKET_LEAGUE_POINTS,key=lambda x:abs(x-8))}** punti per salire di rank :up:",inline=True)
        em.add_field(name='__3vs3__',value=f"{ROCKET_LEAGUE_TIERS[giocatore['rankedSeasons']['8']['13']['tier']]} divisione {giocatore['rankedSeasons']['8']['13']['division']} \n"
                                           f"**{giocatore['rankedSeasons']['8']['13']['rankPoints'] - min(ROCKET_LEAGUE_POINTS,key=lambda x:abs(x-8))}** punti per salire di rank :up:",inline=True)
        await client.say(f"Ecco, {context.message.author.mention}.", embed=em)
    except:
        await client.say(f"Giocatore non trovato, {context.message.author.mention}")


@client.command(name='teodoro',
                description='Sveglia le persone sul server',
                brief='TEODORO!',  # TEODORO WAKE UP
                pass_context=True)
@commands.cooldown(1, 120, commands.BucketType.server)
async def teo(context):
    teodoro = '<:teodoroemoji2:403218863967174667>'
    server = str(context.message.server)
    if server == 'Serverino bellino & Bananen':
        await client.say(f" {teodoro} {teodoro} {teodoro} Hey @everyone! "
                         f"Qui c'è qualcuno che vuole parlare! {teodoro} {teodoro} {teodoro}")
    else:
        await client.say("Hey @everyone! Qui c'è qualcuno che vuole parlare!")


client.loop.create_task(playing_auto())  # LOOP STARTS COMMANDS
client.loop.create_task(online())

client.run(TOKEN)
