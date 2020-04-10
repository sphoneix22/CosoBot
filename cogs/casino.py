import asyncpg
from discord import Embed, Colour
from discord.ext import commands

class Casino(commands.Cog):
    def __init__(self, client):
        self.client = client

    #todo make a check to see if casino exists

    @commands.command(name='casino', aliases=['casinò'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def casino_(self, ctx):
        server_id = ctx.guild.id
        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        await conn.execute(
            f"CREATE TABLE IF NOT EXISTS s_{server_id} (user_id text PRIMARY KEY, money float)"  #table name: s_ID
        )

        rows = await conn.fetch(
            f"SELECT * FROM s_{server_id} ORDER BY money DESC"
        )

        embed = Embed(title=f'Casinò | {ctx.guild.name}',
                      description='Se non sei nella lista, scrivi ``,casino_add`` e inizia a giocare!',
                      color=Colour(0xB5110D))

        if len(rows) != 0:
            for entry in rows:
                embed.add_field(name=f"**{self.client.get_user(int(entry['user_id']))}**", value=f"{entry['money']}€",
                                inline=True)
        else:
            embed.add_field(name='**Che noia!**', value='Il casinò è vuoto!')

        return await ctx.send(embed=embed)

    @commands.command(name='casino_add', aliases=['casinò_add'])
    @commands.cooldown(1,20, commands.BucketType.user)
    async def casino_add_(self, ctx):
        server_id = ctx.guild.id

        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        check_table = await conn.fetchrow(
            f"SELECT to_regclass('cosobot.public.s_{server_id}')"
        )

        if len(check_table) == 0:
            return await ctx.send("Il casinò non è attivato su questo server! Scrivi ``,casino``")

        check_user = await conn.fetchrow(
            f"SELECT * FROM s_{server_id} WHERE user_id = {ctx.author.id}"
        )

        if len(check_user) == 0:
            return await ctx.send("Sei già registrato!")

        await conn.execute(
            f"INSERT INTO s_{server_id} VALUES ({ctx.author.id},0)"
        )

        return await ctx.send(f"{ctx.author.mention} adesso sei nel casinò, inizia a giocare!")


def setup(client):
    client.add_cog(Casino(client))

