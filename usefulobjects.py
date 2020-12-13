import random
import discord

color = 0x330091

def simplebed(title,text):
    embedvar = discord.Embed(title=title,description=text,color=color)
    return embedvar