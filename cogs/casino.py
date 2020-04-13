import asyncpg
import datetime
from numpy.random import choice
from discord import Embed, Colour
from discord.ext import commands
from discord import utils
from asyncio import sleep
from random import randint
from decimal import getcontext, Decimal

getcontext().prec = 3  # setting precision for decimal values


class Casino(commands.Cog):
    def __init__(self, client):
        self.client = client

    # todo make a check to see if casino exists

    @commands.command(name='casino', aliases=['casinò'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def casino_(self, ctx):
        server_id = ctx.guild.id
        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        await conn.execute(
            f"CREATE TABLE IF NOT EXISTS s_{server_id} (user_id text PRIMARY KEY, money float, last_request timestamptz,"
            f" wins integer, losses integer, dj_end timestamptz)"
            # table name: s_ID
        )

        rows = await conn.fetch(
            f"SELECT * FROM s_{server_id} ORDER BY money DESC"
        )

        embed = Embed(title=f'Casinò | {ctx.guild.name}',
                      description='Se non sei nella lista, scrivi ``,casino_add`` e inizia a giocare!',
                      color=Colour(0xB5110D))

        if len(rows) != 0:
            for entry in rows:
                total_plays = entry['wins'] + entry['losses']
                try:
                    winrate = f"{Decimal(entry['wins'] / total_plays) * 100}%"
                except ZeroDivisionError:
                    winrate = 'N/D'
                embed.add_field(name=f"**{self.client.get_user(int(entry['user_id']))}**",
                                value=f"**{entry['money']}€** Winrate {winrate}",
                                inline=True)
        else:
            embed.add_field(name='**Che noia!**', value='Il casinò è vuoto!')

        await conn.close()

        return await ctx.send(embed=embed)

    @commands.command(name='casino_add', aliases=['casinò_add'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def casino_add_(self, ctx):
        server_id = ctx.guild.id

        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        check_table = await conn.fetchrow(
            f"SELECT to_regclass('cosobot.public.s_{server_id}')"
        )

        if check_table[0] is None:
            return await ctx.send("Il casinò non è attivato su questo server! Scrivi ``,casino``")

        check_user = await conn.fetchrow(
            f"SELECT * FROM s_{server_id} WHERE public.s_{server_id}.user_id = '{ctx.author.id}'"
        )

        if check_user is not None:
            return await ctx.send("Sei già registrato!")

        await conn.execute(
            f"INSERT INTO s_{server_id} VALUES ('{ctx.author.id}',50, '{datetime.datetime.now(tz=datetime.timezone.utc)}',0,0, null)"
        )

        await conn.close()

        return await ctx.send(f"{ctx.author.mention} adesso sei nel casinò, inizia a giocare!")

    @commands.command(name='soldi')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def soldi_(self, ctx):
        server_id = ctx.guild.id

        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        check_table = await conn.fetchrow(
            f"SELECT to_regclass('cosobot.public.s_{server_id}')"
        )

        if check_table[0] is None:
            return await ctx.send("Il casinò non è attivato su questo server! Scrivi ``,casino``")

        user = await conn.fetchrow(
            f"SELECT * FROM s_{server_id} WHERE public.s_{server_id}.user_id = '{ctx.author.id}'"
        )

        if user is None:
            return await ctx.send("Non sei registrato! Scrivi ``,casino_add``")

        diff = datetime.datetime.now(tz=datetime.timezone.utc) - user['last_request']
        if diff >= datetime.timedelta(days=1):
            await conn.execute(
                f"UPDATE s_{server_id} SET money = {user['money'] + 10}, last_request = '{datetime.datetime.now(tz=datetime.timezone.utc)}' WHERE user_id = '{ctx.author.id}'"
            )

            await ctx.send("Aggiunti 10€ sul tuo conto. Torna domani per altri soldi!")
        else:
            s_left = 86400-diff.seconds
            await ctx.send(f"Non è ancora passato un giorno dalla tua ultima richiesta! Mancano {int(s_left/3600)} ore.")

        return await conn.close()

    @commands.command(name='roulette')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def roulette_(self, ctx):
        server_id = ctx.guild.id

        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        check_table = await conn.fetchrow(
            f"SELECT to_regclass('cosobot.public.s_{server_id}')"
        )

        if check_table[0] is None:
            return await ctx.send("Il casinò non è attivato su questo server! Scrivi ``,casino``")

        user = await conn.fetchrow(
            f"SELECT * FROM s_{server_id} WHERE public.s_{server_id}.user_id = '{ctx.author.id}'"
        )

        if user is None:
            return await ctx.send("Non sei registrato! Scrivi ``,casino_add``")

        embed = Embed(title=f'Roulette | {ctx.author.name}',
                      description=f"Quanto vuoi puntare? Hai a disposizione **{user['money']}€**\nLa roulette è americana,"
                                  f" con 0 e 00.\nManda un messaggio con il solo importo. Esempio ``21.25`` (max 2 cifre decimali)",
                      color=Colour(0xB5110D))
        sent_embed = await ctx.send(embed=embed)

        def check(m):
            sep = m.content.split('.')
            try:
                return sep[0].isdigit() and sep[1].isdigit() and len(sep[1]) <= 2 and m.author == ctx.author
            except IndexError:
                return sep[0].isdigit() and m.author == ctx.author

        bet = await self.client.wait_for('message', check=check, timeout=60)
        bet_amount = float(bet.content)

        if bet_amount > user['money'] or user['money'] == 0:
            await bet.delete()
            await sent_embed.delete()
            return await ctx.send("Non hai abbastanza soldi!")

        await bet.delete()

        embed.description = f"Ok, punti **{bet_amount}€**.\nAdesso aggiungi una reazione per:\n1- Punta sui colori\n2-Punta sui numeri"
        await sent_embed.edit(embed=embed)
        reactions = {"\U00000031\U000020e3": 1, "\U00000032\U000020e3": 2}
        for rec in reactions.keys():
            await sent_embed.add_reaction(rec)

        def check(reaction, user):
            return str(
                reaction) in reactions.keys() and user == ctx.message.author and reaction.message.id == sent_embed.id

        betting_choose, user_msg = await self.client.wait_for('reaction_add', check=check, timeout=60)
        await sent_embed.delete()

        if reactions[str(betting_choose)] == 1:
            embed = Embed(title=f'Roulette | {ctx.author.name}',
                          description=f"Ok, punti **{bet_amount}€** sui **colori**. Su che colore punti? Aggiungi una reazione.",
                          color=Colour(0xB5110D))
            sent_embed = await ctx.send(embed=embed)
            reactions = {"\U0001f534": "rosso", "\U000026ab": "nero"}
            for rec in reactions.keys():
                await sent_embed.add_reaction(rec)

            def check(reaction, user):
                return str(
                    reaction) in reactions.keys() and user == ctx.message.author and reaction.message.id == sent_embed.id

            color_choose, user_msg = await self.client.wait_for('reaction_add', check=check, timeout=60)

            embed.description = f"Ok, punti **{bet_amount}€** sul **{reactions[str(color_choose)]}**.\nBuona fortuna!\nGirando..."
            embed.set_thumbnail(url="https://media.giphy.com/media/l2SpToqr9rGbGIHHa/giphy.gif")
            await sent_embed.edit(embed=embed)

            result = choice([0, 1, 2, 3], p=[18 / 38, 18 / 38, 1 / 38, 1 / 38])  # black=0, red=1, zero=2, double zero=3

            if result == 3:
                embed.description = f"E' uscito il doppio zero, vince il banco. Adesso hai a disposizione **{user['money'] - bet_amount}€**"
                embed.set_thumbnail(url="https://media.giphy.com/media/YJjvTqoRFgZaM/giphy.gif")
                await sleep(3)

                await conn.execute(
                    f"UPDATE s_{server_id} SET money = {user['money'] - bet_amount}, losses = {user['losses'] + 1} WHERE user_id = '{ctx.author.id}'"
                )
                await sent_embed.edit(embed=embed)
            elif result == 2:
                embed.description = f"E' uscito lo zero, vince il banco. Adesso hai a disposizione **{user['money'] - bet_amount}€**"
                embed.set_thumbnail(url="https://media.giphy.com/media/YJjvTqoRFgZaM/giphy.gif")
                await sleep(3)

                await conn.execute(
                    f"UPDATE s_{server_id} SET money = {user['money'] - bet_amount}, losses = {user['losses'] + 1} WHERE user_id = '{ctx.author.id}'"
                )
                await sent_embed.edit(embed=embed)
            elif result == 1:
                if reactions[str(color_choose)] == 'rosso':
                    embed.description = f"E' uscito rosso, hai vinto! Adesso hai a disposizione **{user['money'] + bet_amount}€**"
                    embed.set_thumbnail(url="https://media.giphy.com/media/ADgfsbHcS62Jy/giphy.gif")
                    await sleep(3)

                    await conn.execute(
                        f"UPDATE s_{server_id} SET money = {user['money'] + bet_amount}, wins = {user['wins'] + 1} WHERE user_id = '{ctx.author.id}'"
                    )
                    await sent_embed.edit(embed=embed)
                else:
                    embed.description = f"E' uscito rosso, hai perso. Adesso hai a disposizione **{user['money'] - bet_amount}€**"
                    embed.set_thumbnail(url="https://media.giphy.com/media/YJjvTqoRFgZaM/giphy.gif")
                    await sleep(3)

                    await conn.execute(
                        f"UPDATE s_{server_id} SET money = {user['money'] - bet_amount}, losses = {user['losses'] + 1} WHERE user_id = '{ctx.author.id}'"
                    )
                    await sent_embed.edit(embed=embed)
            else:
                if reactions[str(color_choose)] == 'nero':
                    embed.description = f"E' uscito nero, hai vinto! Adesso hai a disposizione **{user['money'] + bet_amount}€**"
                    embed.set_thumbnail(url="https://media.giphy.com/media/ADgfsbHcS62Jy/giphy.gif")
                    await sleep(3)

                    await conn.execute(
                        f"UPDATE s_{server_id} SET money = {user['money'] + bet_amount}, wins = {user['wins'] + 1} WHERE user_id = '{ctx.author.id}'"
                    )
                    await sent_embed.edit(embed=embed)
                else:
                    embed.description = f"E' uscito nero, hai perso. Adesso hai a disposizione **{user['money'] - bet_amount}€**"
                    embed.set_thumbnail(url="https://media.giphy.com/media/YJjvTqoRFgZaM/giphy.gif")
                    await sleep(3)

                    await conn.execute(
                        f"UPDATE s_{server_id} SET money = {user['money'] - bet_amount}, losses = {user['losses'] + 1} WHERE user_id = '{ctx.author.id}'"
                    )
                    await sent_embed.edit(embed=embed)
        else:
            embed = Embed(title=f'Roulette | {ctx.author.name}',
                          description=f"Ok, punti **{bet_amount}€** sui **numeri**. Su che numero punti?\nScrivi un numero da 1 a 36, 0 oppure 00",
                          color=Colour(0xB5110D))
            sent_embed = await ctx.send(embed=embed)

            def check(m):
                return (int(m.content) in range(0, 37) or m.content == '00') and m.author == ctx.message.author

            choose_number = await self.client.wait_for('message', check=check, timeout=60)
            await choose_number.delete()
            embed.description = f"Ok, punti **{bet_amount}€** sul numero {choose_number.content}. Buona fortuna!\nGirando..."
            embed.set_thumbnail(url="https://media.giphy.com/media/l2SpToqr9rGbGIHHa/giphy.gif")

            await sent_embed.edit(embed=embed)

            numbers = ['00']
            for i in range(0, 37):
                numbers.append(str(i))

            result = choice(numbers)
            await sleep(3)

            if result == choose_number.content:
                new_money = user['money'] + bet_amount * 35
                embed.description = f"Congratulazioni! E' uscito **{result}**. Ora hai a disposizione **{new_money}€**"
                embed.set_thumbnail(url="https://media.giphy.com/media/ADgfsbHcS62Jy/giphy.gif")

                await conn.execute(
                    f"UPDATE s_{server_id} SET money = {new_money}, wins = {user['wins'] + 1} WHERE user_id = '{ctx.author.id}'"
                )

                await sent_embed.edit(embed=embed)
            else:
                new_money = user['money'] - bet_amount
                embed.description = f"E' uscito **{result}**, hai perso. Ora hai a disposizione **{new_money}€**"
                embed.set_thumbnail(url="https://media.giphy.com/media/YJjvTqoRFgZaM/giphy.gif")

                await conn.execute(
                    f"UPDATE s_{server_id} SET money = {new_money}, losses = {user['losses'] + 1} WHERE user_id = '{ctx.author.id}'"
                )

                await sent_embed.edit(embed=embed)
        return await conn.close()

    @commands.command(name='shop')
    async def shop_(self, ctx):
        server_id = ctx.guild.id

        conn = await asyncpg.connect(
            f"postgres://{self.client.db['user']}:{self.client.db['password']}@{self.client.db['host']}:5432/cosobot")

        check_table = await conn.fetchrow(
            f"SELECT to_regclass('cosobot.public.s_{server_id}')"
        )

        if check_table[0] is None:
            return await ctx.send("Il casinò non è attivato su questo server! Scrivi ``,casino``")

        user = await conn.fetchrow(
            f"SELECT * FROM s_{server_id} WHERE public.s_{server_id}.user_id = '{ctx.author.id}'"
        )

        if user is None:
            return await ctx.send("Non sei registrato! Scrivi ``,casino_add``")

        embed = Embed(title=f"Shop | {ctx.author.name}'",
                      description=f"Spendi, paga, sborsa.\nHai a disposizione {user['money']}€")
        embed.add_field(name='1 - DJ per un giorno', value='200€', inline=True)
        sent_embed = await ctx.send(embed=embed)

        reactions = {"\U00000031\U000020e3": 1}
        for rec in reactions.keys():
            await sent_embed.add_reaction(rec)

        def check(reaction, user):
            return str(
                reaction) in reactions.keys() and user == ctx.message.author and reaction.message.id == sent_embed.id

        choose, user_msg = await self.client.wait_for('reaction_add', check=check, timeout=60)

        if reactions[str(choose)] == 1:
            if user['money'] >= 200:
                role = utils.get(ctx.guild.roles, name='CosoBot DJ')
                if role is None:
                    await ctx.send("Non esiste il ruolo DJ su questo server, chiama il mio padrone.")
                else:
                    await ctx.guild.get_member(int(user['user_id'])).add_roles(role)
                    await conn.execute(
                        f"UPDATE s_{server_id} SET dj_end = '{datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)}',"
                        f" money = {user['money'] - 200}"
                    )
                    await ctx.send(f"Goditi questa giornata di DJ! Il tuo nuovo saldo è {user['money'] - 200}€")
            else:
                await ctx.send("Non hai abbastanza soldi!")

            return await conn.close()


def setup(client):
    client.add_cog(Casino(client))
