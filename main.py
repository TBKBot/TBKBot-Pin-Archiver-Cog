import discord
import logging
import yaml
import os
from discord.ext import commands

# Enable intents at the discord developer portal for the bot to work.
intents = discord.Intents.all()
intents.messages = True
intents.members = True
intents.presences = True

baselogger = logging.getLogger(__name__)
config = yaml.safe_load(open('config.yml'))
client = commands.Bot(command_prefix=config['prefix'], intents=intents)
basecolor = 0x330091

for i in os.listdir('/cogs'):
    if i[-3:] == '.py':
        try:
            baselogger.info(f'loading extension (cog) cogs.{i[0:-3]}')
            client.load_extension(f"cogs.{i[0:-3]}")
        except Exception as e:
            baselogger.exception(f'Exception when attempting to load extension {i[0:-3]}')

client.run(config["token"])