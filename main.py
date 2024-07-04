import discord
import os   
import asyncio
import sqlite3
from discord.ext  import commands

discord_token = os.getenv("DiscordToken")

#Toggle intents
intents = discord.Intents.all()
intents.members = True

#Setup bot and select prefix
Client = commands.Bot(command_prefix = '!', intents = intents)

#when bot is ready
@Client.event
async def on_ready():
    synced = await Client.tree.sync()
    print("Slash CMDs synced: " + str(len(synced)) + " Command(s)")
    print('Bot is ready for use!')

#Refreshes DB automaticly
def init_db():
    conn = sqlite3.connect('RiotIDs.db')

    conn.commit()
    conn.close()

init_db()   

#Read Cogs from other folder
async def load(): 
     path = 'FeederBoard/cogs'

     for filename in os.listdir(path):
          if filename.endswith('.py'):
            #print(f'cogs.{filename[:-3]}')
            await Client.load_extension(f'cogs.{filename[:-3]}')           

#Run main and cogs
async def main():
    await load()
    await Client.start(discord_token)

if __name__ == "__main__":
    asyncio.run(main()) 