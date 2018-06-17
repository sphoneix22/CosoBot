from discord.ext.commands import Bot
import random
import discord
import asyncio
import time

BOT_PREFIX = ("?","!",',')
TOKEN = "xxx"


client = Bot(command_prefix=BOT_PREFIX)

@client.event                                   #GAME AUTO
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


@client.event       #Scrive su console i server in cui è online
async def online():
     await client.wait_until_ready()
     while not client.is_closed:
          print("Sono online su:")
          for server in client.servers:
              print(server.name)
          print(time.strftime("%H:%M:%S"),'\n',time.strftime("%d-%m-%Y"))
          print("---------------")
          await asyncio.sleep(300)
     else:
          client.loop.close()



client.loop.create_task(playing_auto())
client.loop.create_task(online())

client.run(TOKEN)

