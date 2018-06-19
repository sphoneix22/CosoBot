from discord.ext import commands
import rls.rocket
import steam
import discord
import configparser

parser = configparser.ConfigParser()
parser.read('secret.ini')

ROCKET_LEAGUE_API_KEY = parser.get(section='secret', option='rocket_league_api_key')
ROCKET_LEAGUE_TIERS = {0: 'Unranked', 1: 'Bronze I', 2: 'Bronze II', 3: 'Bronze III', 4: 'Silver I', 5: 'Silver II',
                       6: 'Silver III',
                       7: 'Gold I', 8: 'Gold II', 9: 'Gold III', 10: 'Platinum I', 11: 'Platinum II',
                       12: 'Platinum III', 13: 'Diamond I',
                       14: 'Diamond II', 15: 'Diamond III', 16: 'Champion I', 17: 'Champion II', 18: 'Champion III',
                       19: 'Grand Champion'}
ROCKET_LEAGUE_POINTS = (
    0, 192, 256, 316, 376, 443, 492, 555, 615, 692, 772, 852, 932, 1012, 1092, 1192, 1292, 1392, 1513, 1855)


class Rocket():
    def __init__(self, client):
        self.client = client

    @commands.command(name='rl_stats',  # STATS ROCKET LEAGUE
                      description='Restituisce le statistiche di Rocket League dando il custom URL',
                      brief='Restituisce le stats di RL',
                      pass_context=True)
    async def rocket(self, context):
        custom_url = context.message.content[10:]
        id_64 = steam.steamid.steam64_from_url('https://steamcommunity.com/id/' + custom_url)
        razzo = rls.rocket.RocketLeague(ROCKET_LEAGUE_API_KEY)
        try:
            giocatore = razzo.players.player(id=id_64, platform=1).json()
            em = discord.Embed(title='Rocket League Stats', colour=discord.Colour(2041),
                               description=f"Statistiche di {giocatore['displayName']}")
            em.set_thumbnail(url="https://i.imgur.com/qqX4qjb.png")
            em.add_field(name='Vittorie', value=giocatore['stats']['wins'], inline=True)
            em.add_field(name='Goals', value=giocatore['stats']['goals'], inline=True)
            em.add_field(name='Parate', value=giocatore['stats']['saves'], inline=True)
            em.add_field(name='Assist', value=giocatore['stats']['assists'], inline=True)
            await self.client.say(f"Ecco, {context.message.author.mention}.", embed=em)
        except:
            await self.client.say(f"Giocatore non trovato, {context.message.author.mention}")

    @commands.command(name='rl_rank',
                      description="Restituisce il ranking di RL durante l'attuale stagione",
                      brief='Per vedere ranking RL',
                      pass_context=True)
    async def rocket_rank(self, context):
        custom_url = context.message.content[9:]
        id_64 = steam.steamid.steam64_from_url('https://steamcommunity.com/id/' + custom_url)
        razzo = rls.rocket.RocketLeague(ROCKET_LEAGUE_API_KEY)
        try:
            giocatore = razzo.players.player(id=id_64, platform=1).json()

            await self.client.say(f"Rank di {giocatore['displayName']}:\n"
                                  f"__**1vs1**__ : {ROCKET_LEAGUE_TIERS[giocatore['rankedSeasons']['8']['10']['tier']]}, divisione {giocatore['rankedSeasons']['8']['10']['division']} :black_large_square: "
                                  f"**{giocatore['rankedSeasons']['8']['10']['rankPoints'] - min(ROCKET_LEAGUE_POINTS,key=lambda x:abs(x-8))}** punti per salire di rank :up: \n"
                                  f"__**2vs2**__ : {ROCKET_LEAGUE_TIERS[giocatore['rankedSeasons']['8']['11']['tier']]}, divisione {giocatore['rankedSeasons']['8']['11']['division']} :black_large_square: "
                                  f" **{giocatore['rankedSeasons']['8']['11']['rankPoints'] - min(ROCKET_LEAGUE_POINTS,key=lambda x:abs(x-8))}** punti per salire di rank :up: \n"
                                  f"__**3vs3**__ : {ROCKET_LEAGUE_TIERS[giocatore['rankedSeasons']['8']['13']['tier']]}, divisione {giocatore['rankedSeasons']['8']['13']['division']} :black_large_square: "
                                  f" **{giocatore['rankedSeasons']['8']['11']['rankPoints'] - min(ROCKET_LEAGUE_POINTS,key=lambda x:abs(x-8))}** punti per salire di rank :up: \n ")
        except:
            await self.client.say(f"Giocatore non trovato, {context.message.author.mention}")


def setup(client):
    client.add_cog(Rocket(client))
